#-*- coding: utf-8 -*-

from xml.etree.ElementTree import (
    Element,
    tostring
)


class TemplateMixin(object):
    TAG_NAME = None

    def __init__(self, **attrib):
        if self.TAG_NAME is None:
            raise ValueError

        self.root = TemplateElement(self.TAG_NAME, **attrib)

    def tostring(self):
        return tostring(self.root.render())


class TemplateElement(object):

    def __init__(self, tag, **attrib):
        self.tag = unicode(tag)
        self.attrib = dict((unicode(key), unicode(value))
                           for key, value in attrib.items())
        self._text = None

        self._children = []
        self._childmap = {}

    def append(self, element):
        if isinstance(element, self.__class__) is False:
            raise ValueError

        if element.tag in self._childmap:
            raise ValueError

        self._children.append(element)
        self._childmap[unicode(element.tag)] = element

    def remove(self, element):
        if isinstance(element, self.__class__) is False:
            raise ValueError

        if element not in self._children:
            raise ValueError

        self._children.pop(self._children.index(element))
        del self._childmap[element.tag]

    def insert(self, index, element):
        if isinstance(element, self.__class__) is False:
            raise ValueError

        if element.tag in self._childmap:
            raise ValueError

        self._children.insert(index, element)
        self._childmap[element.tag] = element

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
        print u'hoge'
        self._text = unicode(value)

    text = property(get_text, set_text)

    def __getitem__(self, key):
        return self._childmap[unicode(key)]

    def render(self):
        root = Element(self.tag, attrib=self.attrib)
        if self._text is not None:
            root.text = self._text

        for child in self._children:
            root.append(child.render())

        return root
