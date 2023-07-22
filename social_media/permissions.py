from rest_framework.permissions import BasePermission


class IsProfileOwner(BasePermission):
    def has_object_permission(self, request, view, obj):
        return request.method == "GET" or obj.user == request.user


class IsPostOwner(BasePermission):
    def has_object_permission(self, request, view, obj):
        return request.method == "GET" or obj.author == request.user.profile
