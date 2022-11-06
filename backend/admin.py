from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Organization, ImplementingOrganization, ODS, Address, Defect, WorkPerformedType, \
    SecurityEvents, Request, MarmExecutor, MarmImplementingOrganization, ClosingResult, Review, Refinement


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    """
    Панель управления пользователями
    """
    model = User

    fieldsets = (
        (None, {'fields': ('username', 'password', 'organization', 'implementing_organization')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'position')}),
        ('Permissions', {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
        }),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )
    list_display = ('username', 'first_name', 'last_name', 'middle_name', 'is_staff')


@admin.register(Organization)
class ShopAdmin(admin.ModelAdmin):
    pass


@admin.register(ImplementingOrganization)
class CategoryAdmin(admin.ModelAdmin):
    pass


@admin.register(ODS)
class ProductAdmin(admin.ModelAdmin):
    pass


@admin.register(Address)
class ProductInfoAdmin(admin.ModelAdmin):
    pass


@admin.register(Defect)
class ParameterAdmin(admin.ModelAdmin):
    pass


@admin.register(WorkPerformedType)
class OrderAdmin(admin.ModelAdmin):
    pass


@admin.register(SecurityEvents)
class OrderItemAdmin(admin.ModelAdmin):
    pass


@admin.register(Request)
class ContactAdmin(admin.ModelAdmin):
    pass


@admin.register(MarmExecutor)
class ContactAdmin(admin.ModelAdmin):
    pass


@admin.register(MarmImplementingOrganization)
class ContactAdmin(admin.ModelAdmin):
    pass


@admin.register(ClosingResult)
class ContactAdmin(admin.ModelAdmin):
    pass


@admin.register(Review)
class ContactAdmin(admin.ModelAdmin):
    pass


@admin.register(Refinement)
class ContactAdmin(admin.ModelAdmin):
    pass
