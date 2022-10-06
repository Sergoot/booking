from rest_framework import permissions


class IsOwnerOrAdminUser(permissions.BasePermission):
    """ Разрешение на действия с объектом только владельцу или админу """

    def has_object_permission(self, request, view, obj):
        return bool(obj.client == request.user or request.user.is_staff)
