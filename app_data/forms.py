try:
    from operator import methodcaller
except ImportError:
    methodcaller = lambda name: lambda o: getattr(o, name)()

from django.forms.forms import NON_FIELD_ERRORS, Form

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

    @property
    def instance(self):
        return self.app_container._instance

    def save(self):
        self.app_container.update(self.cleaned_data)

class BaseFieldsDescriptor(object):
    " Combines the base_fiels and prefixes them properly. Descriptor because needed on class level. "
    def __get__(self, instance, owner):

        if not hasattr(self, '_base_fields'):
            self._base_fields = bf = {}

            # construct an empty model to get to the data container and thus to the form classes
            app_container = getattr(owner.ModelForm._meta.model(), owner.app_data_field)

            # all the fields form model_form
            bf.update(owner.ModelForm.base_fields)

            # go through all the app forms...
            for label, opts in owner.get_app_form_opts().iteritems():
                Form = app_container[label].form_class
                exclude = set(opts.get('exclude', ()))
                fields = opts.get('fields', None)
                for name, field in Form.base_fields.iteritems():
                    # skip proper fields
                    if fields is not None and name not in fields:
                        continue
                    if name in exclude:
                        continue
                    # prefix the fields
                    bf['%s.%s' % (label, name)] = field

        return self._base_fields


class MultiForm(object):
    app_data_field = 'app_data'
    app_form_opts = {}

    def __init__(self, *args, **kwargs):
        # construct the main model form
        self.model_form = self.ModelForm(*args, **kwargs)
        if self.model_form.is_bound:
            data = self.model_form.data
            files = self.model_form.files
        else:
            data, files = None, None

        # construct all the app forms
        self.app_forms = {}
        app_container = getattr(self.model_form.instance, self.app_data_field)
        for label, label_opts in self.get_app_form_opts().iteritems():
            self.app_forms[label] = app_container[label].get_form(data, files, prefix=label, **label_opts)

    @classmethod
    def get_app_form_opts(cls):
        " Utility method to combinte app_form_opts from all base classes. "
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

    # properties delegated to model_form
    @property
    def media(self):
        return self.model_form.media

    @property
    def save_m2m(self):
        return self.model_form.save_m2m

    @property
    def is_bound(self):
        return self.model_form.is_bound

    # methods combining outputs from all forms
    base_fields = BaseFieldsDescriptor()

    def _get_all_forms(self):
        yield self.model_form
        for f in self.app_forms.itervalues():
            yield f

    def __unicode__(self):
        return self.as_table()

    def as_ul(self):
        return '\n'.join(map(methodcaller('as_ul'), self._get_all_forms()))

    def as_table(self):
        return '\n'.join(map(methodcaller('as_table'), self._get_all_forms()))

    def as_p(self):
        return '\n'.join(map(methodcaller('as_p'), self._get_all_forms()))

    def is_valid(self):
        return all(map(methodcaller('is_valid'), self._get_all_forms()))

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

    @property
    def changed_data(self):
        if not hasattr(self, '_changed_data'):
            self._changed_data = cd = self.model_form.changed_data[:]
            for label, form in self.app_forms.iteritems():
                cd.extend(map(lambda n: '%s.%s' % (label, n), form.changed_data))
        return self._changed_data

    @property
    def errors(self):
        # combine all the errors
        if not hasattr(self, '_errors'):
            self._errors = self.model_form.errors.copy()
            for label, form in self.app_forms.iteritems():
                for k, v in form.errors.iteritems():
                    if k == NON_FIELD_ERRORS:
                        self._errors.setdefault(k, self.model_form.error_class()).extend(v)
                    else:
                        self._errors['%s.%s' % (label, k)] = v
        return self._errors

    def non_field_errors(self):
        return self.errors.get(NON_FIELD_ERRORS, self.model_form.error_class())

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
