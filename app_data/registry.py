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
        for registry in (
            # use str for models to avoid import-time mess
            self._model_registry.get(model, {}),
            self._global_registry
            ):
            if namespace in registry:
                return registry[namespace]
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


