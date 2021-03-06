from rest_framework.permissions import BasePermission
from elearning.constants import USER_TYPE

class IsTeacherUser(BasePermission):
    """
    Allows access only to teacher users.
    """

    def has_permission(self, request, view):
        return bool(request.user and request.user.user_type == USER_TYPE.TEACHER)

class IsStudentUser(BasePermission):
    """
    Allows access only to student users.
    """

    def has_permission(self, request, view):
        return bool(request.user and request.user.user_type == USER_TYPE.STUDENT)