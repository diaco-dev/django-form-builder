from django.contrib.auth import get_user_model
from rest_framework import permissions
from rest_framework.permissions import BasePermission, SAFE_METHODS

from core.type import UserType

User = get_user_model()


class IsOwner(BasePermission):
    """
    Custom permission to only allow owners of an object to edit it.
    """
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        return obj.user == request.user


# ----------------------  IsAdminUserOrReadOnly Permission  -----------------------------
# Global permission check for admin. Not admin, read only
#
class IsAdminUserOrReadOnly(BasePermission):
    message = 'Editing or creating a category is restricted to admin users.'

    def has_permission(self, request, view):
        # Read permissions are allowed to any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        if request.method in SAFE_METHODS:
            return True

        return request.user.is_staff


class CurrentUserOrAdmin(BasePermission):
    def has_object_permission(self, request, view, obj):
        user = request.user
        return user.is_staff or obj.pk == user.pk


class CurrentUserOrAdminOrReadOnly(BasePermission):
    def has_object_permission(self, request, view, obj):
        user = request.user
        if type(obj) == type(user) and obj == user:
            return True
        return request.method in SAFE_METHODS or user.is_staff


# ----------------------  SystemManager Permissions  -----------------------------
class IsSystemManager(BasePermission):
    def has_permission(self, request, view):
        return request.user.user_type == UserType.SYSTEM_MANAGER


class IsSystemManagerOrReadonly(BasePermission):
    message = 'Editing or creating a category is restricted to administrator users.'

    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True

        return request.user.user_type == UserType.SYSTEM_MANAGER


# ----------------------  Customer Permissions  -----------------------------
class IsCustomer(BasePermission):
    def has_permission(self, request, view):
        return request.user.user_type == UserType.CUSTOMER


class IsCustomerOrReadonly(BasePermission):
    message = 'Editing or creating a category is restricted to administrator users.'

    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True

        return request.user.user_type == UserType.SYSTEM_MANAGER


# ----------------------  SuperUser Permissions  -----------------------------
class IsManager(BasePermission):
    def has_permission(self, request, view):
        return request.user.user_type == UserType.MANAGER


class IsManagerOrReadonly(BasePermission):
    message = 'Editing or creating a category is restricted to SuperUser users.'

    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True

        return request.user.user_type == UserType.MANAGER


# ----------------------  CustomsOfficer Permissions  -----------------------------
class IsCustomsOfficer(BasePermission):
    def has_permission(self, request, view):
        return request.user.user_type == UserType.CUSTOMS_OFFICER


# ----------------------  CustomsOfficer Permissions  -----------------------------
class IsManagerOrAbove(BasePermission):
    def has_permission(self, request, view):
        return request.user.user_type <= UserType.MANAGER


class IsManagerOrAboveOrReadonly(BasePermission):
    message = 'Editing or creating a category is restricted to SuperUser users.'

    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True

        return request.user.user_type <= UserType.MANAGER


# ----------------------  OfficeEmployee Permissions  -----------------------------
class IsOfficeEmployee(BasePermission):
    def has_permission(self, request, view):
        return request.user.user_type == UserType.OFFICE_EMPLOYEE


class IsOfficeEmployeeOrReadonly(BasePermission):
    message = 'Editing or creating a category is restricted to SuperUser users.'

    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True

        return request.user.user_type == UserType.OFFICE_EMPLOYEE


class IsOfficeEmployeeOrAbove(permissions.IsAuthenticated):
    def has_permission(self, request, view):
        return request.user.user_type <= UserType.OFFICE_EMPLOYEE


class IsOfficeEmployeeOrAboveOrReadonly(BasePermission):
    message = 'Editing or creating a category is restricted to SuperUser users.'

    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True

        return request.user.user_type <= UserType.OFFICE_EMPLOYEE


# ----------------------  WarehouseEmployee Permissions  -----------------------------
class IsWarehouseEmployeeUser(BasePermission):
    def has_permission(self, request, view):
        return request.user.user_type == UserType.WAREHOUSE_EMPLOYEE


class IsWarehouseEmployeeOrReadonly(BasePermission):
    message = 'Editing or creating a category is restricted to SuperUser users.'

    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True

        return request.user.user_type == UserType.WAREHOUSE_EMPLOYEE


class IsWarehouseEmployeeOrAbove(permissions.IsAuthenticated):
    def has_permission(self, request, view):
        return request.user.user_type <= UserType.WAREHOUSE_EMPLOYEE


class IsWarehouseEmployeeOrAboveOrReadonly(BasePermission):
    message = 'Editing or creating a category is restricted to SuperUser users.'

    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True

        return request.user.user_type <= UserType.WAREHOUSE_EMPLOYEE


    # def has_permission(self, request, view):
    #     return bool(request.user and request.user.is_authenticated)


# ----------------------  WarehouseEmployee Permissions  -----------------------------
class CurrentUserOrManager(permissions.IsAuthenticated):
    def has_object_permission(self, request, view, obj):
        user = request.user
        if isinstance(obj, User) and obj == user:
            return True
        return user.user_type <= UserType.MANAGER


# ----------------------  OfficeEmployee Permissions  -----------------------------
class IsSystemManagerOrIsManagerOrOfficeEmployee(BasePermission):
    def has_permission(self, request, view):
        return request.user.user_type in (UserType.SYSTEM_MANAGER, UserType.MANAGER, UserType.OFFICE_EMPLOYEE)


class IsSystemManagerOrIsManagerOrOfficeEmployeeOrReadonly(BasePermission):
    message = 'Editing or creating a category is restricted to SuperUser users.'

    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True

        return request.user.user_type in (UserType.SYSTEM_MANAGER, UserType.MANAGER, UserType.OFFICE_EMPLOYEE)


# ----------------------  OfficeEmployee Permissions  -----------------------------
class IsSystemManagerOrIsManagerOrOffice(BasePermission):
    def has_permission(self, request, view):
        return request.user.user_type in (UserType.SYSTEM_MANAGER, UserType.MANAGER)


class IsSystemManagerOrIsManagerOrReadonlyOfficeEmployee(BasePermission):
    message = 'Editing or creating a category is restricted to SuperUser users.'

    def has_permission(self, request, view):
        if (request.user.user_type == UserType.OFFICE_EMPLOYEE) and (request.method in SAFE_METHODS):
            return True

        return request.user.user_type in (UserType.SYSTEM_MANAGER, UserType.MANAGER)
