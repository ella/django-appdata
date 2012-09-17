from django.utils import simplejson as json
from django.db.models.fields.subclassing import Creator
from django.db.models import TextField

from south.modelsinspector import add_introspection_rules

from .registry import app_registry
from .containers import AppDataContainerFactory

class AppDataDescriptor(Creator):
    "Ensure the user attribute is accessible via the profile"
    def __get__(self, instance, instance_type=None):
        if instance is None:
            return self

        value = instance.__dict__[self.field.name]

        if isinstance(value, basestring):
            value = json.loads(value)

        if isinstance(value, dict) and not isinstance(value, AppDataContainerFactory):
            value = AppDataContainerFactory(instance, value)
            instance.__dict__[self.field.name] = value

        return value

    def __set__(self, instance, value):
        if instance is None:
            raise AttributeError("%s must be accessed via instance" % self.field.name)
        if isinstance(value, dict) and not isinstance(value, AppDataContainerFactory):
            value = AppDataContainerFactory(instance, value)
        instance.__dict__[self.field.name] = value


class AppDataField(TextField):
    def __init__(self, *args, **kwargs):
        self.app_registry = kwargs.pop('app_registry', app_registry)
        kwargs.setdefault('default', '{}')
        kwargs.setdefault('editable', False)
        super(AppDataField, self).__init__(*args, **kwargs)

    def contribute_to_class(self, cls, name):
        super(AppDataField, self).contribute_to_class(cls, name)
        setattr(cls, name, AppDataDescriptor(self))

    def get_db_prep_value(self, value, connection, prepared=False):
        """Convert JSON object to a string"""
        return json.dumps(value.serialize())

    def validate(self, value, model_instance):
        super(AppDataField, self).validate(value, model_instance)
        value.validate(model_instance)


add_introspection_rules([], ["^app_data\.fields\.AppDataField"])

