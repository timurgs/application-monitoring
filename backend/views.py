import pytz

from django.contrib.auth import authenticate
from django.contrib.postgres.aggregates import StringAgg
from django.db.models import Q, Max, CharField
from django.db.models.functions import Cast
from django.http import JsonResponse, Http404
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet
from datetime import datetime, timedelta

from backend.models import Request, Refinement, Address, Defect, ImplementingOrganization, WorkPerformedType
from backend.serializers import RequestSerializer, AddressSerializer, DefectSerializer


class LoginView(APIView):

    def post(self, request, *args, **kwargs):
        if {'username', 'password'}.issubset(request.data):
            user = authenticate(request, username=request.data['username'], password=request.data['password'])
            if user is not None:
                token, _ = Token.objects.get_or_create(user=user)
                return JsonResponse({'Status': True, 'Token': token.key})
            else:
                return JsonResponse({'Status': False, 'Errors': 'Не удалось авторизировать'})
        else:
            return JsonResponse({'Status': False, 'Errors': 'Не указаны все необходимые аргументы'})


class RequestsViewSet(ModelViewSet):
    """
    Класс для работы с заявками
    """
    queryset = Request.objects\
        .prefetch_related('defect__work_performed_types', 'defect__work_performed_types__security_events') \
        .select_related('address__ods',
                        'implementing_organization',
                        'defect',
                        'user__organization',
                        'user__implementing_organization',
                        'closing_result',
                        'closing_result__marm_executor',
                        'closing_result__marm_implementing_organization',
                        'closing_result__review',
                        'closing_result__refinement')
    serializer_class = RequestSerializer
    permission_classes = [IsAuthenticated]

    def list(self, request, *args, **kwargs):
        serializer = self.get_serializer(self.get_queryset(), many=True)
        return Response(serializer.data)

    def retrieve(self, request, pk=None, *args, **kwargs):
        try:
            request_obj = Request.objects.get(root_id=pk)
        except Request.DoesNotExist:
            raise Http404
        serializer = self.get_serializer(request_obj)
        if request_obj.closing_result.being_under_revision_sign == 'Да':
            current_datetime = datetime.now(pytz.timezone('Europe/Moscow'))
            date = current_datetime - request_obj.created_at
            data = {'total_term': date}
            data.update(serializer.data)
            return Response(data)
        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        # Генерация корневого ИД заявки
        max_values = Request.objects.aggregate(Max('root_id'), Max('version_id'))
        if max_values['root_id__max'] > max_values['version_id__max']:
            max_val = max_values['root_id__max']
        else:
            max_val = max_values['version_id__max']
        request.data.update({'root_id': max_val + 1})

        # Генерация номера заявки
        values = Request.objects.aggregate(string_agg=StringAgg(Cast('number', CharField()), delimiter=', '))
        numbers = values['string_agg'].split(", ")
        max_number = max(list(map(lambda x: int(x.split("/")[0]), numbers)))
        current_datetime = datetime.now(pytz.timezone('Europe/Moscow')).year
        request.data.update({'number': str(max_number) + str(current_datetime)[-2:]})

        # Инцидент
        defect_name = request.data.get('defect').get('name')
        repeated_location = request.data.get('defect').get('repeated_location')

        current_datetime = datetime.now(pytz.timezone('Europe/Moscow'))
        requests = Request.objects.filter(defect__name=defect_name,
                                          defect__repeated_location=repeated_location)
        for r in requests:
            if r.created_at + timedelta(r.defect.another_term) < current_datetime:
                r.incident_sign = 'Да'
                request.data.update({'incident_sign': 'Нет',
                                     'parent_application_root_id': r.root_id,
                                     'parent_application_number': r.number})

        # Присвоение статуса
        request.data.update({'status_name': 'Новая', 'status_code': 'new'})

        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_404_NOT_FOUND)

    def update(self, request, pk=None, *args, **kwargs):
        try:
            request_obj = Request.objects.get(root_id=pk)
        except Request.DoesNotExist:
            raise Http404
        if request_obj.status_name in {'Новая', 'Ожидает обработки', 'В работе'} or \
                request_obj.defect.urgency_category_name != 'Аварийная':

            # Генерация ИД версии заявки
            max_values = Request.objects.aggregate(Max('root_id'), Max('version_id'))
            if max_values['root_id__max'] > max_values['version_id__max']:
                max_val = max_values['root_id__max']
            else:
                max_val = max_values['version_id__max']
            request.data.update({'version_id': max_val + 1})

            # Отправка пользователя и роли
            request_obj.user = request.user.id
            request_obj.save()
            serializer = self.get_serializer(request_obj)
            return Response(serializer.data)
        else:
            raise Http404


