from django.db import transaction
from django_filters.rest_framework import DjangoFilterBackend
from django.contrib.auth import login
from django.utils.translation import ugettext as _

from rest_framework import filters, mixins, serializers, status, viewsets
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.authtoken.models import Token
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response

from elearning.bases.views import ViewBase, ResponseClient
from elearning.decorators import serializer_class
from elearning.serializers import UserSerializer, LoginSerializer, StudentSerializer, TeacherSerializer
from elearning.constants import RESPONSE_TYPE, USER_TYPE
from elearning.models import User

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]

    filter_backends = (
        DjangoFilterBackend,
        filters.SearchFilter,
    )

    filterset_fields = [
        'username',
        'email',
        'first_name',
        'last_name'
    ]

    search_fields = (
        'username',
        'email',
        'first_name',
        'last_name'
    )

    @action(detail=False, methods=['post'], permission_classes=[], serializer_class=LoginSerializer)
    def login(self, request):
        '''
        Login user.
        '''
        serializer = LoginSerializer(data=request.data, context={"request":request})

        serializer.is_valid(raise_exception=True)

        user = serializer.validated_data['user']
        token, created = Token.objects.get_or_create(user=user)

        login(request, user)

        user_data = UserSerializer(instance=user).data
        
        return ResponseClient(
            type=RESPONSE_TYPE.SUCCESS,
            message=_("You have successfully logged in."),
            data={
                "user": user_data,
                "authtoken": token.key
            }
        )

    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def info(self, request):
        if not request.user:
            raise APIException(_("You are not logged in."))

        user_data = UserSerializer(instance=request.user).data
        token, created = Token.objects.get_or_create(user=request.user)
        
        return Response({
            "user": user_data,
            "authtoken": token.key
        })

class TeacherViewSet(UserViewSet):
    serializer_class = TeacherSerializer

    def get_queryset(self):
        return self.queryset.filter(
            user_type=USER_TYPE.TEACHER
        )

class StudentViewSet(UserViewSet):
    serializer_class = StudentSerializer

    def get_queryset(self):
        return self.queryset.filter(
            user_type=USER_TYPE.STUDENT
        )
        