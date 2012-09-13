from django.contrib.admin import ModelAdmin

class AppDataModelAdmin(ModelAdmin):
    multiform = None

    def get_form(self, request, obj=None, **kwargs):
        if self.multiform:
            return self.multiform
        return super(AppDataModelAdmin, self).get_form(request, obj=None, **kwargs)
