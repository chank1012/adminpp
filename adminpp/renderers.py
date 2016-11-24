from django.contrib.admin.templatetags.admin_list import _boolean_icon
from django.utils import html
from adminpp.tags import Tag, VoidTag


class FieldRendererBase(object):
    def render_text(self, value):
        raise NotImplementedError

    def render_integer(self, value):
        raise NotImplementedError

    def render_boolean(self, value):
        raise NotImplementedError

    def render_tag(self, value):
        raise NotImplementedError


class BasicFieldRenderer(FieldRendererBase):
    def render_text(self, value):
        return html.escape(value)

    def render_integer(self, value):
        raise str(value)

    def render_boolean(self, value):
        return _boolean_icon(value)

    def render_tag(self, value):
        return html.mark_safe(value)
