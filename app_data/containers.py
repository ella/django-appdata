from copy import copy

from django.core.exceptions import ValidationError
from django.utils import six

from .registry import app_registry
from .forms import AppDataForm

class AppDataContainerFactory(dict):
    def __init__(self, model_instance, *args, **kwargs):
        self._model = model_instance.__class__
        self._instance = model_instance
        self._app_registry = kwargs.pop('app_registry', app_registry)
        super(AppDataContainerFactory, self).__init__(*args, **kwargs)

    def __repr__(self):
        return '<AppDataContainerFactory: %s>' % super(AppDataContainerFactory, self).__repr__()

    def __setattr__(self, name, value):
        if name.startswith('_') or self._app_registry.get_class(name, self._model) is None:
            super(AppDataContainerFactory, self).__setattr__(name, value)
        else:
            self[name] = copy(value)

    def __getattr__(self, name):
        if name.startswith('_') or self._app_registry.get_class(name, self._model) is None:
            raise AttributeError('No Container registered under %s for class %s' % (name, self._model.__name__))
        return self[name]

    def __getitem__(self, name):
        class_ = self._app_registry.get_class(name, self._model)
        try:
            val = super(AppDataContainerFactory, self).__getitem__(name)
        except KeyError:
            if class_ is None:
                raise
            val = class_(self._instance)
            self[name] = val
        else:
            if class_ is not None and not isinstance(val, class_):
                val = class_(self._instance, val)
                self[name] = val

        return val

    def __reduce__(self):
        return (dict, (self.serialize(), ))

    def validate(self, model_instance):
        errors = {}
        for key, value in six.iteritems(self):
            if hasattr(value, 'validate') and getattr(value, 'accessed', True):
                try:
                    value.validate(self, model_instance)
                except ValidationError as e:
                    errors[key] = e.message_dict
        if errors:
            raise ValidationError(errors)

    def serialize(self):
        for key, value in six.iteritems(self):
            if isinstance(value, AppDataContainer):
                value = value.serialize() if value.accessed else value._data
                super(AppDataContainerFactory, self).__setitem__(key, value)
        # return a copy so that it's a fresh dict, not AppDataContainerFactory
        return self.copy()

    def get(self, name, default=None):
        if name in self:
            return self[name]

        if default is None:
            return None

        class_ = self._app_registry.get_class(name, self._model)
        if class_ is not None and not isinstance(default, class_):
            return class_(self._instance, default)

        return default


INITIAL = object()

class AppDataContainer(object):
    form_class = AppDataForm

    @classmethod
    def from_form(cls, form_class):
        return type('%sAppDataContainer' % form_class.__name__, (cls, ), {'fields': {}, 'form_class': form_class})

    @property
    def accessed(self):
        " Return a boolean indicating whether the data have been accessed. "
        return self._accessed

    def __init__(self, model_instance, *args, **kwargs):
        self._data = dict(*args, **kwargs)
        self._attr_cache = {}
        self._accessed = False
        self._instance = model_instance

    def __repr__(self):
        return '<%s: %r>' % (self.__class__.__name__, self.serialize())

    def __eq__(self, other):
        if isinstance(other, AppDataContainer):
            return self.serialize() == other.serialize()
        elif isinstance(other, dict):
            return other == self.serialize()
        return False

    @property
    def _form(self):
        " Form instance used to clean/(de)serialize field values. "
        if not hasattr(self, '_form_instance'):
            self._form_instance = self.get_form()
        return self._form_instance

    def __setitem__(self, name, value):
        self._accessed = True
        # if dealing with defined field...
        if name in self._form.fields:
            # ..store the original - do not serialize, do not store in _data
            self._attr_cache[name] = value
        else:
            # fallback to behaving as normal dict otherwise
            self._data[name] = value

    def __setattr__(self, name, value):
        " Provide access to fields as attributes. "
        if name.startswith('_'):
            super(AppDataContainer, self).__setattr__(name, value)
        else:
            self.__setitem__(name, value)

    def __getitem__(self, name):
        self._accessed = True

        # defined field, still uncleaned, retrieve from self._form and put in cache
        if name in self._form.fields and name not in self._attr_cache:
            field = self._form.fields[name]
            # we want to invoke clean, even on initial values. otherwise it's
            # quite inelegant to work with collection types like lists, as
            # initial=[] will lead to a single list instance being used for all
            # instances.
            self._attr_cache[name] = field.clean(self._data.get(name, field.initial))

        # defined field stored in cache, return it
        if name in self._attr_cache:
            return self._attr_cache[name]

        return self._data[name]

    def __getattr__(self, name):
        " Provide access to fields as attributes. "
        if name.startswith('_'):
            raise AttributeError(name)
        try:
            return self.__getitem__(name)
        except KeyError:
            raise AttributeError(name)

    def __delitem__(self, name):
        self._accessed = True
        if name in self._attr_cache:
            del self._attr_cache[name]
        del self._data[name]

    def get(self, name, default=INITIAL):
        " Mimic dict's get with the exception of returning the inital value for defined fields "
        try:
            return self[name]
        except KeyError:
            if default is INITIAL:
                return None
            return default

    def update(self, data):
        for k, v in six.iteritems(data):
            self[k] = v

    def validate(self, app_data, model_instance):
        self.serialize()
        form = self.get_form(self._data)
        if not form.is_valid():
            raise ValidationError(form.errors)

    def serialize(self):
        " Go through attribute cache and use ._form to serialze those values into ._data. "
        for name, value in six.iteritems(self._attr_cache):
            f = self._form.fields[name]
            value = f.prepare_value(value)
            if hasattr(f.widget, '_format_value'):
                value = f.widget._format_value(value)
            self._data[name] = value
        return self._data

    def get_form(self, data=None, files=None, fields=(), exclude=(), form_class=None, **kwargs):
        " Contrsuct a form for this "
        form_class = form_class or self.form_class
        return form_class(self, data, files, fields=fields, exclude=exclude, initial=self.serialize(), **kwargs)
