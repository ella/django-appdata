from django.contrib.admin import ModelAdmin

from .forms import multiform_factory

class AppDataModelAdmin(ModelAdmin):
    app_data_field = 'app_data'
    app_data = {}

    def get_form(self, request, obj=None, **kwargs):
        ModelForm = super(AppDataModelAdmin, self).get_form(request, obj, **kwargs)
        return multiform_factory(ModelForm, app_data_field=self.app_data_field, **self.app_data)
