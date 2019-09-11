from django.conf.urls import url, include
from django.contrib.auth.models import User
from rest_framework import routers

from django.contrib import admin
from django.urls import path

from elearning.views import UserViewSet, StudentViewSet, TeacherViewSet, CourseViewSet

# Routers provide an easy way of automatically determining the URL conf.
router = routers.DefaultRouter()
router.register(r'users', UserViewSet, base_name='users')
router.register(r'students', StudentViewSet, base_name='students')
router.register(r'teachers', TeacherViewSet, base_name='teachers')
router.register(r'courses', CourseViewSet, base_name='courses')

# Wire up our API using automatic URL routing.
# Additionally, we include login URLs for the browsable API.
urlpatterns = [
  url(r'^api/v1/', include(router.urls)),
  url(r'^api/v1/info', UserViewSet.as_view({'get': 'info'}), name='info'),
  url(r'^api/v1/login', UserViewSet.as_view({'post': 'login'}), name='login'),
  url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework')),
  path('admin/', admin.site.urls)
]