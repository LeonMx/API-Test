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
from elearning.serializers import \
    UserSerializer, LoginSerializer, \
    StudentSerializer, TeacherSerializer, \
    CourseSerializer, BasicCourseSerializer, \
    LessonSerializer, BasicLessonSerializer, \
    QuestionSerializer, BasicQuestionSerializer, \
    AnswerSerializer, LessonAnswersSerializer
from elearning.constants import RESPONSE_TYPE, USER_TYPE, QUESTION_TYPE
from elearning.models import User, Course, Lesson, Question, Answer, AnswerStudent, LessonStudent
from elearning.permissions import IsTeacher, IsStudent

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
    permission_classes = [IsAuthenticated&(IsAdminUser|IsTeacher)]

    def get_queryset(self):
        return self.queryset.filter(
            user_type=USER_TYPE.TEACHER
        )

class StudentViewSet(UserViewSet):
    serializer_class = StudentSerializer
    permission_classes = [IsAuthenticated&(IsAdminUser|IsTeacher|IsStudent)]

    def get_queryset(self):
        return self.queryset.filter(
            user_type=USER_TYPE.STUDENT
        )

class CourseViewSet(viewsets.ModelViewSet):
    queryset = Course.objects.all()

    def get_serializer_class(self):
        if self.request.user.is_staff:
            return CourseSerializer
        return BasicCourseSerializer

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            permission_classes = [IsAuthenticated&(IsAdminUser|IsTeacher)]
        else:
            permission_classes = [IsAuthenticated]
            
        return [permission() for permission in permission_classes]

class LessonViewSet(viewsets.ModelViewSet):
    queryset = Lesson.objects.all()

    def get_queryset(self):
        course_pk = self.kwargs.get('course_pk', None)
        if course_pk:
            return Lesson.objects.filter(course=course_pk)
        else:
            return Lesson.objects.all()

    def get_serializer_class(self):
        if not self.serializer_class:
            if self.request.user.is_staff:
                return LessonSerializer
            else:
                return BasicLessonSerializer
        else:
            return self.serializer_class

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            permission_classes = [IsAuthenticated&(IsAdminUser|IsTeacher)]
        elif self.action == 'select_answers':
            permission_classes = [IsStudent]
        else:
            permission_classes = [IsAuthenticated]
            
        return [permission() for permission in permission_classes]

    @action(detail=True, methods=['post'], serializer_class=LessonAnswersSerializer)
    def select_answers(self, request, pk):
        user = request.user
        data = request.data
        answers_pk = data.get('answers', None)

        serializer = LessonAnswersSerializer(data=data, many=True)
        serializer.is_valid(raise_exception=True)

        score = 0
        lesson = Lesson.objects.get(pk=pk)
        answers = Answer.objects.filter(pk__in=answers_pk)
        questions = Question.objects.filter(answers__in=answers)
        list_answers_student = []

        AnswerStudent.objects.filter(answer__question__lesson=lesson, student=user).delete()

        for answer in answers:
            list_answers_student.append(AnswerStudent(answer=answer, student=user)) 

        AnswerStudent.objects.bulk_create(list_answers_student)

        def question_boolean(question, answers):
            if answers.filter(question=question, is_correct=True).exists():
                return question.score
            else:
                return 0

        def question_one(question, answers):
            return question_boolean(question, answers)

        def question_more_than_one(question, answers):
            if len(answers.filter(question=question, is_correct=True)) > 1:
                return question.score
            else:
                return 0
        
        def question_more_than_one_all(question, answers):
            if len(Answers.objects.filter(question=question, is_correct=True)) == \
                len(answer.filter(question=question, is_correct=True)):
                return question.score
            else:
                return 0

        method_question = { 
            QUESTION_TYPE.BOOLEAN : question_boolean,
            QUESTION_TYPE.ONE : question_one,
            QUESTION_TYPE.MORE_THAN_ONE : question_more_than_one,
            QUESTION_TYPE.MORE_THAN_ONE_ALL : question_more_than_one_all
        }

        for question in questions:
            score += method_question[question.type](question, answers)

        LessonStudent.objects.filter(lesson=lesson, student=user).delete()
        LessonStudent.objects.create(lesson=lesson, student=user, score=score,)

        approval_score = lesson.approval_score
        lesson_approved = lesson.approval_score <= score

        return ResponseClient(
            type=RESPONSE_TYPE.SUCCESS,
            message= (_("Lesson approved with %s score") if lesson_approved else _("Lesson not approved. Your score is %s. At least %s point are required")) % (score, approval_score),
            data={
                "score": score,
            }
        )

class QuestionViewSet(viewsets.ModelViewSet):
    queryset = Question.objects.all()

    def get_queryset(self):
        lesson_pk = self.kwargs.get('lesson_pk', None)
        if lesson_pk:
            return Question.objects.filter(lesson=lesson_pk)
        else:
            return Question.objects.all()

    def get_serializer_class(self):
        if self.request.user.is_staff:
            return QuestionSerializer
        return BasicQuestionSerializer

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            permission_classes = [IsAuthenticated&(IsAdminUser|IsTeacher)]
        else:
            permission_classes = [IsAuthenticated]
            
        return [permission() for permission in permission_classes]

class AnswerViewSet(viewsets.ModelViewSet):
    queryset = Answer.objects.all()
    serializer_class = AnswerSerializer

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            permission_classes = [IsAuthenticated&(IsAdminUser|IsTeacher)]
        else:
            permission_classes = [IsAuthenticated]
            
        return [permission() for permission in permission_classes]
