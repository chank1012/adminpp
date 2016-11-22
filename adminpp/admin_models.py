from adminpp.builder import AdminBuilder


class optional:
    pass


class BaseField(object):
    name = None  # name of the field (at AdminModel)
    model = None

    def __init__(self,
                 list_display=True,
                 source=None,
                 short_description=None):
        self.list_display = list_display

        # Set property objects
        self._short_description = short_description
        self._source = source

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

    def render(self, obj):
        return getattr(obj, self.source)


class CharField(BaseField):
    pass


class IntegerField(BaseField):
    pass


class AdminModel(object):
    Meta = None

    def get_fields(self):
        fields = []
        # Get all fields declared at ModelAdmin class
        for attr_name in dir(self):
            attr = getattr(self, attr_name, None)
            if isinstance(attr, BaseField):
                field_object = attr
                # Append "model" and "name" info into field object
                field_object.model = self.Meta.model
                field_object.name = attr_name
                # Append to result array
                fields.append(attr)
        return fields

    def get_queryset(self):
        return self.Meta.model._default_manager.get_queryset()


def adminpp_register(site, admin_model):
    admin_class = AdminBuilder(admin_model).build()
    site.register(admin_model.Meta.model, admin_class)
