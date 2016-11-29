from django.contrib import admin


# http://stackoverflow.com/questions/17392087/how-to-modify-django-admin-filters-title
def get_titled_filter(title, base_class=admin.FieldListFilter):
    class Wrapper(base_class):
        def __new__(cls, *args, **kwargs):
            instance = admin.FieldListFilter.create(*args, **kwargs)
            instance.title = title
            return instance
    return Wrapper