class ActiveRequestsViewSet(ModelViewSet):
    """
    Класс для получения активных заявок
    """
    queryset = Request.objects.filter(Q(status_name="Новая") |
                                      Q(status_name="Ожидает обработки") |
                                      Q(status_name="В работе")) \
        .prefetch_related('defect__work_performed_types', 'defect__work_performed_types__security_events') \
        .select_related('address__ods',
                        'implementing_organization',
                        'defect',
                        'user__organization',
                        'user__implementing_organization',
                        'closing_result',
                        'closing_result__marm_executor',
                        'closing_result__marm_implementing_organization',
                        'closing_result__review',
                        'closing_result__refinement')
    serializer_class = RequestSerializer
    permission_classes = [IsAuthenticated]


class NewRequestsViewSet(ModelViewSet):
    """
    Класс для получения заявок со стастусом "Новая"
    """
    queryset = Request.objects.filter(status_name="Новая")\
        .prefetch_related('defect__work_performed_types', 'defect__work_performed_types__security_events')\
        .select_related('address__ods',
                        'implementing_organization',
                        'defect',
                        'user__organization',
                        'user__implementing_organization',
                        'closing_result',
                        'closing_result__marm_executor',
                        'closing_result__marm_implementing_organization',
                        'closing_result__review',
                        'closing_result__refinement')
    serializer_class = RequestSerializer
    permission_classes = [IsAuthenticated]


class PendingProcessingRequestsViewSet(ModelViewSet):
    """
    Класс для получения заявок со статусом "Ожидает обработки"
    """
    queryset = Request.objects.filter(status_name="Ожидает обработки")\
        .prefetch_related('defect__work_performed_types', 'defect__work_performed_types__security_events')\
        .select_related('address__ods',
                        'implementing_organization',
                        'defect',
                        'user__organization',
                        'user__implementing_organization',
                        'closing_result',
                        'closing_result__marm_executor',
                        'closing_result__marm_implementing_organization',
                        'closing_result__review',
                        'closing_result__refinement')
    serializer_class = RequestSerializer
    permission_classes = [IsAuthenticated]


class InProgressRequestsViewSet(ModelViewSet):
    """
    Класс для получения заявок со статусом "В работе"
    """
    queryset = Request.objects.filter(status_name="В работе")\
        .prefetch_related('defect__work_performed_types', 'defect__work_performed_types__security_events')\
        .select_related('address__ods',
                        'implementing_organization',
                        'defect',
                        'user__organization',
                        'user__implementing_organization',
                        'closing_result',
                        'closing_result__marm_executor',
                        'closing_result__marm_implementing_organization',
                        'closing_result__review',
                        'closing_result__refinement')
    serializer_class = RequestSerializer
    permission_classes = [IsAuthenticated]


class ClosedRequestsViewSet(ModelViewSet):
    """
    Класс для получения заявок со статусом "Закрыта"
    """
    queryset = Request.objects.filter(status_name="Закрыта")\
        .prefetch_related('defect__work_performed_types', 'defect__work_performed_types__security_events')\
        .select_related('address__ods',
                        'implementing_organization',
                        'defect',
                        'user__organization',
                        'user__implementing_organization',
                        'closing_result',
                        'closing_result__marm_executor',
                        'closing_result__marm_implementing_organization',
                        'closing_result__review',
                        'closing_result__refinement')
    serializer_class = RequestSerializer
    permission_classes = [IsAuthenticated]


