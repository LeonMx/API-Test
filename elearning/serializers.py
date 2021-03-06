from django.utils.translation import ugettext_lazy as _

from rest_framework_friendly_errors.mixins import FriendlyErrorMessagesMixin
from rest_framework_nested.serializers import NestedHyperlinkedModelSerializer
from rest_framework import serializers, authentication
from rest_framework.authentication import authenticate
from drf_writable_nested import WritableNestedModelSerializer

from elearning.bases.serializers import SerializerBase, SerializerModelBase, NestedPrimaryKeyRelatedField
from elearning.models import User, Course, Lesson, Question, Answer, AnswerStudent
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

class AnswerSerializer(SerializerModelBase):
  question = NestedPrimaryKeyRelatedField(queryset=Question.objects, lookup='question')

  class Meta:
    model = Answer
    fields = Answer().get_fields()

class AnswerQuestionSerializer(AnswerSerializer):
  class Meta(AnswerSerializer.Meta):
    fields = list(AnswerSerializer.Meta.fields)
    fields.remove('question')
    fields.remove('is_correct')

class AnswerStudentSerializer(SerializerModelBase):
  answer = AnswerSerializer()
  student = StudentSerializer()

  class Meta:
    model = AnswerStudent
    fields = AnswerStudent().get_fields()
    
class QuestionSerializer(SerializerModelBase):
  teacher = serializers.PrimaryKeyRelatedField(queryset=User.objects.filter(user_type=USER_TYPE.TEACHER))
  lesson = NestedPrimaryKeyRelatedField(queryset=Lesson.objects, lookup='lesson')
  answers = AnswerQuestionSerializer(read_only=True, many=True)

  class Meta:
    model = Question
    fields = Question().get_fields() + ('answers',)

class BasicQuestionSerializer(QuestionSerializer):
  teacher_set = serializers.HiddenField(write_only=True, default=serializers.CurrentUserDefault())
  teacher = serializers.PrimaryKeyRelatedField(read_only=True, default=serializers.CurrentUserDefault())

  class Meta(QuestionSerializer.Meta):
    fields = QuestionSerializer.Meta.fields + ('teacher_set',)
    read_only_fields = ('teacher',)

  def create(self, validated_data):
    validated_data['teacher'] = validated_data.pop('teacher_set')
    return Question.objects.create(**validated_data)

class QuestionLessonSerializer(QuestionSerializer):
  class Meta(QuestionSerializer.Meta):
    fields = list(QuestionSerializer.Meta.fields)
    fields.remove('lesson')

class LessonSerializer(SerializerModelBase):
  teacher = serializers.PrimaryKeyRelatedField(queryset=User.objects.filter(user_type=USER_TYPE.TEACHER))
  course = NestedPrimaryKeyRelatedField(queryset=Course.objects, lookup='course')
  questions = QuestionLessonSerializer(read_only=True, many=True)

  class Meta:
    model = Lesson
    fields = Lesson().get_fields() + ('questions',)

class BasicLessonSerializer(LessonSerializer):
  teacher_set = serializers.HiddenField(write_only=True, default=serializers.CurrentUserDefault())
  teacher = serializers.PrimaryKeyRelatedField(read_only=True, default=serializers.CurrentUserDefault())

  class Meta(LessonSerializer.Meta):
    fields = LessonSerializer.Meta.fields + ('teacher_set',)
    read_only_fields = ('teacher',)

  def create(self, validated_data):
    validated_data['teacher'] = validated_data.pop('teacher_set')
    return Lesson.objects.create(**validated_data)
 
class LessonAnswerPrimaryKeyRelatedField(serializers.PrimaryKeyRelatedField):
  def get_queryset(self):
    queryset = super().get_queryset()
    if not queryset:
      return None

    view = self.context.get('view', None)
    if not view:
      return None

    pk = view.kwargs.get('pk', None)
    
    if pk and queryset:
      return queryset.filter(question__lesson=pk)
    elif queryset:
      return queryset

class LessonAnswersSerializer(SerializerModelBase):
  answers = LessonAnswerPrimaryKeyRelatedField(queryset=Answer.objects, many=True) 

  class Meta:
    model = Answer
    fields = ('answers',)
   
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