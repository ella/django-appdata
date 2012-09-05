from operator import methodcaller

from django.forms.forms import BoundField, NON_FIELD_ERRORS

class MultiForm(object):
    def __init__(self, data=None, files=None, **kwargs):
        self.model_form = self.ModelForm(data, files, **kwargs)

        app_container = getattr(self.model_form.instance, self.app_data_field)

        self.app_forms = {}
        for label, opts in self.app_form_opts.iteritems():
            self.app_forms[label] = app_container[label].get_form(data, files, prefix=label,  **opts)

    def __getitem__(self, name):
        app = None
        if '.' in name:
            app, field = name.split('.', 1)

        if app is None:
            form = self.model_form
        else:
            try:
                form = self.app_forms[app]
            except KeyError:
                raise KeyError('AppForm %r not found in MultiForm.' % name)

        try:
            field = form[field]
        except KeyError:
            raise KeyError('Field %r not found in Form %s' % (name, form))

        return BoundField(form, field, name)

    def is_valid(self):
        return self.model_form.is_valid() and all(map(methodcaller('is_valid'), self.app_forms.itervalues()))

    @property
    def errors(self):
        _errors = self.model_form.errors.copy()
        for label, form in self.app_forms.iteritems():
            for k, v in form.errors.iteritems():
                if k == NON_FIELD_ERRORS:
                    _errors[k] = _errors.get(k, []).extend(v)
                else:
                    _errors['%s.%s' % (label, k)] = v
        return _errors

    def save(self, **kwargs):
        for f in self.app_forms.values():
            f.save()
        return self.model_form.save(**kwargs)

def multiform_factory(model_form, app_data_field='app_data', **form_opts):
    return type(
        '%sWithAppDataForm' % model_form._meta.model.__name__,
        (MultiForm, ),
        {'ModelForm': model_form, 'app_data_field': app_data_field, 'app_form_opts': form_opts}
    )
