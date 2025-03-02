from rest_framework.permissions import BasePermission

class IsOwnerOrAdmin(BasePermission):
    """
    Custom permission to only allow owners or admins to access the resource.
    """
    def has_permission(self, request, view):
        if request.user and request.user.is_staff:
            return True
   
        return False

    def has_object_permission(self, request, view, obj):
        if request.user and request.user.is_staff:
            return True
        return obj.user == request.user
