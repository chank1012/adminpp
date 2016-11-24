from django.contrib import admin


class AdminBuilder:
    def __init__(self, admin_model_class):
        self.admin_model = admin_model_class()
        self.model = admin_model_class.Meta.model

    def construct_list_display(self, admin_class):
        admin_class.list_display = []
        for field in self.admin_model.get_fields():
            if field.list_display:
                # Create getter function that can be injected to admin class
                class _getter(object):
                    def __init__(self, field):
                        self.field = field

                    # "_getter" class implements "__call__" method,
                    # so it can behave like a get_something(self, obj) in ModelAdmin
                    def __call__(self, obj):
                        value = self.field.get_value(obj)
                        return self.field.render(value)

                    # Add some nice attributes
                    short_description = field.short_description
                    admin_order_field = field.admin_order_field

                # Append getter function to admin_class
                getter_attr_name = 'get_{}'.format(field.name)
                setattr(admin_class, getter_attr_name, _getter(field))
                # Register it to list_display
                admin_class.list_display.append(getter_attr_name)

    def construct_get_queuryset(self, admin_class):
        # https://github.com/django/django/blob/1.10.3/django/contrib/admin/options.py#L318
        def get_queryset(admin_self, request):
            # Main difference is that we get queryset from AdminModel instance, not from model's default manager
            qs = self.admin_model.get_queryset()
            # Others are same with django admin's default implementation
            ordering = admin_self.get_ordering(request)
            if ordering:
                qs = qs.order_by(*ordering)
            return qs

        admin_class.get_queryset = get_queryset

    def construct_meta_kwargs(self, admin_class):
        # Copy all attributes at AdminModel.Meta into admin class
        for attr_name in dir(self.admin_model.Meta):
            # Skip magic methods & predefined attributes
            if attr_name.startswith('__'):
                continue
            elif attr_name in self.admin_model.predefined_meta_fields:
                continue
            # Copy
            setattr(admin_class, attr_name, getattr(self.admin_model.Meta, attr_name))

    def build(self):
        # Create new ModelAdmin class
        class BuilderAdmin(admin.ModelAdmin):
            pass

        # Setup
        self.construct_list_display(BuilderAdmin)
        self.construct_get_queuryset(BuilderAdmin)
        self.construct_meta_kwargs(BuilderAdmin)

        return BuilderAdmin
