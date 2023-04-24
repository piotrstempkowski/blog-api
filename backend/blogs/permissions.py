from rest_framework import permissions


class StaffAllReadOnlyUser(permissions.BasePermission):
    def has_permission(self, request, view):
        # check authentication
        if not request.user.is_authenticated:
            return False
        # Staff members grants all permissions
        if request.user.is_staff:
            return True
        if request.method in permissions.SAFE_METHODS:
            return True

        return False


class IsAuthorOrAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        # If request user is Admin grants permissions to all methods
        if request.user.is_staff:
            return True
        # If request user is Author grands permissions to methods for his model
        if request.method in ["PUT", "PATCH", "DELETE"]:
            return obj.author == request.user
        # If request user can POST and GET all models
        if request.method in ["POST", "GET"]:
            return True

        return False
