import hashlib
import os
import json

from django.utils.encoding import force_text
from django.core.serializers.json import DjangoJSONEncoder
from django.db import models
from django.db.models.query import QuerySet
from django.core.serializers import serialize

from datetime import datetime
from jinja2 import Environment, FileSystemLoader

THIS_DIR = os.path.dirname(os.path.abspath(__file__))

def generate_token(seed=''):
  return hashlib.md5((seed + str(datetime.now())).encode('utf-8')).hexdigest()

def get_template(tmpl):
   env = Environment(loader=FileSystemLoader(os.path.join(THIS_DIR, 'templates')), trim_blocks=True)
   return env.get_template(tmpl)

class LazyEncoder(DjangoJSONEncoder):
    def default(self, obj):
        if isinstance(obj, QuerySet):
            return list(obj.values())
        elif isinstance(obj, models.Model):
            return obj.to_dict()
        elif isinstance(obj, datetime):
            return force_text(obj)
        elif isinstance(obj, enum.Enum):
            return obj.value
        elif attr.has(obj.__class__):
            return attr.asdict(obj)
        elif isinstance(obj, Exception):
            return {
                "error": obj.__class__.__name__,
                "args": obj.args,
            }
        return super(LazyEncoder, self).default(obj)

def to_json(obj):
  return json.loads(serialize('json', [obj,], cls=LazyEncoder))[0]