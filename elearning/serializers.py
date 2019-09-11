from django.utils.translation import ugettext_lazy as _

from rest_framework_friendly_errors.mixins import FriendlyErrorMessagesMixin
from rest_framework import serializers, authentication
from rest_framework.authentication import authenticate
from drf_writable_nested import WritableNestedModelSerializer

from elearning.bases.serializers import SerializerBase, SerializerModelBase
from elearning.models import User, Course, Lession
from elearning.constants import USER_TYPE

class UserSerializer(SerializerModelBase):
  password = serializers.CharField(
    label=_("Password"),
    style={'input_type': 'password'},
    trim_whitespace=False,
    write_only=True
  )

  class Meta:
    model = User
    fields = User().get_fields(exclude=('groups', 'user_permissions'))
    read_only_fields = ('is_active', 'is_staff', 'is_superuser', 'last_login', 'date_joined')
    extra_kwargs = {'password': {'write_only': True}}

  def create(self, validated_data):
    user = super().create(validated_data)

    user.set_password(validated_data.get('password'))
    user.save()

    return user

class LoginSerializer(FriendlyErrorMessagesMixin, serializers.Serializer):    
  
  username = serializers.CharField(label=_("Username or email"))
  password = serializers.CharField(
    label=_("Password"),
    style={'input_type': 'password'},
    trim_whitespace=False
  )

  def validate(self, attrs):
    username = attrs.get('username')
    password = attrs.get('password')

    if username and password:
      user = authenticate(request=self.context.get('request'), username=username, password=password)

      if user:
        # From Django 1.10 onwards the `authenticate` call simply
        # returns `None` for is_active=False users.
        # (Assuming the default `ModelBackend` authentication backend.)
        if not user.is_active:
          raise serializers.ValidationError(_('User account is disabled.'))
      else:
        raise serializers.ValidationError(_('Unable to log in with provided credentials.'))
    else:
      raise serializers.ValidationError(_('Must include "username" and "password".'))

    attrs['user'] = user
    return attrs
  
class StudentSerializer(UserSerializer):
  class Meta(UserSerializer.Meta):
    read_only_fields = UserSerializer.Meta.read_only_fields + ('user_type',)

  def create(self, validated_data):
    validated_data['user_type'] = USER_TYPE.STUDENT
    return super().create(validated_data)

class TeacherSerializer(UserSerializer):
  class Meta(UserSerializer.Meta):
    read_only_fields = UserSerializer.Meta.read_only_fields + ('user_type',)

  def create(self, validated_data):
    validated_data['user_type'] = USER_TYPE.TEACHER
    return super().create(validated_data)

class CourseSerializer(SerializerModelBase):
  teacher = serializers.PrimaryKeyRelatedField(queryset=User.objects.filter(user_type=USER_TYPE.TEACHER))

  class Meta:
    model = Course
    fields = Course().get_fields()

class BasicCourseSerializer(CourseSerializer):
  teacher_set = serializers.HiddenField(write_only=True, default=serializers.CurrentUserDefault())
  teacher = serializers.PrimaryKeyRelatedField(read_only=True, default=serializers.CurrentUserDefault())

  class Meta(CourseSerializer.Meta):
    fields = CourseSerializer.Meta.fields + ('teacher_set',)
    read_only_fields = ('teacher',)

  def create(self, validated_data):
    validated_data['teacher'] = validated_data.pop('teacher_set')
    return Course.objects.create(**validated_data)


class LessionSerializer(SerializerModelBase):
  teacher = serializers.PrimaryKeyRelatedField(queryset=User.objects.filter(user_type=USER_TYPE.TEACHER))

  class Meta:
    model = Lession
    fields = Lession().get_fields()

class BasicLessionSerializer(LessionSerializer):
  teacher_set = serializers.HiddenField(write_only=True, default=serializers.CurrentUserDefault())
  teacher = serializers.PrimaryKeyRelatedField(read_only=True, default=serializers.CurrentUserDefault())

  class Meta(LessionSerializer.Meta):
    fields = LessionSerializer.Meta.fields + ('teacher_set',)
    read_only_fields = ('teacher',)

  def create(self, validated_data):
    validated_data['teacher'] = validated_data.pop('teacher_set')
    return Lession.objects.create(**validated_data)

