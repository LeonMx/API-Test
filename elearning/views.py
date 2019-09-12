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
from elearning.permissions import IsTeacherUser, IsStudentUser

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
    permission_classes = [IsAuthenticated&(IsAdminUser|IsTeacherUser)]

    def get_queryset(self):
        return self.queryset.filter(
            user_type=USER_TYPE.TEACHER
        )

class StudentViewSet(UserViewSet):
    serializer_class = StudentSerializer
    permission_classes = [IsAuthenticated&(IsAdminUser|IsTeacherUser)]

    def get_queryset(self):
        return self.queryset.filter(
            user_type=USER_TYPE.STUDENT
        )

class CourseViewSet(viewsets.ModelViewSet):
    queryset = Course.objects.all()

    def get_queryset(self):
        courses = Lesson.objects.all()

        if self.request.user.user_type == USER_TYPE.STUDENT:
            courses.objects.all().filter(opened=True)
        
        return courses

    def get_serializer_class(self):
        if self.request.user.is_staff:
            return CourseSerializer
        return BasicCourseSerializer

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            permission_classes = [IsAuthenticated&(IsAdminUser|IsTeacherUser)]
        else:
            permission_classes = [IsAuthenticated]
            
        return [permission() for permission in permission_classes]

class LessonViewSet(viewsets.ModelViewSet):
    queryset = Lesson.objects.all()

    def get_queryset(self):
        course_pk = self.kwargs.get('course_pk', None)
        if course_pk:
            lessons = Lesson.objects.filter(course=course_pk)
        else:
            lessons = Lesson.objects.all()

        if self.request.user.user_type == USER_TYPE.STUDENT:
            lessons.filter(opened=True)
        
        return lessons

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
            permission_classes = [IsAuthenticated&(IsAdminUser|IsTeacherUser)]
        elif self.action == 'select_answers':
            permission_classes = [IsStudentUser]
        else:
            permission_classes = [IsAuthenticated]
            
        return [permission() for permission in permission_classes]

    @action(detail=True, methods=['post'], serializer_class=LessonAnswersSerializer)
    def select_answers(self, request, pk):
        score = 0
        list_answers_student = []

        # get user and data from request
        user = request.user
        data = request.data
        # get answers sended
        answers_pk = data.get('answers', None)

        # validate data
        serializer = LessonAnswersSerializer(data=data, many=True)
        serializer.is_valid(raise_exception=True)

        # get lesson 
        lesson = Lesson.objects.get(pk=pk)
        # get answers filtering by answers sended
        answers = Answer.objects.filter(pk__in=answers_pk)
        # get questions filtering by answers object
        questions = Question.objects.filter(answers__in=answers)

        # delete previously saved answers by lesson and user
        AnswerStudent.objects.filter(answer__question__lesson=lesson, student=user).delete()

        # preparing to save list answers sended for user
        for answer in answers:
            list_answers_student.append(AnswerStudent(answer=answer, student=user)) 

        # save list answers
        AnswerStudent.objects.bulk_create(list_answers_student)

        # get score for question type boolean answer
        def question_boolean(question, answers):
            if answers.filter(question=question, is_correct=True).exists():
                return question.score
            else:
                return 0
        # get score for question type one answer correct
        def question_one(question, answers):
            return question_boolean(question, answers)
        # get score for question type more than one answers correct
        def question_more_than_one(question, answers):
            if len(answers.filter(question=question, is_correct=True)) > 1:
                return question.score
            else:
                return 0
        # get score for question type more than one and all answers correct
        def question_more_than_one_all(question, answers):
            if len(Answers.objects.filter(question=question, is_correct=True)) == \
                len(answer.filter(question=question, is_correct=True)):
                return question.score
            else:
                return 0

        # group method
        method_score_question = { 
            QUESTION_TYPE.BOOLEAN : question_boolean,
            QUESTION_TYPE.ONE : question_one,
            QUESTION_TYPE.MORE_THAN_ONE : question_more_than_one,
            QUESTION_TYPE.MORE_THAN_ONE_ALL : question_more_than_one_all
        }
        
        # get score for each question
        for question in questions:
            score += method_score_question[question.type](question, answers)

        # delete previously saved lesson by lesson and user
        LessonStudent.objects.filter(lesson=lesson, student=user).delete()
        # save lesson with score
        LessonStudent.objects.create(lesson=lesson, student=user, score=score)

        # is approval score?
        approval_score = lesson.approval_score
        lesson_approved = lesson.approval_score <= score

        return ResponseClient(
            type=RESPONSE_TYPE.SUCCESS,
            message= (_("Lesson approved with %s score")) % (score) \
                if lesson_approved else \
                    (_("Lesson not approved. Your score is %s. At least %s point are required")) % (score, approval_score),
            data={
                "score": score,
            }
        )

class QuestionViewSet(viewsets.ModelViewSet):
    queryset = Question.objects.all()

    def get_queryset(self):
        lesson_pk = self.kwargs.get('lesson_pk', None)
        if lesson_pk:
            questions = Question.objects.filter(lesson=lesson_pk)
        else:
            questions = Question.objects.all()

        return question

    def get_serializer_class(self):
        if self.request.user.is_staff:
            return QuestionSerializer
        return BasicQuestionSerializer

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            permission_classes = [IsAuthenticated&(IsAdminUser|IsTeacherUser)]
        else:
            permission_classes = [IsAuthenticated]
            
        return [permission() for permission in permission_classes]

class AnswerViewSet(viewsets.ModelViewSet):
    queryset = Answer.objects.all()
    serializer_class = AnswerSerializer

    def get_queryset(self):
        question_pk = self.kwargs.get('question_pk', None)
        if question_pk:
            return Answer.objects.filter(question=question_pk)
        else:
            return Answer.objects.all()

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            permission_classes = [IsAuthenticated&(IsAdminUser|IsTeacherUser)]
        else:
            permission_classes = [IsAuthenticated]
            
        return [permission() for permission in permission_classes]
