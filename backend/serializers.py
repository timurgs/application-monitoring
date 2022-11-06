from rest_framework import serializers

from backend.models import Request, Address, ODS, ImplementingOrganization, Defect, User, Organization, \
    WorkPerformedType, SecurityEvents, ClosingResult, MarmExecutor, MarmImplementingOrganization, Review, Refinement


class ODSSerializer(serializers.ModelSerializer):
    class Meta:
        model = ODS
        fields = ('number',)
        read_only_fields = ('number',)


class AddressSerializer(serializers.ModelSerializer):
    ods = ODSSerializer(read_only=True)

    class Meta:
        model = Address
        fields = ('country_name', 'country_code', 'district_name', 'district_code', 'problem_address', 'unom', 'ods',
                  'management_company')
        read_only_fields = ('country_name', 'country_code', 'district_name', 'district_code', 'problem_address', 'unom',
                            'ods', 'management_company')


class SecurityEventsSerializer(serializers.ModelSerializer):
    class Meta:
        model = SecurityEvents
        fields = ('name', 'root_version_id')


class WorkPerformedTypeSerializer(serializers.ModelSerializer):
    security_events = SecurityEventsSerializer(read_only=True, many=True)

    class Meta:
        model = WorkPerformedType
        fields = ('work_performed_type', 'root_version_id', 'security_events', 'defects')
        read_only_field = ('work_performed_type', 'root_version_id', 'security_events', 'defects')


class DefectSerializer(serializers.ModelSerializer):
    work_performed_types = WorkPerformedTypeSerializer(read_only=True, many=True)

    class Meta:
        model = Defect
        fields = ('category_name', 'category_root_id', 'category_code', 'name', 'short_name', 'identifier', 'code',
                  'sign_return_for_revision', 'work_performed_types', 'urgency_category_name', 'urgency_category_code')
        read_only_fields = ('category_name', 'category_root_id', 'category_code', 'name', 'short_name', 'identifier',
                            'code', 'sign_return_for_revision', 'work_performed_types', 'urgency_category_name',
                            'urgency_category_code')


class OrganizationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Organization
        fields = ('business_role',)
        read_only_fields = ('business_role',)


class ImplementingOrganizationUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = ImplementingOrganization
        fields = ('business_role',)
        read_only_fields = ('business_role',)


class ImplementingOrganizationRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = ImplementingOrganization
        fields = ('name', 'identifier', 'inn')
        read_only_fields = ('name', 'identifier', 'inn')


class UserSerializer(serializers.ModelSerializer):
    organization = OrganizationSerializer(read_only=True)
    implementing_organization = ImplementingOrganizationUserSerializer(read_only=True, many=True)

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'middle_name', 'organization', 'implementing_organization')
        read_only_fields = ('username', 'first_name', 'last_name', 'middle_name', 'organization',
                            'implementing_organization')


class RefinementSerializer(serializers.ModelSerializer):
    class Meta:
        model = Refinement
        fields = ('return_count', 'last_return_date')


class MarmImplementingOrganizationSerializer(serializers.ModelSerializer):
    class Meta:
        model = MarmImplementingOrganization
        fields = ('name_reason_refusal', 'failure_reason_id')


class MarmExecutorSerializer(serializers.ModelSerializer):
    class Meta:
        model = MarmExecutor
        fields = ('name_reason_refusal', 'failure_reason_id')


class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = ('dt', 'review', 'assessment_quality_work')


class ClosingResultSerializer(serializers.ModelSerializer):
    marm_executor = MarmExecutorSerializer()
    marm_implementing_organization = MarmImplementingOrganizationSerializer()
    review = ReviewSerializer()
    refinement = RefinementSerializer()

    class Meta:
        model = ClosingResult
        fields = ('consumed_material', 'effectiveness', 'marm_executor', 'marm_implementing_organization',
                  'efficiency_code', 'being_under_revision_sign', 'sign_alerted', 'closing_date', 'review',
                  'refinement')


class RequestSerializer(serializers.ModelSerializer):
    address = AddressSerializer()
    implementing_organization = ImplementingOrganizationRequestSerializer()
    defect = DefectSerializer()
    user = UserSerializer()
    closing_result = ClosingResultSerializer()

    class Meta:
        model = Request
        fields = ('root_id', 'version_id', 'number', 'unique_public_services_appeal_number', 'created_at', 'updated_at',
                  'source_name', 'source_code', 'creator_name', 'incident_sign', 'parent_application_root_id',
                  'parent_application_number', 'comments', 'description', 'question', 'address', 'entrance', 'floor',
                  'apartment', 'implementing_organization', 'status_name', 'status_code', 'desired_time_from',
                  'desired_time_before', 'payment_category_name', 'payment_category_code', 'card_payment_sign',
                  'defect', 'user', 'closing_result')
