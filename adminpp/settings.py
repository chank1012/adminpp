from django.conf import settings

DEFAULT_RENDERER = getattr(settings, 'ADMINPP_DEFAULT_RENDERER', 'adminpp.renderers.BasicFieldRenderer')
