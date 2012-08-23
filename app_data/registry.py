from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.utils.importlib import import_module

def _import_module_member(modstr):
    module, attr = modstr.rsplit('.', 1)
    try:
        mod = import_module(module)
    except ImportError, e:
        raise ImproperlyConfigured('Error importing AppDataContainer %s: "%s"' % (modstr, e))
    try:
        member = getattr(mod, attr)
    except AttributeError, e:
        raise ImproperlyConfigured('Error importing AppDataContainer %s: "%s"' % (modstr, e))
    return member


class NamespaceConflict(Exception):
    pass


class NamespaceMissing(KeyError):
    pass


class NamespaceRegistry(object):
    """
    Global registry of app_specific storage classes in app_data field
    """
    def __init__(self, default_class=None):
        self.default_class = default_class
        self._reset()

    def _reset(self):
        # stuff registered by apps
        self._global_registry = {}
        self._model_registry = {}

        self._global_overrides = {}
        self._model_overrides = {}
        # overrides from settings
        for key, value in getattr(settings, 'APP_DATA_CLASSES', {}).iteritems():
            if key == 'global':
                self._global_overrides.update(value)
            else:
                # use str for models to avoid import-time mess
                self._model_overrides[key] = value.copy()

        for d in [self._global_overrides] + self._model_overrides.values():
            for k in d:
                d[k] = _import_module_member(d[k])

    def get_class(self, namespace, model):
        """
        Get class for namespace in given model, look into overrides first and
        then into registered classes.
        """
        for registry in (
            # use str for models to avoid import-time mess
            self._model_overrides.get(str(model._meta), {}),
            self._global_overrides,
            self._model_registry.get(model, {}),
            self._global_registry
            ):
            if namespace in registry:
                return registry[namespace]
        return self.default_class

    def register(self, namespace, class_, model=None):
        registry = self._model_registry.setdefault(model, {}) if model is not None else self._global_registry
        if namespace in registry:
            raise NamespaceConflict(
                'Namespace %r already assigned to class %r%s.' % (
                    namespace,
                    registry[namespace],
                    '' if model is None else ' for model %s' % model._meta
                )
            )
        registry[namespace] = class_

    def unregister(self, namespace, model=None):
        registry = self._model_registry.setdefault(model, {}) if model is not None else self._global_registry
        if namespace not in registry:
            raise NamespaceMissing(
                'Namespace %r is not registered yet.' % namespace)

        del registry[namespace]

app_registry = NamespaceRegistry()


