from copy import deepcopy
from operator import methodcaller

from django.forms.forms import NON_FIELD_ERRORS, Form
from django.forms.formsets import formset_factory
from django.forms.models import BaseInlineFormSet, BaseModelFormSet, _get_foreign_key, modelform_factory
from django.forms.utils import pretty_name
from django.utils.safestring import mark_safe


class AppDataForm(Form):
    def __init__(self, app_container, data=None, files=None, fields=(), exclude=(), *args, **kwargs):
        self.app_container = app_container
        super().__init__(data, files, *args, **kwargs)

        if fields or exclude:
            for f in list(self.fields.keys()):
                if fields and f not in fields:
                    del self.fields[f]
                elif f in exclude:
                    del self.fields[f]

    @property
    def instance(self):
        return self.app_container._instance

    def save(self):
        self.app_container.update(self.cleaned_data)


class BaseFieldsDescriptor:
    """Combines the base_fields and prefixes them properly. Descriptor because needed on class level."""

    def __get__(self, instance, owner):
        if not hasattr(self, "_base_fields"):
            self._base_fields = bf = {}

            # construct an empty model to get to the data container and thus to the form classes
            app_container = getattr(owner.ModelForm._meta.model(), owner.app_data_field)

            # all the fields form model_form
            bf.update(owner.ModelForm.base_fields)

            # go through all the app forms...
            for label, opts in owner.get_app_form_opts().items():
                Form = app_container[label].form_class  # noqa: N806
                exclude = set(opts.get("exclude", ()))
                fields = opts.get("fields", None)
                for name, field in Form.base_fields.items():
                    # skip proper fields
                    if fields is not None and name not in fields:
                        continue
                    if name in exclude:
                        continue
                    # prefix the fields
                    bf["{}.{}".format(label, name)] = field

        return self._base_fields


class AppFormOptsDescriptor:
    def __get__(self, instance, owner):
        # we cannot check hasattr because parent's app_form_opts would pick it up
        if "_app_form_opts" not in owner.__dict__:
            owner._app_form_opts = {}
        return owner._app_form_opts


class MultiFormMetaclass(type):
    # This property is needed by BaseInlineFormSet which expect the form *class* to have a "real" _meta
    # and thus the proxing in the instance property won't work
    @property
    def _meta(cls):
        return cls.ModelForm._meta


