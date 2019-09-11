from django.views import View
from django.shortcuts import get_object_or_404
from django.db.models import Q
from distutils.util import strtobool

from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response

import django_filters
import operator


class ResponseClient(Response):
  """
  An HttpResponse that allows its data to be rendered into
  arbitrary media types.
  """

  def __init__(self, data=None, message=None, type=None, status=None,
    template_name=None, headers=None,
    exception=False, content_type=None):

    _data = {
      "type": type,
      "message": message,
      "data": data
    }

    super().__init__(
      data=_data, 
      status=status, 
      template_name=template_name, 
      headers=headers, 
      exception=exception, 
      content_type=content_type
    )

class ViewBase(View):

  def __init__(self, *args, **kwargs):
    self.ResponseClient = ResponseClient
        
    super().__init__(*args, **kwargs)

  @staticmethod
  def async(method, is_async=False, *args, **kwargs):
    if is_async:
      task_id = uuid()
      if not 'task_id' in kwargs:
        kwargs['task_id'] = task_id
      method.apply_async(args=args, kwargs=kwargs, task_id=task_id)
      return task_id
    else:
      return method(*args, **kwargs)

  @staticmethod
  def str2bool(v):
    v = 'f' if not v else v
    return bool(strtobool(v.lower()))

class CharInFilter(django_filters.BaseInFilter, django_filters.CharFilter):
  pass

class StandardResultsSetPagination(PageNumberPagination):
  page_size = 20
  page_size_query_param = 'page_size'
  max_page_size = 100

class OtherLookupFieldMixin(object):

  def get_object(self):
    queryset = self.get_queryset()             # Get the base queryset
    queryset = self.filter_queryset(queryset)  # Apply any filter backends
    
    filter = {}
    value = self.kwargs[self.lookup_field]

    if self.lookup_field in ['pk', None] and value.isdigit():
        filter[self.lookup_field] = value
    else:
        filter[self.other_lookup_field] = value

    obj = get_object_or_404(queryset, **filter)

    # May raise a permission denied
    self.check_object_permissions(self.request, obj)
    return obj