class RequestsRefinementViewSet(ModelViewSet):
    """
    Класс для возвращения заявок на доработку
    """
    serializer_class = RequestSerializer
    permission_classes = [IsAuthenticated]

    def update(self, request, pk=None, *args, **kwargs):
        try:
            request_obj = Request.objects.get(root_id=pk)
        except Request.DoesNotExist:
            raise Http404
        current_datetime = datetime.now(pytz.timezone('Europe/Moscow'))
        if request_obj.created_at == request_obj.updated_at:
            difference = current_datetime - request_obj.created_at
        else:
            difference = current_datetime - request_obj.updated_at
        urgency_category = request_obj.defect.urgency_category_name
        incident_sign = request_obj.incident_sign
        parent_application_root_id = request_obj.parent_application_root_id
        if difference.days >= 5 \
                or urgency_category == 'Аварийная' \
                or (incident_sign == 'Нет' and parent_application_root_id is not None) \
                or incident_sign == 'Да':
            raise Http404
        request_obj.status_name = 'Новая'
        request_obj.status_code = 'new'

        request_obj.closing_result.being_under_revision_sign = 'Да'
        request_obj.closing_result.save()

        refinement, _ = Refinement.objects.get_or_create(closing_result=request_obj.closing_result)
        refinement.return_count += 1
        refinement.save()

        serializer = self.get_serializer(request_obj)
        return Response(serializer.data)


class AddressesViewSet(ReadOnlyModelViewSet):
    """
    Класс для получения адресов
    """
    queryset = Address.objects.select_related('ods')
    serializer_class = AddressSerializer
    permission_classes = [IsAuthenticated]


class AddRequestToIncidentViewSet(ModelViewSet):
    """
    Класс для добавления заявки в инцидент
    """
    queryset = Request.objects.filter(Q(status_name="Новая") |
                                      Q(status_name="Ожидает обработки") |
                                      Q(status_name="В работе")) \
        .prefetch_related('defect__work_performed_types', 'defect__work_performed_types__security_events')\
        .select_related('address__ods',
                        'implementing_organization',
                        'defect',
                        'user__organization',
                        'user__implementing_organization',
                        'closing_result',
                        'closing_result__marm_executor',
                        'closing_result__marm_implementing_organization',
                        'closing_result__review',
                        'closing_result__refinement')
    serializer_class = RequestSerializer
    permission_classes = [IsAuthenticated]

    def list(self, request, *args, **kwargs):
        requests_list = []
        for q in self.get_queryset():
            if q.parent_application_root_id:
                parent_request = Request.objects.filter(root_id=q.parent_application_root_id).first()
                if q.defect.category_name == parent_request.defect.category_name and \
                        q.address.problem_address == parent_request.address.problem_address:
                    diff = q.created_at - timedelta(7)
                    if diff < parent_request.created_at and parent_request.created_at + timedelta(1) < q.created_at:
                        requests_list.append(q)
        serializer = self.get_serializer(requests_list, many=True)
        return Response(serializer.data)


class DefectsViewSet(ReadOnlyModelViewSet):
    """
    Класс для получения дефектов
    """
    queryset = Defect.objects.values('category_name', 'name')
    serializer_class = DefectSerializer
    permission_classes = [IsAuthenticated]


class ImplementingOrganizationsViewSet(ModelViewSet):
    """
    Класс для получения организаций-исполнителей
    """
    permission_classes = [IsAuthenticated]

    def list(self, request, *args, **kwargs):
        queryset = ImplementingOrganization.objects.prefetch_related('users').values('name',
                                                                                     'users__first_name',
                                                                                     'users__last_name',
                                                                                     'users__middle_name')
        return Response(queryset)


class WorkPerformedTypesViewSet(ReadOnlyModelViewSet):
    """
    Класс для получения видов выполненных работ
    """
    permission_classes = [IsAuthenticated]

    def list(self, request, *args, **kwargs):
        queryset = WorkPerformedType.objects.prefetch_related('defects').values('work_performed_type', 'defects__name')
        return Response(queryset)
