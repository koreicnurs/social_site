from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from rest_framework import status, mixins
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import generics
from rest_framework.viewsets import GenericViewSet

from account.serializers import RegisterSerializer, LoginSerializer, UserSerializer, SearchSerializer
from main.permissions import IsProfileOwner

User = get_user_model()


class RegistrationView(APIView):
    def post(self, request):
        data = request.data
        serializer = RegisterSerializer(data=data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response('Successfully signed up', status=status.HTTP_201_CREATED)


class ActivationView(APIView):
    def get(self, request, activation_code):
        User = get_user_model()
        user = get_object_or_404(User, activation_code=activation_code)
        user.is_active = True
        user.activation_code = ''
        user.save()
        return Response('Your account successfully activated', status=status.HTTP_200_OK)


class LoginView(ObtainAuthToken):
    serializer_class = LoginSerializer


class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        Token.objects.filter(user=user).delete()
        return Response('Successfully logged out', status=status.HTTP_200_OK)


class ProfileViewSet(mixins.RetrieveModelMixin, mixins.UpdateModelMixin, GenericViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def get_permissions(self):
        if self.action == 'get':
            permission_classes = [IsAuthenticated, ]
        else:
            permission_classes = [IsProfileOwner, ]
        return [permission() for permission in permission_classes]


class SearchViewSet(generics.ListAPIView):
    queryset = User.objects.all()
    serializer_class = SearchSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        search = self.request.query_params.get('search')
        if search is not None:
            queryset = queryset.filter(email__icontains=search)
        return queryset




