from rest_framework.permissions import BasePermission


class IsProfileOwner(BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method == "GET":
            return True

        return obj.user == request.user


class IsPostOwner(BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method == "GET":
            return True

        return obj.author == request.user.profile
