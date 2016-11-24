import sys
from django.db import models
from adminpp.builder import AdminBuilder
from adminpp.renderers import BasicFieldRenderer
from adminpp.tags import Tag, VoidTag


class optional:
    pass


class auto:
    pass


default_renderer = BasicFieldRenderer()


class BaseField(object):
    name = None  # name of the field (at AdminModel)
    model = None

    def __init__(self,
                 list_display=True,
                 renderer=None,
                 short_description=None,
                 source=None):
        self.list_display = list_display

        # Set property objects
        self._renderer = renderer
        self._short_description = short_description
        self._source = source

    def bind(self, name, admin_model):
        self.name = name
        self.admin_model = admin_model
        self.model = admin_model.Meta.model

    @property
    def renderer(self):
        if self._renderer is None:
            self._renderer = default_renderer
        return self._renderer

    @property
    def short_description(self):
        if self._short_description is not None:
            return self._short_description
        return self.name

    @property
    def source(self):
        if self._source is not None:
            return self._source
        return self.name

    @property
    def admin_order_field(self):
        try:
            self.model._meta.get_field(self.source)
            return self.source
        except:
            return None

    def get_value(self, obj):
        return getattr(obj, self.source)

    def render(self, value):
        return self.renderer.render_text(value)


class CharField(BaseField):
    pass


class IntegerField(BaseField):
    pass


class BaseTagField(BaseField):
    pass


class BooleanField(BaseTagField):
    def render(self, value):
        return self.renderer.render_boolean(value)


class MethodField(BaseField):
    def __init__(self, method_name=None, **kwargs):
        self._method_name = method_name
        super(MethodField, self).__init__(**kwargs)

    @property
    def method_name(self):
        if self._method_name is not None:
            return self._method_name
        return 'get_{}'.format(self.name)

    def get_value(self, obj):
        method = getattr(self.admin_model, self.method_name)
        return method(obj)


class ImageField(BaseTagField):
    def render(self, value):
        tag = VoidTag('img', src=value)
        return self.renderer.render_text(tag)


class DateTimeField(BaseField):
    def render(self, value):
        return str(value)


class AdminModel(object):
    Meta = None

    field_mapping = {
        models.AutoField: IntegerField,
        models.BooleanField: BooleanField,
        models.CharField: CharField,
        models.DateTimeField: DateTimeField,
        models.ImageField: ImageField,
        models.TextField: CharField,
    }

    def get_fields(self):
        fields = []
        # Get pk field
        model = self.Meta.model
        field_object = IntegerField()
        field_object.bind(model._meta.pk.name, self)
        fields.append(field_object)
        # Get all fields declared at ModelAdmin class
        for attr_name in dir(self):
            attr = getattr(self, attr_name, None)
            if isinstance(attr, BaseField):
                field_object = attr
                # Bind "name" and "admin_model" info into field object
                field_object.bind(attr_name, self)
                # Append to result array
                fields.append(field_object)
        return fields

    def get_queryset(self):
        return self.Meta.model._default_manager.get_queryset()


class AutoAdminModel(AdminModel):
    def get_fields(self):
        model = self.Meta.model



def create_proxy_model(model, proxy_name):
    # This function call should be bypassed under migration commands
    # because proxy model creates dummy migration files.
    # (Not very clever, but it works)
    if 'makemigrations' in sys.argv or 'migrate' in sys.argv:
        return model

    # http://stackoverflow.com/questions/2223375/multiple-modeladmins-views-for-same-model-in-django-admin
    class Meta:
        proxy = True
        app_label = model._meta.app_label

    attrs = {'__module__': '', 'Meta': Meta}
    proxy_model = type(proxy_name, (model,), attrs)
    return proxy_model


def adminpp_register(site, admin_model):
    admin_class = AdminBuilder(admin_model).build()
    model = admin_model.Meta.model

    # If Meta has proxy_name, use proxy model instead
    proxy_name = getattr(admin_model.Meta, 'proxy_name', None)
    if proxy_name is not None:
        model = create_proxy_model(model, proxy_name)

    site.register(model, admin_class)
