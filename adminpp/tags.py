import six
from django.utils import html


def render_attribute(value):
    if isinstance(value, six.integer_types):
        return str(value)
    elif isinstance(value, six.string_types):
        return '"' + html.escape(value) + '"'
    else:
        # Maybe we don't need to handle this
        return str(value)


def render_body(value):
    if value is None:
        return ''
    elif isinstance(value, six.string_types):
        return html.escape(value)
    elif isinstance(value, TagBase):
        return value.render()
    else:
        return str(value)


class TagBase(object):
    def __init__(self, tag, body=None, **kwargs):
        self.tag = tag
        self.body = body
        self.kwargs = kwargs

    def __str__(self):
        return unicode(self).encode('utf-8')

    def __unicode__(self):
        return self.render()

    def render(self):
        raise NotImplementedError

    def render_body(self):
        if hasattr(self.body, '__iter__'):
            return html.mark_safe(''.join([render_body(x) for x in self.body]))
        else:
            return render_body(self.body)

    def render_kwargs(self):
        result = ''
        for attr_key in self.kwargs:
            attr_value = self.kwargs[attr_key]
            result += ' {}={}'.format(attr_key, render_attribute(attr_value))
        return html.mark_safe(result)


class Tag(TagBase):
    def render(self):
        return html.format_html('<{0}{1}>{2}</{0}>',
                                self.tag,
                                self.render_kwargs(),
                                self.render_body())

class VoidTag(TagBase):
    def render(self):
        return html.format_html('<{0}{1} />',
                                self.tag,
                                self.render_kwargs())
