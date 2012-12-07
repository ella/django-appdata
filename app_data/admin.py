from django.contrib.admin.options import ModelAdmin, InlineModelAdmin

class AppDataModelAdmin(ModelAdmin):
    multiform = None

    def get_form(self, request, obj=None, **kwargs):
        if self.multiform:
            return self.multiform
        return super(AppDataModelAdmin, self).get_form(request, obj=None, **kwargs)


class AppDataInlineModelAdmin(InlineModelAdmin):
    multiform = None


class AppDataStackedInline(AppDataInlineModelAdmin):
    template = 'admin/edit_inline/stacked.html'

class AddDataTabularInline(AppDataInlineModelAdmin):
    template = 'admin/edit_inline/tabular.html'

