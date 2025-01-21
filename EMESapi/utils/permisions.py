from rest_framework.permissions import BasePermission

class IsOwnerOrAdmin(BasePermission):
    """
    Custom permission to only allow owners or admins to access the resource.
    """

    def has_permission(self, request, view):
        if request.user and request.user.is_staff:
            return True
        
        if hasattr(view, 'get_object') and view.get_object():
            obj = view.get_object()
            return obj.user == request.user
        
        return False
