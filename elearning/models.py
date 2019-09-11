from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import ugettext_lazy as _

from rest_framework.validators import UniqueValidator

from elearning.bases.models import ModelBase
from elearning.constants import USER_TYPE, QUESTION_TYPE

USER_TYPE_CHOICES = (
  (USER_TYPE.STUDENT, 'student'),
  (USER_TYPE.TEACHER, 'teacher'),
  (USER_TYPE.ADMIN, 'admin'),
)

QUESTION_TYPE_CHOICES = (
  (QUESTION_TYPE.BOOLEAN, 'boolean'),
  (QUESTION_TYPE.ONE, 'one'),
  (QUESTION_TYPE.MORE_THAN_ONE, 'more_than_one'),
  (QUESTION_TYPE.MORE_THAN_ONE_ALL, 'more_than_one_all')
)

class User(AbstractUser, ModelBase):
  user_type = models.PositiveSmallIntegerField(
    choices=USER_TYPE_CHOICES, 
    blank=True, 
    default=USER_TYPE.STUDENT
  )

  def save(self, *args, **kwargs):
    if self.is_staff:
      self.user_type = USER_TYPE.ADMIN

    super(User, self).save(*args, **kwargs)

class Course(models.Model, ModelBase):
  class Meta:
    verbose_name = _('course')
    verbose_name_plural = _('courses')
  
  def __str__(self):
    return self.title

  title = models.CharField(
    max_length=150, 
    null=False, 
    blank=False
  )
  description = models.TextField(
    max_length=500, 
    blank=True,
    null=True
  )
  opened = models.BooleanField(
    default=False
  )
  teacher = models.ForeignKey(
    User,
    related_name='course_teacher',
    on_delete=models.CASCADE
  )
  previous = models.ForeignKey(
    'self', 
    related_name='course_previous', 
    blank=True, 
    null=True,
    on_delete=models.CASCADE
  )

class Lession(models.Model, ModelBase):
  class Meta:
    verbose_name = _('lession')
    verbose_name_plural = _('lessions')

  def __str__(self):
    return self.title

  title = models.CharField(
    max_length=150, 
    null=False, 
    blank=False
  )
  description = models.TextField(
    max_length=500, 
    blank=True,
    null=True
  )
  opened = models.BooleanField(
    default=False
  )
  approval_score = models.IntegerField(
    blank=True, 
    null=True
  )
  teacher = models.ForeignKey(
    User, 
    related_name='lession_teacher',
    on_delete=models.CASCADE
  )
  course = models.ForeignKey(
    Course, 
    related_name='lession_course',
    on_delete=models.CASCADE
  )
  previous = models.ForeignKey(
    'self', 
    related_name='lession_previous', 
    blank=True, 
    null=True,
    on_delete=models.CASCADE
  )

class Question(models.Model, ModelBase):
  class Meta:
    verbose_name = _('question')
    verbose_name_plural = _('questions')

  def __str__(self):
    return self.text

  text = models.CharField(
    max_length=150, 
    null=False, 
    blank=False
  )
  type = models.PositiveSmallIntegerField(
    choices=QUESTION_TYPE_CHOICES,
    blank=True, 
    default=QUESTION_TYPE.BOOLEAN
  )
  score = models.IntegerField(
    blank=True, 
    null=True
  )
  lession = models.ForeignKey(
    Lession, 
    related_name='question_lession',
    on_delete=models.CASCADE
  )
  teacher = models.ForeignKey(
    User, 
    related_name='question_teacher',
    on_delete=models.CASCADE
  )

class Answer(models.Model, ModelBase):
  class Meta:
    verbose_name = _('answer')
    verbose_name_plural = _('answers')

  text = models.CharField(
    max_length=150, 
    null=False, 
    blank=False
  )
  is_correct = models.BooleanField(
    default=False
  )
  question = models.ForeignKey(
    Question, 
    related_name='answer_question',
    on_delete=models.CASCADE
  )

class LessionStudent(models.Model, ModelBase):
  class Meta:
    verbose_name = _('lession_student')
    verbose_name_plural = _('lession_students')

  lession = models.ForeignKey(
    Lession, 
    related_name='lessionstudent_lession',
    on_delete=models.CASCADE
  )
  student = models.ForeignKey(
    User, 
    related_name='lessionstudent_student',
    on_delete=models.CASCADE
  )
  score = models.IntegerField(
    null=True, 
    blank=True
  )

class AnswerStudent(models.Model, ModelBase):
  class Meta:
    verbose_name = _('lession_student')
    verbose_name_plural = _('lession_students')

  answer = models.ForeignKey(
    Answer, 
    related_name='answerstudent_answer',
    on_delete=models.CASCADE
  )
  student = models.ForeignKey(
    User, 
    related_name='answerstudent_student',
    on_delete=models.CASCADE
  )
