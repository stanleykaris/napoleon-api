from rest_framework import permissions

class IsAdminOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow admins to edit objects,
    but allow read-only access to everyone.
    """
    def has_permission(self, request, view):
        # Read permissions are allowed to any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Write permissions are only allowed to admin users.
        return request.user and request.user.is_staff

class IsOwnerOrAdmin(permissions.BasePermission):
    """
    Custom permission to only allow owners of an object or admins to edit it.
    """
    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        if request.method in permissions.SAFE_METHODS:
            return True
            
        # Check if the user is the owner of the object or an admin
        if hasattr(obj, 'user'):
            return obj.user == request.user or request.user.is_staff
        return False

class IsAdminOrPartner(permissions.BasePermission):
    """
    Custom permission to only allow admin users or partner organization members.
    """
    def has_permission(self, request, view):
        # Allow read-only access to all authenticated users
        if request.method in permissions.SAFE_METHODS:
            return request.user and request.user.is_authenticated
            
        # Allow full access to staff users
        if request.user and request.user.is_staff:
            return True
            
        # Check if the user is associated with a partner organization
        # This assumes you have a way to check if a user is a partner
        # You might need to adjust this based on your user model
        return hasattr(request.user, 'is_partner') and request.user.is_partner
