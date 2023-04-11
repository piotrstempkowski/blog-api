from rest_framework import viewsets, status
from rest_framework.authentication import TokenAuthentication
from rest_framework.response import Response

from .models import CustomUser
from .permissions import AdminOrOwnerAccessPermission
from .serializers import UserSerializer, CreateUserSerializer


class UserViewSet(viewsets.ModelViewSet):
    queryset = CustomUser.objects.all()
    serializer_class = UserSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [AdminOrOwnerAccessPermission]

    def get_serializer_class(self):
        if self.action == "create":
            return CreateUserSerializer
        return UserSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        password = serializer.validated_data.get("password")
        user = serializer.save()
        if password:
            user.set_password(password)
            user.save()
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        partial = self.kwargs.pop("partial", False)
        # print(f"Partial: {partial}")
        instance = self.get_object()
        # print(f"Instance: {instance}")
        # print(f"Request data {request.data}")
        serializer = self.get_serializer(instance, data=request.data)
        serializer.is_valid(raise_exception=True)
        # print(f"Serializer: {serializer}")
        password = request.data.get("password")
        user = serializer.save()
        # print(f"User:{user} ")
        if password:
            user.set_password(password)
            user.save()
        return Response(serializer.data)

    def perform_destroy(self, instance):
        print(f"Instance: {instance}")
        print(instance)
        instance.is_active = False
        instance.set_unusable_password()
        instance.save()


# Create your views here.


class UserBlogViewSet(viewsets.ModelViewSet):
    pass
