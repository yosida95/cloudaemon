#-*- coding: utf-8 -*-

from xml.etree.ElementTree import (
    Element,
    tostring
)


class TemplateElement(object):

    def __init__(self, tag, **attrib):
        self.tag = unicode(tag)
        self.attrib = dict((unicode(key), unicode(value))
                           for key, value in attrib.items())
        self._text = None

        self._children = []

    def append(self, element):
        if isinstance(element, self.__class__) is False:
            raise ValueError

        if element in self._children:
            raise ValueError

        self._children.append(element)

    def remove(self, element):
        if isinstance(element, self.__class__) is False:
            raise ValueError

        if element not in self._children:
            raise ValueError

        self._children.pop(self._children.index(element))

    def insert(self, index, element):
        if isinstance(element, self.__class__) is False:
            raise ValueError

        if element in self._children:
            raise ValueError

        self._children.insert(index, element)

    def set(self, key, value=None):
        self.attrib[unicode(key)] = unicode(value)

    def get(self, key):
        return self.attrib[unicode(key)]

    def keys(self):
        return self.attrib.keys()

    def items(self):
        return self.attrib.items()

    def get_text(self):
        return self._text

    def set_text(self, value):
        self._text = unicode(value)

    text = property(get_text, set_text)

    def copy(self):
        inst = self.__class__(self.tag, **self.attrib)
        inst._text = self._text
        inst._children = [child.copy() for child in self._children]

        return inst

    def render(self):
        root = Element(self.tag, attrib=self.attrib)
        if self._text is not None:
            root.text = self._text

        for child in self._children:
            root.append(child.render())

        return root


class TemplateMixin(object):
    __tag_name__ = None
    required_values = []

    def __init__(self, **attrib):
        if self.__tag_name__ is None:
            raise ValueError(u'__tag_name__')

        self._root = TemplateElement(self.__tag_name__, **attrib)

        required_attributes = set(
            key.split(u'__')[0] for key in self.required_values
        )
        for attribute in required_attributes:
            if attribute not in dir(self):
                raise ValueError(u'%s.%s is undefined' % (
                    self.__class__.__name__, attribute
                ))

        self.attributes = {}
        for key in dir(self):
            value = getattr(self, key)
            if key != u'_root':
                if isinstance(value, TemplateElement):
                    self.attributes[key] = value.copy()
                    self._root.append(self.attributes[key])
                elif isinstance(value, TemplateMixin):
                    self.attributes[key] = value.copy()
                    self._root.append(self.attributes[key]._root)

    def copy(self):
        return self.__class__(**dict(self._root.items()))


class TemplateRenderer(object):

    def __init__(self, template):
        self.template = template

    def set_value(self, key, value, root=None):
        if root is None:
            root = self.template

        key_splited = key.split(u'__')
        if len(key_splited) > 2:
            self.set_value(u'__'.join(key_splited[1:]), value,
                           root.attributes[key_splited[0]])
        else:
            if key_splited[1] == u'$text':
                root.attributes[key_splited[0]].set_text(value)
            else:
                root.attributes[key_splited[0]].set(key_splited[1], value)

    def render(self, values):
        if len(set(self.template.required_values) - set(values.keys())) > 0:
            raise ValueError(u'Not enough values')

        for key, value in values.items():
            self.set_value(key, value)

        return tostring(self.template._root.render())
