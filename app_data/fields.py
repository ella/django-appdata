from django.utils import simplejson as json

from south.modelsinspector import add_introspection_rules

from jsonfield.fields import JSONField

from .registry import app_registry
from .containers import AppDataContainerFactory


class AppDataField(JSONField):
    def __init__(self, *args, **kwargs):
        self.app_registry = kwargs.pop('app_registry', app_registry)
        kwargs.setdefault('default', '{}')
        kwargs.setdefault('editable', False)
        super(AppDataField, self).__init__(*args, **kwargs)

    def to_python(self, value):
        """Convert string value to JSON and wrap it in AppDataContainerFactory"""
        if isinstance(value, basestring):
            try:
                val = json.loads(value, **self.load_kwargs)
                return AppDataContainerFactory(self.model, val, app_registry=self.app_registry)
            except ValueError:
                pass

        # app_data = {} should use AppDataContainerFactory
        if isinstance(value, dict) and not isinstance(value, AppDataContainerFactory):
            value = AppDataContainerFactory(self.model, value, app_registry=self.app_registry)

        return value

    def get_db_prep_value(self, value, connection, prepared=False):
        """Convert JSON object to a string"""
        if hasattr(value, 'serialize'):
            value = value.serialize()

        return json.dumps(value, **self.dump_kwargs)

    def validate(self, value, model_instance):
        super(AppDataField, self).validate(value, model_instance)
        value.validate(model_instance)


add_introspection_rules([], ["^app_data\.fields\.AppDataField"])

