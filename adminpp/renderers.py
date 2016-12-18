from django.contrib.admin.templatetags.admin_list import _boolean_icon
from django.utils import html
from adminpp.settings import DEFAULT_RENDERER
from adminpp.utils import get_class_from_string


class FieldRendererBase(object):
    def render_text(self, value):
        raise NotImplementedError

    def render_integer(self, value):
        raise NotImplementedError

    def render_boolean(self, value):
        raise NotImplementedError

    def render_datetime(self, value):
        raise NotImplementedError


class BasicFieldRenderer(FieldRendererBase):
    def render_text(self, value, allow_tags=False):
        if allow_tags:
            return html.mark_safe(value)
        else:
            return html.escape(value)

    def render_integer(self, value):
        return str(value)

    def render_boolean(self, value):
        return _boolean_icon(value)

    def render_datetime(self, value):
        return value.strftime('%Y-%m-%d %I:%M:%S')


_default_renderer = None
def get_default_renderer():
    global _default_renderer
    if _default_renderer is None:
        default_renderer_class = get_class_from_string(DEFAULT_RENDERER)
        _default_renderer = default_renderer_class()
    return _default_renderer