class MultiForm(metaclass=MultiFormMetaclass):
    app_data_field = "app_data"
    app_form_opts = AppFormOptsDescriptor()

    def __init__(self, *args, **kwargs):
        # construct the main model form
        self.model_form = self.ModelForm(*args, **kwargs)
        try:
            self.label_suffix = self.model_form.label_suffix
        except AttributeError:
            pass
        if self.model_form.is_bound:
            data = self.model_form.data
            files = self.model_form.files
        else:
            data, files = None, None

        # construct all the app forms
        self.app_forms = {}
        app_container = getattr(self.model_form.instance, self.app_data_field)
        for label, label_opts in self.get_app_form_opts().items():
            prefix = label
            if self.model_form.prefix:
                prefix = "{}-{}".format(self.model_form.prefix, prefix)
            self.app_forms[label] = app_container[label].get_form(data, files, prefix=prefix, **label_opts)

    @classmethod
    def get_app_form_opts(cls):
        """Utility method to combine app_form_opts from all base classes."""
        # subclass may wish to remove superclass's app_form
        skip_labels = set()

        form_opts = {}
        # go through class hierarchy and collect form definitions
        for c in cls.mro():
            # not a MultiForm, skip
            if not hasattr(c, "app_form_opts"):
                continue
            for label, label_opts in c.app_form_opts.items():
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
    def add_form(cls, label, form_options=None):
        """Add an app_data form to the multi form after its creation."""
        form_options = form_options or {}
        cls.app_form_opts[label] = form_options.copy()

    @classmethod
    def remove_form(cls, label):
        """
        Remove an app_data form to the multi form after its creation.
        Even if this form would be specified in a superclass it would be skipped.
        """
        cls.app_form_opts[label] = None

    # properties delegated to model_form
    @property
    def _get_validation_exclusions(self):
        return self.model_form._get_validation_exclusions

    @property
    def cleaned_data(self):
        return self.model_form.cleaned_data

    @property
    def is_multipart(self):
        return self.model_form.is_multipart

    @property
    def _meta(self):
        # user by BaseInlineFormSet.add_fields
        return self.model_form._meta

    @property
    def fields(self):
        # user by BaseModelFormSet.add_fields
        return self.model_form.fields

    @property
    def _raw_value(self):
        # used by FormSet._should_delete_form
        return self.model_form._raw_value

    @property
    def instance(self):
        return self.model_form.instance

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
        yield from self.app_forms.values()

    def __unicode__(self):
        return self.as_table()

    def as_ul(self):
        return mark_safe("\n".join(map(methodcaller("as_ul"), self._get_all_forms())))

    def as_table(self):
        return mark_safe("\n".join(map(methodcaller("as_table"), self._get_all_forms())))

    def as_p(self):
        return mark_safe("\n".join(map(methodcaller("as_p"), self._get_all_forms())))

    def is_valid(self):
        return all(map(methodcaller("is_valid"), self._get_all_forms()))

    def has_changed(self):
        return any(map(methodcaller("has_changed"), self._get_all_forms()))

    def __getitem__(self, name):
        # provide access to app.field as well
        app = None
        if "." in name:
            app, name = name.split(".", 1)

        if app is None:
            form = self.model_form
        else:
            try:
                form = self.app_forms[app]
            except KeyError:
                raise KeyError("AppForm %r not found in MultiForm." % name)

        try:
            field = form[name]
        except KeyError:
            raise KeyError("Field {!r} not found in Form {}".format(name, form.fields))

        return field

    @property
    def changed_data(self):
        if not hasattr(self, "_changed_data"):
            self._changed_data = cd = self.model_form.changed_data[:]
            for label, form in self.app_forms.items():
                cd.extend(map(lambda n: "{}.{}".format(label, n), form.changed_data))  # noqa: B023, C417
        return self._changed_data

    @property
    def errors(self):
        # combine all the errors
        if not hasattr(self, "_errors"):
            self._errors = self.model_form.errors.copy()
            for label, form in self.app_forms.items():
                for k, v in form.errors.items():
                    if k == NON_FIELD_ERRORS:
                        self._errors.setdefault(k, self.model_form.error_class()).extend(v)
                    else:
                        self._errors["{}.{}".format(label, k)] = v
        return self._errors

    def non_field_errors(self):
        return self.errors.get(NON_FIELD_ERRORS, self.model_form.error_class())

    def save(self, **kwargs):
        # save the app_data forms first
        for f in self.app_forms.values():
            f.save()
        # save the model itself
        return self.model_form.save(**kwargs)


class AppDataBaseInlineFormSet(BaseInlineFormSet):
    def add_fields(self, form, index):
        """appcontainer fields are no longer added to the empty form, we can inject them hooking here."""
        super().add_fields(form, index)
        for name, field in form.base_fields.items():
            if name not in form.fields:
                form.fields[name] = deepcopy(field)
                if not form.fields[name].label:
                    form.fields[name].label = pretty_name(name.split(".")[1])


def multiform_factory(model, multiform=MultiForm, app_data_field="app_data", name=None, form_opts=None, **kwargs):
    form_opts = form_opts or {}
    model_form = modelform_factory(model, **kwargs)
    name = name or "%sWithAppDataForm" % model_form._meta.model.__name__
    return type(
        name,
        (multiform,),
        {
            "ModelForm": model_form,
            "app_data_field": app_data_field,
            "_app_form_opts": form_opts,
        },
    )


def multiformset_factory(
    model,
    multiform=MultiForm,
    app_data_field="app_data",
    name=None,
    form_opts=None,
    formset=BaseModelFormSet,
    extra=3,
    can_order=False,
    can_delete=True,
    max_num=None,
    **kwargs,
):
    form_opts = form_opts or {}
    multiform = multiform_factory(model, multiform, app_data_field, name, form_opts, **kwargs)
    FormSet = formset_factory(  # noqa: N806
        multiform,
        formset=formset,
        extra=extra,
        can_order=can_order,
        can_delete=can_delete,
        max_num=max_num,
    )
    FormSet.model = model
    return FormSet


def multiinlineformset_factory(
    parent_model,
    model,
    multiform=MultiForm,
    app_data_field="app_data",
    name=None,
    form_opts=None,
    formset=BaseInlineFormSet,
    fk_name=None,
    **kwargs,
):
    form_opts = form_opts or {}
    fk = _get_foreign_key(parent_model, model, fk_name=fk_name)
    if fk.unique:
        kwargs["max_num"] = 1
    FormSet = multiformset_factory(  # noqa: N806
        model,
        multiform,
        app_data_field,
        name,
        form_opts,
        formset=formset,
        **kwargs,
    )  # noqa: N806
    FormSet.fk = fk
    return FormSet
