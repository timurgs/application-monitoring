from django.contrib.auth.base_user import BaseUserManager
from django.db.models import Q
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.apps import apps

from django.db import models


class Organization(models.Model):
    """
    Модель организаций
    """
    name = models.CharField(max_length=200, unique=True, verbose_name='Наименование')
    identifier = models.PositiveIntegerField(unique=True, verbose_name='Идентификатор')
    inn = models.PositiveBigIntegerField(unique=True, verbose_name='ИНН')
    business_role = models.CharField(max_length=20, verbose_name='Бизнес-роль')

    class Meta:
        verbose_name = 'Организация'
        verbose_name_plural = 'Организации'

    def __str__(self):
        return f'{self.name} {str(self.identifier)} {str(self.inn)}'


class ImplementingOrganization(models.Model):
    """
    Модель организаций-исполнителей
    """
    name = models.CharField(max_length=200, unique=True, verbose_name='Наименование')
    identifier = models.PositiveIntegerField(unique=True, verbose_name='Идентификатор')
    inn = models.PositiveBigIntegerField(unique=True, verbose_name='ИНН')
    business_role = models.CharField(max_length=20, verbose_name='Бизнес-роль')

    class Meta:
        verbose_name = 'Организация-исполнитель'
        verbose_name_plural = 'Организации-исполнители'

    def __str__(self):
        return f'{self.name} {str(self.identifier)} {str(self.inn)}'


