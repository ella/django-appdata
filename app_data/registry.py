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

    def get_class(self, namespace, model):
        """
        Get class for namespace in given model
        """

        # go through the MRO looking for registered namespace to our model or it's parents
        for c in model.mro():
            if c in self._model_registry and namespace in self._model_registry[c]:
                return self._model_registry[c][namespace]

        # no namespace found for model or it's parents, try the global registry
        if namespace in self._global_registry:
            return self._global_registry[namespace]

        # fallback to default
        return self.default_class

    def register(self, namespace, class_, model=None, override=False):
        registry = self._model_registry.setdefault(model, {}) if model is not None else self._global_registry
        if namespace in registry and not override:
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


