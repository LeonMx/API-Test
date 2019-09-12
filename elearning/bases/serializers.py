from rest_framework_friendly_errors.mixins import FriendlyErrorMessagesMixin
from rest_framework import serializers
from drf_writable_nested import WritableNestedModelSerializer

class ModelSerializer(FriendlyErrorMessagesMixin, serializers.ModelSerializer):
  pass

class SerializerBase(FriendlyErrorMessagesMixin, serializers.Serializer):
  pass

class SerializerModelBase(SerializerBase, WritableNestedModelSerializer):
  __remove_fields__ = tuple()

  def __init__(self, *args, **kwargs):
    for f in self.__remove_fields__:
      if f in self.fields:
        self.fields.pop(f)
        
    super().__init__(*args, **kwargs)

  def update(self, instance, validated_data):
    _validate_data = validated_data.copy()

    relations, reverse_relations = self._extract_relations(_validate_data)

    self._set_pk_to_reverse_relations(instance, reverse_relations)
    
    return super().update(instance, validated_data)
    
  def _set_pk_to_reverse_relations(self, instance, reverse_relations):
    self.initial_data._mutable = True

    for field_name, (related_field, field, field_source) in reverse_relations.items():

      related_data = self.get_initial().get(field_name, None)

      if related_data is None:
        continue

      if related_field.one_to_one:
        # If an object already exists, fill in the pk so
        # we don't try to duplicate it
        pk_name = field.Meta.model._meta.pk.attname
        if pk_name not in related_data and 'pk' in related_data:
            pk_name = 'pk'
        if pk_name not in related_data:
            related_instance = getattr(instance, field_source, None)
            if related_instance:
                related_data[pk_name] = related_instance.pk
        
        self.initial_data[field_name+'.'+pk_name] = related_data[pk_name]

    self.initial_data._mutable = False

class NestedPrimaryKeyRelatedField(serializers.PrimaryKeyRelatedField):
  lookup = None

  def __init__(self, **kwargs):
    self.lookup = kwargs.pop('lookup', self.lookup)
    super().__init__(**kwargs)

  def get_queryset(self):
    queryset = super().get_queryset()
    if not queryset:
      return None

    view = self.context.get('view', None)
    if not view:
      return None

    pk = view.kwargs.get(self.lookup + '_pk', None)

    print(self.lookup, pk)
        
    if self.lookup and pk and queryset:
      return queryset.filter(pk=pk)
    elif queryset:
      return queryset
