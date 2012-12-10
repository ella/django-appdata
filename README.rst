Django AppData
##############

Extandable field and related tools that enable Django apps to extend your
reusable app.

Motivation
**********

When working with reusable django apps we often found that we needed to add
something extra to the model or form the app provided. Some apps try to solve
this by providing a flexible model definition and a pluggable form (see
`django.contrib.comments` for an exmple of this approach) but even then it
leads to some duplication of efforts.

`django-appdata` app tries, through `AppDataField`, `MultiForm` and `AppDataModelAdmin`,
to provide a standardised approach to extending existing apps.

Extending Models
****************

Your code can register a namespace on any (or all) `AppDataField` and store
it's own data there:

    from django.forms.models import ModelMultipleChoiceField
    from app_data import app_registry, AppDataForm, AppDataContainer

    from .models import Tag

    class TaggingAppDataForm(AppDataForm):
        public_tags = ModelMultipleChoiceField(Tag.objects.all())
        admin_tags = ModelMultipleChoiceField(Tag.objects.all())
    app_registry.register('tagging', AppDataContainer.from_form(TaggingAppDataForm))

This should give you access to `'tagging'` namespace in any defined `AppDataField`:

    from django.db import models
    from app_data import AppDataField

    class BlogPost(models.Model):
        text = models.TextField()
        app_data = AppDataField()

    bp = BlogPost()
    assert bp.app_data.tagging.public_tags == []

Extending Forms
***************

`django-appdata` supplies a `MultiForm` class - a wrapper around django's `ModelForm`
with optional added sub-forms that corresponds to namespaces registered in the
model's `AppDataField`, typically the extendable app would create and use a
`MultiForm` instead of a regular `ModelForm`:

    from app_data.forms import multiform_factory
    from .models import BlogPost

    BlogPostMultiForm = multiform_factory(BlogPost)

And when using that app any project can add additional sub-forms to that `MultiForm`:

    from blog_app.forms import BlogPostMultiForm

    BlogPostMultiForm.add_form('tagging', {'fields': ['public_tags']})

This way when the reusable app's code can remain unchanged and we can inject
additional form logic to it's processing.

MultiForms in Admin
*******************

If you wish to add your own code to the admin interface, just use
`AppDataModelAdmin`:

    from django.contrib import admin
    from app_data.admin import AppDataModelAdmin
    from blog_app.models import BlogPost

    class BlogPostAdmin(AppDataModelAdmin):
        # due to bug in django's admin validation we need to use
        # declared_fieldsets instead of just fieldsets
        declared_fieldsets = [
            (None, {'fields': ['text', ]}),
            ('Tagging': {'fields': [('tagging.public_tags', 'tagging.admin_tags')]})
        ]

Behind the scenes
*****************

`django-appdata` uses a `TextField` to store the data on the model using JSON
and django's forms framework for (de)serialization and validation of the data.

Build status
************

:Master branch:

  .. image:: https://secure.travis-ci.org/ella/django-appdata.png?branch=master
     :alt: Travis CI - Distributed build platform for the open source community
     :target: http://travis-ci.org/#!/ella/django-appdata

