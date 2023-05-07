Django AppData
##############

Extendable field and related tools that enable Django apps to extend your
reusable app.

Motivation
**********

When working with reusable django apps we often found that we needed to add
something extra to the model or form the app provided. Some apps try to solve
this by providing a flexible model definition and a pluggable form (see
``django.contrib.comments`` for an exmple of this approach) but even then it
leads to some duplication of efforts.

``django-appdata`` app tries, through ``AppDataField``, ``MultiForm`` and ``AppDataModelAdmin``,
to provide a standardised approach to extending existing apps.

Supported versions
******************

Python: 3.9, 3.10, 3.11
Django: 3.2, 4.2

Upgrading to 0.4
****************

If you are upgrading from a 0.3.x version, please note the following incompatible changes in 0.4

* Dropped Django < 3.2 and Python < 3.9 compatibility


Extending Models
****************

When you have an extendable django app using the ``AppDataField``::

    from django.db import models
    from app_data import AppDataField

    class BlogPost(models.Model):
        text = models.TextField()
        app_data = AppDataField()

your code can register a namespace on any (or all) ``AppDataField`` and store
it's own data there by registering a *container* (subclass of
``AppDataContainer``). To define the data you use django's form framework::

    from django.forms.models import ModelMultipleChoiceField
    from app_data import app_registry, AppDataForm, AppDataContainer

    from .models import Tag

    class TaggingAppDataForm(AppDataForm):
        public_tags = ModelMultipleChoiceField(Tag.objects.all())
        admin_tags = ModelMultipleChoiceField(Tag.objects.all())

    class TaggingAppDataContainer(AppDataContainer):
        form_class = TaggingAppDataForm

        def tag_string(self):
            print ', '.join(t.name for t in self.public_tags)

    app_registry.register('tagging', TaggingAppDataContainer)

This should give you access to ``'tagging'`` namespace in any defined ``AppDataField``::

    from blog_app.models import BlogPost

    bp = BlogPost()
    assert bp.app_data.tagging.tag_string() == ""


Additional Options
~~~~~~~~~~~~~~~~~~

Note that if you don't need to add custom methods to your container you can
just use a factory to create the subclass::

    app_registry.register('tagging', AppDataContainer.from_form(TaggingAppDataForm))

Additionaly you can restrict the registration to a given model::

    from blog_app.models import BlogPost

    app_registry.register('tagging', TaggingAppDataContainer, BlogPost)

Extending Forms
***************

``django-appdata`` supplies a ``MultiForm`` class - a wrapper around django's ``ModelForm``
with optional added sub-forms that corresponds to namespaces registered in the
model's ``AppDataField``, typically the extendable app would create and use a
``MultiForm`` instead of a regular ``ModelForm``::

    from app_data.forms import multiform_factory
    from .models import BlogPost

    BlogPostMultiForm = multiform_factory(BlogPost)

And when using that app any project can add additional sub-forms to that ``MultiForm``::

    from blog_app.forms import BlogPostMultiForm

    BlogPostMultiForm.add_form('tagging', {'fields': ['public_tags']})

This way when the reusable app's code can remain unchanged and we can inject
additional form logic to its processing.

Additional Options
~~~~~~~~~~~~~~~~~~

Any arguments and keyword arguments are passed without change to the
``ModelForm`` class the ``MultiForm`` is wrapping so even if you have custom args
for your ``ModelForm`` everything will still work::

    from django.forms.models import BaseModelForm

    class ModelFormWithUser(ModelForm):
        def __init__(self, user, *args, **kwargs):
            self.user = user
            super(ModelFormWithUser, self).__init__(*args, **kwargs)

    BlogPostMultiForm = multiform_factory(BlogPost, form=ModelFormWithUser)

And of course you are not limited to the use of a factory function::

    from app_data import MultiForm

    class MyMultiForm(MultiForm):
        ModelForm = BlogPostModelForm

MultiForms in Admin
*******************

If you wish to add your own code to the admin interface, just use
``AppDataModelAdmin``::

    from django.contrib import admin
    from app_data.admin import AppDataModelAdmin
    from blog_app.models import BlogPost

    class BlogPostAdmin(AppDataModelAdmin):
        # due to the behavior of django admin validation we need to use
        # get_fieldsets instead of just fieldsets
        def get_fieldsets(self, request, obj=None):
             return [
                 (None, {'fields': ['text', ]}),
                 ('Tagging', {'fields': [('tagging.public_tags', 'tagging.admin_tags')]})
             ]
    admin.site.register(BlogPost, BlogPostAdmin)

Additional Options
~~~~~~~~~~~~~~~~~~

As with django's admin and forms you can supply your own ``MultiForm`` class by
using the ``multiform`` attribute of ``AppDataModelAdmin``.

Behind the scenes
*****************

``django-appdata`` uses a ``TextField`` to store the data on the model using JSON
and django's forms framework for (de)serialization and validation of the data.

When accessing the containers in the field we will try to locate the
appropriate container in the registry. If none is found, plain data will be
returned if present (dict). To assure everything working properly we recommend
putting some sort of init code in place for your project that will make sure all
the registration is done before any actual code is run. We are using a module
called ``register`` in our apps and then a `piece of code`_ similar to admin's
autodiscover to iterate through installed apps and load this module.

.. _`piece of code`: https://github.com/ella/ella/blob/master/ella/utils/installedapps.py#L27

Build status
************

:Master branch:

  .. image:: https://secure.travis-ci.org/ella/django-appdata.png?branch=master
     :alt: Travis CI - Distributed build platform for the open source community
     :target: http://travis-ci.org/#!/ella/django-appdata
