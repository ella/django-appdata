from operator import methodcaller

from django.forms.forms import BoundField, NON_FIELD_ERRORS, Form
from django.forms.widgets import media_property

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

class BaseFieldsDescriptor(object):
    def __get__(self, instance, owner):
        app_container = getattr(owner.ModelForm._meta.model(), owner.app_data_field)

        if not hasattr(self, '_base_fields'):
            self._base_fields = bf = {}
            bf.update(owner.ModelForm.base_fields)
            for label, opts in owner.get_app_form_opts().iteritems():
                Form = app_container[label].form_class
                exclude = set(opts.get('exclude', ()))
                fields = opts.get('fields', None)
                for name, field in Form.base_fields.iteritems():
                    if fields is not None and name not in fields:
                        continue
                    if name in exclude:
                        continue
                    bf['%s.%s' % (label, name)] = field

        return self._base_fields


class MultiForm(object):
    app_data_field = 'app_data'
    app_form_opts = {}
    def __init__(self, *args, **kwargs):
        self.model_form = self.ModelForm(*args, **kwargs)
        data = self.model_form.data
        files = self.model_form.files

        app_container = getattr(self.model_form.instance, self.app_data_field)

        self.app_forms = {}
        for label, label_opts in self.get_app_form_opts().iteritems():
            self.app_forms[label] = app_container[label].get_form(data, files, prefix=label, **label_opts)

    base_fields = BaseFieldsDescriptor()

    @property
    def media(self):
        return self.model_form.media

    @property
    def save_m2m(self):
        return self.model_form.save_m2m

    @property
    def is_bound(self):
        return self.model_form.is_bound

    @classmethod
    def get_app_form_opts(cls):
        # subclass may wish to remove superclass's app_form
        skip_labels = set()

        form_opts = {}
        # go through class hierarchy and collect form definitions
        for c in cls.mro():
            # not a MultiForm, skip
            if not hasattr(c, 'app_form_opts'):
                continue
            for label, label_opts in c.app_form_opts.iteritems():
                if label in form_opts or label in skip_labels:
                    # form already defined, or should be skipped
                    continue

                elif label_opts is None:
                    # mark as to-be-skipped
                    skip_labels.add(label)

                else:
                    # add form def
                    form_opts[label] = label_opts
        return form_opts

    @classmethod
    def add_form(cls, label, form_options={}):
        " Add an app_data form to the multi form after it's creation. "
        cls.app_form_opts[label] = form_options.copy()

    @classmethod
    def remove_form(cls, label):
        """
        Remove an app_data form to the multi form after it's creation.
        Even if this form would be specified in a superclass it would be skipped.
        """
        cls.app_form_opts[label] = None

    # TODO: mock other API of form like base_fields etc.
    def __getitem__(self, name):

        # provide access to app.field as well
        app = None
        if '.' in name:
            app, name = name.split('.', 1)

        if app is None:
            form = self.model_form
        else:
            try:
                form = self.app_forms[app]
            except KeyError:
                raise KeyError('AppForm %r not found in MultiForm.' % name)

        try:
            field = form[name]
        except KeyError:
            raise KeyError('Field %r not found in Form %s' % (name, form.fields))

        return field

    def is_valid(self):
        return self.model_form.is_valid() and all(map(methodcaller('is_valid'), self.app_forms.itervalues()))

    @property
    def errors(self):
        # combine all the errors
        _errors = self.model_form.errors.copy()
        for label, form in self.app_forms.iteritems():
            for k, v in form.errors.iteritems():
                if k == NON_FIELD_ERRORS:
                    _errors[k] = _errors.get(k, []).extend(v)
                else:
                    _errors['%s.%s' % (label, k)] = v
        return _errors

    def save(self, **kwargs):
        # save the app_data forms first
        for f in self.app_forms.values():
            f.save()
        # save the model itself
        return self.model_form.save(**kwargs)

def multiform_factory(model_form, base_class=MultiForm, app_data_field='app_data', name=None, **form_opts):
    name = name or '%sWithAppDataForm' % model_form._meta.model.__name__
    return type(
        name, (base_class, ),
        {'ModelForm': model_form, 'app_data_field': app_data_field, 'app_form_opts': form_opts}
    )
