import json

from django import forms
from django.db.models import TextField
from django.utils.encoding import smart_text
from django.utils import six

from .registry import app_registry
from .containers import AppDataContainerFactory


class AppDataDescriptor(object):
    "Ensure the user attribute is accessible via the profile"

    def __init__(self, field):
        self.field = field

    def __get__(self, instance, instance_type=None):
        if instance is None:
            return self

        value = instance.__dict__[self.field.name]

        if isinstance(value, six.string_types):
            value = json.loads(value)

        if isinstance(value, dict) and not isinstance(value, AppDataContainerFactory):
            value = AppDataContainerFactory(instance, value, app_registry=self.field.app_registry)
            instance.__dict__[self.field.name] = value

        value._instance = instance
        value._model = instance.__class__
        value._app_registry = self.field.app_registry
        return value

    def __set__(self, instance, value):
        if instance is None:
            raise AttributeError("%s must be accessed via instance" % self.field.name)
        if isinstance(value, dict) and not isinstance(value, AppDataContainerFactory):
            value = AppDataContainerFactory(instance, value, app_registry=self.field.app_registry)
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
        if isinstance(value, AppDataContainerFactory):
            value = value.serialize()
        if isinstance(value, dict):
            value = json.dumps(value)
        return value

    def validate(self, value, model_instance):
        super(AppDataField, self).validate(value, model_instance)
        value.validate(model_instance)

    def value_to_string(self, obj):
        value = self._get_val_from_obj(obj)

        if isinstance(value, AppDataContainerFactory):
            value = value.serialize()
        if isinstance(value, dict):
            value = json.dumps(value)

        return smart_text(value)


class ListModelMultipleChoiceField(forms.ModelMultipleChoiceField):
    """
    A ModelMultipleChoiceField that cleans to a list instead of a QuerySet

    Use this on AppDataForms rather than a ModelMultipleChoiceField to make it
    possible to manipulate the app data field like a list.
    """
    def clean(self, value):
        value = super(ListModelMultipleChoiceField, self).clean(value)
        return list(value)

try:
    from south.modelsinspector import add_introspection_rules
except ImportError:
    pass
else:
    add_introspection_rules([], ["^app_data\.fields\.AppDataField"])
    # Django 1.7