class UserManager(BaseUserManager):
    """
    Миксин для управления пользователями
    """
    use_in_migrations = True

    def _create_user(self, username, password, **extra_fields):
        """
        Create and save a user with the given username and password.
        """
        if not username:
            raise ValueError('The given username must be set')
        GlobalUserModel = apps.get_model(
            self.model._meta.app_label, self.model._meta.object_name
        )
        username = GlobalUserModel.normalize_username(username)
        user = self.model(username=username, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, username, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(username, password, **extra_fields)

    def create_superuser(self, username, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self._create_user(username, password, **extra_fields)


class User(AbstractUser):
    """
    Стандартная модель пользователей
    """
    REQUIRED_FIELDS = []
    objects = UserManager()
    email = None
    first_name = None
    last_name = None
    position = models.CharField(verbose_name='Должность', max_length=40, blank=True)
    username_validator = UnicodeUsernameValidator()
    username = models.CharField(
        _('username'),
        max_length=20,
        unique=True,
        help_text=_('Required. 20 characters or fewer. Letters, digits and @/./+/-/_ only.'),
        validators=[username_validator],
        error_messages={
            'unique': _('A user with that username already exists.'),
        },
    )
    organization = models.ForeignKey(Organization,
                                     verbose_name='Организация',
                                     related_name='organizations',
                                     blank=True,
                                     null=True,
                                     on_delete=models.CASCADE)
    implementing_organization = models.ForeignKey(ImplementingOrganization,
                                                  verbose_name='Организация-исполнитель',
                                                  related_name='implementing_organizations',
                                                  blank=True,
                                                  null=True,
                                                  on_delete=models.CASCADE)

    def __str__(self):
        return self.username

    class Meta:
        verbose_name = 'Пользователь',
        verbose_name_plural = 'Список пользователей',
        ordering = ('username',)
        constraints = [
            models.CheckConstraint(
                check=Q(organization__isnull=False) | Q(implementing_organization__isnull=False),
                name='not_both_null'
            )
        ]


class ODS(models.Model):
    """
    Модель ОДС (объединенных диспетчерских служб)
    """
    number = models.CharField(max_length=109, unique=True, verbose_name='Номер ОДС')

    class Meta:
        verbose_name = 'ОДС'
        verbose_name_plural = 'ОДС'

    def __str__(self):
        return self.number


class Address(models.Model):
    """
    Модель адресов
    """
    country_name = models.CharField(max_length=10, verbose_name='Наименование округа')
    country_code = models.PositiveSmallIntegerField(verbose_name='Код округа')
    district_name = models.CharField(max_length=100, verbose_name='Наименование района')
    district_code = models.PositiveSmallIntegerField(verbose_name='Код района')
    problem_address = models.CharField(max_length=100, unique=True, verbose_name='Адрес проблемы')
    unom = models.PositiveIntegerField(unique=True, verbose_name='УНОМ')
    ods = models.ForeignKey(ODS, verbose_name='ОДС', blank=True, related_name='ods', on_delete=models.CASCADE)
    management_company = models.CharField(max_length=100, verbose_name='Наименование управляющей компании')

    class Meta:
        verbose_name = 'Адрес'
        verbose_name_plural = 'Список адресов'

    def __str__(self):
        return f'{self.problem_address} {str(self.unom)}'


class Defect(models.Model):
    """
    Модель дефектов
    """
    category_name = models.CharField(max_length=33, verbose_name='Наименование категории')
    category_root_id = models.PositiveIntegerField(verbose_name='Корневой идентификатор категории')
    category_code = models.CharField(max_length=100, blank=True, verbose_name='Код категории')
    name = models.CharField(max_length=150, verbose_name='Наименование'),
    short_name = models.CharField(max_length=150, verbose_name='Краткое наименование')
    identifier = models.PositiveIntegerField(verbose_name='Идентификатор')
    code = models.CharField(max_length=150, verbose_name='Код')
    sign_return_for_revision = models.CharField(max_length=3, verbose_name='Признак возврата на доработку')

    class Meta:
        verbose_name = 'Дефект'
        verbose_name_plural = 'Список дефектов'


class WorkPerformedType(models.Model):
    """
    Модель видов выполненных работ
    """
    work_performed_type = models.CharField(max_length=250, unique=True, verbose_name='Вид выполненных работ')
    root_version_id = models.PositiveSmallIntegerField(unique=True, verbose_name='Идентификатор корневой версии')
    defects = models.ManyToManyField(Defect, verbose_name='Дефекты', related_name='work_performed_types', blank=True)

    class Meta:
        verbose_name = 'Вид выполненных работ'
        verbose_name_plural = 'Список видов выполненных работ'
        ordering = ('root_version_id',)

    def __str__(self):
        return f'{self.work_performed_type} {str(self.root_version_id)}'


class SecurityEvents(models.Model):
    """
    Модель охранных мероприятий
    """
    name = models.CharField(max_length=200, unique=True, verbose_name='Наименование')
    root_version_id = models.PositiveIntegerField(unique=True, verbose_name='Идентификатор корневой версии')
    term = models.DateTimeField(verbose_name='Срок')
    work_performed_type = models.ForeignKey(WorkPerformedType,
                                            verbose_name='Вид выполненных работ',
                                            blank=True,
                                            related_name='security_events',
                                            on_delete=models.CASCADE)

    class Meta:
        verbose_name = 'Охранные мероприятия'
        verbose_name_plural = 'Список охранных мероприятий'
        ordering = ('root_version_id',)

    def __str__(self):
        return f'{self.name} {str(self.root_version_id)}'


class Request(models.Model):
    """
    Модель заявок
    """
    root_id = models.PositiveIntegerField(unique=True, verbose_name='Корневой ИД')
    version_id = models.PositiveIntegerField(unique=True, blank=True, null=True, verbose_name='ИД версии')
    number = models.CharField(max_length=11, unique=True, verbose_name='Номер')
    unique_public_services_appeal_number = models.CharField(max_length=27,
                                                            verbose_name='Уникальный номер обращения ГУ (mos.ru)',
                                                            blank=True)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Дата начала действия версии')
    source_name = models.CharField(max_length=23, verbose_name='Наименование источника поступления')
    source_code = models.CharField(max_length=10, verbose_name='Код источника поступления')
    creator_name = models.CharField(max_length=20, verbose_name='Имя создателя')
    incident_sign = models.CharField(max_length=3, verbose_name='Признак инцидента')
    parent_application_root_id = models.PositiveIntegerField(blank=True,
                                                             null=True,
                                                             verbose_name='Корневой идентификатор материнской заявки')
    parent_application_number = models.CharField(max_length=11,
                                                 blank=True,
                                                 verbose_name='Номер материнской заявки')
    comments = models.TextField(max_length=1000, blank=True, null=True, verbose_name='Комментарии')
    description = models.TextField(max_length=1000, verbose_name='Описание')
    question = models.TextField(max_length=1000, blank=True, verbose_name='Наличие у заявителя вопроса')
    urgency_category_name = models.CharField(max_length=9, verbose_name='Наименование категории срочности')
    urgency_category_code = models.CharField(max_length=9, verbose_name='Код категории срочности')
    address = models.ForeignKey(Address, verbose_name='Адрес', blank=True, related_name='requests', on_delete=models.CASCADE)
    entrance = models.PositiveSmallIntegerField(blank=True, null=True, verbose_name='Подъезд')
    floor = models.PositiveSmallIntegerField(blank=True, null=True, verbose_name='Этаж')
    apartment = models.PositiveSmallIntegerField(blank=True, null=True, verbose_name='Квартира')
    implementing_organization = models.ForeignKey(ImplementingOrganization,
                                                  verbose_name='Организация-исполнитель',
                                                  blank=True,
                                                  related_name='requests',
                                                  on_delete=models.CASCADE)
    status_name = models.CharField(max_length=17, verbose_name='Наименование статуса')
    status_code = models.CharField(max_length=17, verbose_name='Код статуса')
    desired_time_from = models.CharField(max_length=70, blank=True, verbose_name='Желаемое время с')
    desired_time_before = models.CharField(max_length=70, blank=True, verbose_name='Желаемое время до')
    payment_category_name = models.CharField(max_length=17, verbose_name='Наименование категории платности')
    payment_category_code = models.CharField(max_length=14, verbose_name='Код категории платности')
    card_payment_sign = models.CharField(max_length=3, verbose_name='Признак оплаты картой')
    defect = models.ForeignKey(Defect, verbose_name='Дефект', blank=True, related_name='requests', on_delete=models.CASCADE)
    user = models.ForeignKey(User, verbose_name='Пользователь', blank=True, related_name='requests', on_delete=models.CASCADE)

    class Meta:
        verbose_name = 'Заявка'
        verbose_name_plural = 'Список заявок'
        ordering = ('number',)

    def __str__(self):
        return f'{str(self.root_id)} {str(self.version_id)} {self.number} {self.unique_public_services_appeal_number}'


class MarmExecutor(models.Model):
    """
    Модель МАРМ (Исполнитель)
    """
    name_reason_refusal = models.CharField(max_length=50, unique=True, verbose_name='Наименование причины отказа')
    failure_reason_id = models.PositiveIntegerField(unique=True, verbose_name='Идентификатор причины отказа')

    class Meta:
        verbose_name = 'МАРМ (Исполнитель)'
        verbose_name_plural = 'МАРМ (Исполнители)'
        ordering = ('failure_reason_id',)

    def __str__(self):
        return f'{self.name_reason_refusal} {self.failure_reason_id}'


class MarmImplementingOrganization(models.Model):
    """
    Модель МАРМ (Организация-исполнитель)
    """
    name_reason_refusal = models.CharField(max_length=51, unique=True, verbose_name='Наименование причины отказа')
    failure_reason_id = models.PositiveIntegerField(unique=True, verbose_name='Идентификатор причины отказа')

    class Meta:
        verbose_name = 'МАРМ (Организация-исполнитель)'
        verbose_name_plural = 'МАРМ (Организации-исполнители)'
        ordering = ('failure_reason_id',)

    def __str__(self):
        return f'{self.name_reason_refusal} {self.failure_reason_id}'


class ClosingResult(models.Model):
    """
    Модель результатов закрытия
    """
    consumed_material = models.CharField(max_length=200, blank=True, verbose_name='Израсходованный материал')
    security_events_sign = models.CharField(max_length=3, verbose_name='Признак проведения охранных мероприятий')
    security_events_time = models.DateTimeField(blank=True, null=True, verbose_name='Время проведения охранных мероприятий')
    actions_taken_during_security_measures = models.CharField(max_length=500,
                                                              blank=True,
                                                              verbose_name='Описание выполненных действий при '
                                                                           'проведении охранных мероприятий')
    effectiveness = models.CharField(max_length=33, verbose_name='Результативность')
    marm_executor = models.ForeignKey(MarmExecutor,
                                      verbose_name='МАРМ (Исполнитель)',
                                      blank=True,
                                      null=True,
                                      related_name='closing_results',
                                      on_delete=models.CASCADE)
    marm_implementing_organization = models.ForeignKey(MarmImplementingOrganization,
                                                       verbose_name='МАРМ (Организация-исполнитель)',
                                                       blank=True,
                                                       null=True,
                                                       related_name='closing_results',
                                                       on_delete=models.CASCADE)
    efficiency_code = models.CharField(max_length=9, verbose_name='Код результативности')
    being_under_revision_sign = models.CharField(max_length=3, verbose_name='Признак нахождения на доработке')
    sign_alerted = models.CharField(max_length=3, verbose_name='Признак “Оповещен”')
    closing_date = models.DateTimeField(auto_now=True, verbose_name='Дата закрытия')
    request = models.OneToOneField(Request, verbose_name='Заявка', blank=True, on_delete=models.CASCADE)

    class Meta:
        verbose_name = 'Результат закрытия'
        verbose_name_plural = 'Список результатов закрытия'


class Review(models.Model):
    """
    Модель отзывов
    """
    dt = models.DateTimeField(auto_now_add=True, verbose_name='Дата')
    review = models.TextField(max_length=200, verbose_name='Отзыв')
    assessment_quality_work = models.PositiveSmallIntegerField(max_length=1,
                                                               verbose_name='Оценка качества выполнения работ')
    closing_result = models.OneToOneField(ClosingResult,
                                          verbose_name='Результат закрытия',
                                          blank=True, null=True,
                                          on_delete=models.CASCADE)

    class Meta:
        verbose_name = 'Отзыв'
        verbose_name_plural = 'Список отзывов'


class Refinement(models.Model):
    """
    Модель доработок
    """
    return_count = models.PositiveSmallIntegerField(verbose_name='Кол-во возвратов')
    last_return_date = models.DateTimeField(auto_now=True, verbose_name='Дата последнего возврата')
    closing_result = models.OneToOneField(ClosingResult,
                                          verbose_name='Результат закрытия',
                                          blank=True,
                                          null=True,
                                          on_delete=models.CASCADE)

    class Meta:
        verbose_name = 'Доработка'
        verbose_name_plural = 'Список доработок'
