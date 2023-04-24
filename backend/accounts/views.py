from rest_framework import viewsets, status
from rest_framework.authentication import TokenAuthentication
from rest_framework.response import Response

from .models import CustomUser
from .permissions import AdminOrOwnerAccessPermission
from .serializers import UserSerializer, CreateUserSerializer, UpdateUserSerializer


class UserViewSet(viewsets.ModelViewSet):
    queryset = CustomUser.objects.all()
    serializer_class = UserSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [AdminOrOwnerAccessPermission]

    def get_serializer_class(self):
        if self.request.method == "POST":
            return CreateUserSerializer
        if self.request.method in ["PUT", "PATCH"]:
            return UpdateUserSerializer
        return UserSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        password = serializer.validated_data.get("password")
        user = serializer.save()
        if password:
            user.set_password(password)
            user.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data)
        serializer.is_valid(raise_exception=True)
        password = request.data.get("password")
        user = serializer.save()
        if password:
            user.set_password(password)
            user.save()
        return Response(serializer.data)

    def perform_destroy(self, instance):
        instance.is_active = False
        instance.set_unusable_password()
        instance.save()


class UserBlogViewSet(viewsets.ModelViewSet):
    pass
