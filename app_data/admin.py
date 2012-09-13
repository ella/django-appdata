from django.contrib.admin import ModelAdmin

from app_data import MultiForm

class AppDataModelAdmin(ModelAdmin):
    def get_form(self, request, obj=None, **kwargs):
        if isinstance(self.form, MultiForm):
            return self.multiform
        return super(AppDataModelAdmin, self).get_form(request, obj=None, **kwargs)
