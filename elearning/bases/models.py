from django.db import models
from elearning.utils import to_json

class ModelBase():
  # Get fields of model
  def get_fields(self, exclude=None):
    def not_in_seq(names):
      return lambda name: name not in names

    fields = self._meta.get_fields()
    default_field_names = [f.name for f in fields
                           if (getattr(f, 'serialize', False) or
                               getattr(f, 'primary_key', False))]

    if exclude is None:
      field_names = default_field_names
    else:
      field_names = filter(not_in_seq(exclude), default_field_names)

    field_names = tuple(field_names)

    return field_names

  def to_dict(self, exclude=[]):
    return dict([(attr, getattr(self, attr)) for attr in [f.name for f in self._meta.fields] if not attr in exclude])

  def to_json(self, exclude=[]):
    json = to_json(self)
    data = json['fields']
    data[self._meta.pk.name] = json['pk']
    return {k:v for k,v in data.items() if k not in exclude}