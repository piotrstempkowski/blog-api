from rest_framework import permissions

from .models import CustomUser


class AdminOrOwnerAccessPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        # If the user is not authenticated, deny permission
        if not request.user.is_authenticated:
            return False

        # If the user is an admin, grant full permissionss
        if request.user.is_staff:
            return True
        # If the request is to create a new user, deny permission
        if view.action == "create":
            return False

        # Allow the user to update their own data
        if view.action in ["update", "partial_update", "retrieve"]:
            return True

    def has_object_permission(self, request, view, obj):
        # If the user is an admin, grant full permissions
        if request.user.is_staff:
            return True

        # If the object is a CustomUser instance
        if isinstance(obj, CustomUser):
            # Only allow the user to retrieve, update, and partially update their own data
            if request.method in ["GET", "PUT", "PATCH"]:
                return obj == request.user




