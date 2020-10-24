from functools import partial

from django.contrib.admin.utils import flatten_fieldsets
from django.contrib.admin.options import ModelAdmin, InlineModelAdmin
from django import forms
from django.forms.models import modelform_defines_fields

from app_data.forms import multiform_factory, multiinlineformset_factory, MultiForm, AppDataBaseInlineFormSet


class AppDataAdminMixin(object):

    multiform = MultiForm
    app_form_opts = {}

    def get_fieldsets(self, request, obj=None):
        try:
            return self.declared_fieldsets
        except AttributeError:
            return super(AppDataAdminMixin, self).get_fieldsets(request, obj)

    def _get_form_factory_opts(self, request, obj=None, **kwargs):
        fieldsets = self.get_fieldsets(request, obj)
        if fieldsets:
            fields = flatten_fieldsets(fieldsets)
        else:
            fields = None
        if self.exclude is None:
            exclude = []
        else:
            exclude = list(self.exclude)
        exclude.extend(self.get_readonly_fields(request, obj))
        if self.exclude is None and hasattr(self.form, '_meta') and self.form._meta.exclude:
            # Take the custom ModelForm's Meta.exclude into account only if the
            # ModelAdmin doesn't define its own.
            exclude.extend(self.form._meta.exclude)

        # construct the form_opts from declared_fieldsets
        form_opts = self.app_form_opts.copy()
        if fields is not None:
            # put app_name prefixed fields into form_opts
            for f in fields:
                if '.' not in f:
                    continue
                label, name = f.split('.')
                app_fields = form_opts.setdefault(label, {}).setdefault('fields', [])
                if name not in app_fields:
                    app_fields.append(name)
            # .. and remove them from fields for the model form
            fields = [f for f in fields if '.' not in f]

        # do the same for exclude
        for f in exclude:
            if '.' not in f:
                continue
            label, name = f.split('.')
            app_fields = form_opts.setdefault(label, {}).setdefault('exclude', [])
            if name not in app_fields:
                app_fields.append(name)
        exclude = [f for f in exclude if '.' not in f]

        # Django 3.1 always adds the fields attribute to the kwargs
        # and we must remove appdata fields from this list
        kwargs["fields"] = [f for f in fields if '.' not in kwargs.get("fields", [])]

        # if exclude is an empty list we pass None to be consistant with the
        # default on modelform_factory
        exclude = exclude or None
        defaults = {
            "form": self.form,
            "multiform": self.multiform,
            "form_opts": form_opts,
            "fields": fields,
            "exclude": exclude,
            "formfield_callback": partial(self.formfield_for_dbfield, request=request),
        }
        defaults.update(kwargs)

        if hasattr(forms, 'ALL_FIELDS'):
            # Django 1.7
            if defaults['fields'] is None and not modelform_defines_fields(defaults['form']):
                defaults['fields'] = forms.ALL_FIELDS

        return defaults


class AppDataModelAdmin(AppDataAdminMixin, ModelAdmin):
    def get_form(self, request, obj=None, change=False, **kwargs):
        """
        Returns a Form class for use in the admin add view. This is used by
        add_view and change_view.
        """
        if self.multiform is None:
            return super(AppDataModelAdmin, self).get_form(request, obj=obj, **kwargs)
        return multiform_factory(self.model, **self._get_form_factory_opts(request, obj, **kwargs))


class AppDataInlineModelAdmin(AppDataAdminMixin, InlineModelAdmin):
    formset = AppDataBaseInlineFormSet

    def get_formset(self, request, obj=None, **kwargs):
        if self.multiform is None:
            return super(AppDataInlineModelAdmin, self).get_formset(request, obj=obj, **kwargs)
        can_delete = self.can_delete
        if hasattr(self, 'has_delete_permission'):
            can_delete = can_delete and self.has_delete_permission(request, obj)
        defaults = {
            "formset": self.formset,
            "fk_name": self.fk_name,
            "extra": self.extra,
            "max_num": self.max_num,
            "can_delete": can_delete,
        }
        defaults.update(self._get_form_factory_opts(request, obj, **kwargs))
        return multiinlineformset_factory(self.parent_model, self.model, **defaults)


class AppDataStackedInline(AppDataInlineModelAdmin):
    template = 'admin/edit_inline/stacked.html'


class AppDataTabularInline(AppDataInlineModelAdmin):
    template = 'admin/edit_inline/tabular.html'

