import sys
from django.db import models
from adminpp.builder import AdminBuilder
from adminpp.renderers import get_default_renderer
from adminpp.tags import Tag, VoidTag


class optional:
    pass


class auto:
    pass


class BaseField(object):
    name = None  # name of the field (at AdminModel)
    model = None

    def __init__(self,
                 list_display=True,
                 renderer=None,
                 short_description=None,
                 source=None,
                 **kwargs):
        self.list_display = list_display

        # Set property objects
        self._renderer = renderer
        self._short_description = short_description
        self._source = source

        self.kwargs = kwargs

    def bind(self, name, admin_model):
        self.name = name
        self.admin_model = admin_model
        self.model = admin_model.Meta.model

    @property
    def renderer(self):
        if self._renderer is None:
            self._renderer = get_default_renderer()
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
        allow_tags = self.kwargs.get('allow_tags', False)
        return self.renderer.render_text(value, allow_tags=allow_tags)


class CharField(BaseField):
    pass


class IntegerField(BaseField):
    pass


class BooleanField(BaseField):
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


class ImageField(BaseField):
    def render(self, value):
        tag = VoidTag('img', src=value, **self.kwargs)
        return self.renderer.render_text(tag, allow_tags=True)


class DateTimeField(BaseField):
    def render(self, value):
        return self.renderer.render_datetime(value)


class AdminModelMeta(type):
    """
    This metaclass will make AdminModel.Meta inherit all variables from parent.
    Reference code for metaclass:
     https://github.com/django/django/blob/1.10.3/django/db/models/base.py#L82
    """

    def __new__(cls, name, bases, attrs):
        super_new = super(AdminModelMeta, cls).__new__

        # Also ensure initialization is only performed for subclasses of AdminModel
        # (excluding AdminModel class itself)
        parents = [b for b in bases if isinstance(b, AdminModelMeta)]
        if not parents:
            return super_new(cls, name, bases, attrs)

        if 'Meta' not in attrs:
            raise RuntimeError("'class Meta' must be defined at ({})".format(name))

        # Create the class
        new_class = super_new(cls, name, bases, attrs)
        new_meta = attrs.pop('Meta', None)

        # Construct Meta
        parent_class = filter(lambda c: issubclass(c, AdminModel), bases)[0]
        parent_meta = parent_class.Meta
        for attr_name in dir(parent_meta):
            # If parent.Meta has attributes that new.Meta doesn't have,
            # append it to new.Meta
            if attr_name not in dir(new_meta):
                setattr(new_meta, attr_name, getattr(parent_meta, attr_name))

        return new_class


class AdminModel(object):
    __metaclass__ = AdminModelMeta

    field_mapping = {
        models.AutoField: IntegerField,
        models.BooleanField: BooleanField,
        models.CharField: CharField,
        models.DateTimeField: DateTimeField,
        models.ImageField: ImageField,
        models.TextField: CharField,
    }

    class Meta:
        list_display = auto

    predefined_meta_fields = [
        'model',
        'list_display',
        'proxy_name',
    ]

    def get_mapped_field(self, model_field):
        # Given django.Model field, find appropriate admin_models.Field class
        if model_field.__class__ in self.field_mapping:
            return self.field_mapping[model_field.__class__]
        # Return CharField by default
        return CharField

    def get_field_names(self):
        if self.Meta.list_display == auto:
            # Get list_display from model
            model_fields = self.Meta.model._meta.fields
            return [f.name for f in model_fields]
        else:
            # Get list_display from Meta
            return self.Meta.list_display

    def get_fields(self):
        fields = []
        for field_name in self.get_field_names():
            if hasattr(self, field_name):
                # Get field defined at ModelAdmin
                field = getattr(self, field_name)
            else:
                # Create field from Model.field
                model_field = self.Meta.model._meta.get_field(field_name)
                field_class = self.get_mapped_field(model_field)
                field = field_class()
            # Bind "name" and "admin_model" info into field object
            field.bind(field_name, self)
            # Append to result array
            fields.append(field)
        return fields

    def get_queryset(self):
        return self.Meta.model._default_manager.get_queryset()


def create_proxy_model(model, proxy_name):
    # http://stackoverflow.com/questions/2223375/multiple-modeladmins-views-for-same-model-in-django-admin
    class Meta:
        proxy = True
        app_label = model._meta.app_label

    attrs = {'__module__': '', 'Meta': Meta}
    proxy_model = type(proxy_name, (model,), attrs)
    return proxy_model


def register(site, admin_model):
    # This function call should be bypassed under migration commands
    # because proxy model creates dummy migration files.
    # (Not very clever, but it works)
    if 'makemigrations' in sys.argv or 'migrate' in sys.argv:
        return

    admin_class = AdminBuilder(admin_model).build()
    model = admin_model.Meta.model

    # If Meta has proxy_name, use proxy model instead
    proxy_name = getattr(admin_model.Meta, 'proxy_name', None)
    if proxy_name is not None:
        model = create_proxy_model(model, proxy_name)

    site.register(model, admin_class)


def register_auto(site, model_class):
    # Create AdminModel first
    class AutoAdminModel(AdminModel):
        class Meta:
            model = model_class
    # Register
    register(site, AutoAdminModel)
