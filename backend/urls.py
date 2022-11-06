from django.urls import path, include
from rest_framework.routers import DefaultRouter

from backend.views import ActiveRequestsViewSet, NewRequestsViewSet, PendingProcessingRequestsViewSet, \
    InProgressRequestsViewSet, ClosedRequestsViewSet, LoginView, RequestsViewSet, RequestsRefinementViewSet, \
    AddressesViewSet, AddRequestToIncidentViewSet, DefectsViewSet, ImplementingOrganizationsViewSet, \
    WorkPerformedTypesViewSet

app_name = 'backend'

router = DefaultRouter()
router.register('work-performed-types', WorkPerformedTypesViewSet, basename='work-performed-types')
router.register('implementing-organizations', ImplementingOrganizationsViewSet, basename='implementing-organizations')
router.register('defects', DefectsViewSet, basename='defects')
router.register('requests/incident', AddRequestToIncidentViewSet, basename='add-request-to-incident')
router.register('addresses', AddressesViewSet, basename='addresses')
router.register('requests/refinement', RequestsRefinementViewSet, basename='requests-refinement')
router.register('requests/all', RequestsViewSet, basename='requests')
router.register('requests/active', ActiveRequestsViewSet, basename='active-requests')
router.register('requests/new', NewRequestsViewSet, basename='new-requests')
router.register('requests/pending-processing', PendingProcessingRequestsViewSet, basename='pending-processing-requests')
router.register('requests/in-progress', InProgressRequestsViewSet, basename='in-progress-requests')
router.register('requests/closing', ClosedRequestsViewSet, basename='closing-requests')

urlpatterns = [
    path('login', LoginView.as_view(), name='login'),
    path('', include(router.urls)),
]
