from copy import copy

from django.forms import Form
from django.core.exceptions import ValidationError

from .registry import app_registry

class AppDataContainerFactory(dict):
    def __init__(self, model, *args, **kwargs):
        self._model = model
        self._app_registry = kwargs.pop('app_registry', app_registry)
        super(AppDataContainerFactory, self).__init__(*args, **kwargs)

    def __setattr__(self, name, value):
        if name.startswith('_') or self._app_registry.get_class(name, self._model) is None:
            super(AppDataContainerFactory, self).__setattr__(name, value)
        else:
            self[name] = copy(value)

    def __getattr__(self, name):
        if name.startswith('_') or self._app_registry.get_class(name, self._model) is None:
            raise AttributeError()
        return self[name]

    def __getitem__(self, name):
        class_ = self._app_registry.get_class(name, self._model)
        try:
            val = super(AppDataContainerFactory, self).__getitem__(name)
        except KeyError:
            if class_ is None:
                raise
            val = class_()
            self[name] = val
        else:
            if class_ is not None and not isinstance(val, class_):
                val = class_(val)
                self[name] = val

        return val

    def validate(self, model_instance):
        errors = {}
        for key, value in self.items():
            if hasattr(value, 'validate') and getattr(value, 'accessed', True):
                try:
                    value.validate(self, model_instance)
                except ValidationError, e:
                    errors[key] = e.message_dict
        if errors:
            raise ValidationError(errors)

    def serialize(self):
        for key, value in self.items():
            if hasattr(value, 'serialize') and getattr(value, 'accessed', True):
                super(AppDataContainerFactory, self).__setitem(key, value.serialize())
        return self

    def get(self, name, default=None):
        if name in self:
            return self[name]

        if default is None:
            return None

        class_ = self._app_registry.get_class(name, self._model)
        if class_ is not None and not isinstance(default, class_):
            return class_(default)

        return default

class AppDataForm(Form):
    def __init__(self, app_container, data=None, files=None, fields=(), exclude=(), **kwargs):
        self.app_container = app_container
        super(AppDataForm, self).__init__(data, files, **kwargs)

        if fields or exclude:
            for f in self.fields.keys():
                if fields and f not in fields:
                    del self.fields[f]
                elif f in exclude:
                    del self.fields[f]

    def save(self):
        self.app_container.update(self.cleaned_data)

class AppDataContainer(object):
    form_class = AppDataForm

    @classmethod
    def from_form(cls, form_class):
        return type('FormAppDataContainer', (cls, ), {'fields': {}, 'form_class': form_class})

    def __init__(self, *args, **kwargs):
        self._data = dict(*args, **kwargs)
        self._attr_cache = {}
        self.accessed = False

    def __eq__(self, other):
        if isinstance(other, AppDataContainer):
            #FIXME: _attr_cache
            return self._data == other._data
        elif isinstance(other, dict):
            return other == self._data
        return False

    @property
    def _form(self):
        if not hasattr(self, '_form_instance'):
            self._form_instance = self.get_form(self._data)
        return self._form_instance

    def __setitem__(self, name, value):
        self.accessed = True
        if name in self._form.fields:
            # store the original
            self._attr_cache[name] = value
        else:
            self._data[name] = value

    def __getitem__(self, name):
        self.accessed = True
        if name in self._form.fields and name in self._data:
            self._attr_cache[name] = self.form.cleaned_data[name]

        if name in self._attr_cache:
            return self._attr_cache[name]

        return self._data[name]

    def __delitem__(self, name):
        self.accessed = True
        if name in self._attr_cache:
            del self._attr_cache[name]
        del self._data[name]

    def validate(self, app_data, model_instance):
        self.serialize()
        form = self.get_form(self._data)
        if not form.is_valid():
            raise ValidationError(form.errors)

    def serialize(self):
        for name, value in self._attr_cache.iteritems():
            value = self.form.fields[name].widget._format_value(value)
            self._data[name] = value
        return self._data

    def get_form(self, data=None, files=None, fields=(), exclude=()):
        return self.form_class(self, data, files, fields=fields, exclude=exclude)
