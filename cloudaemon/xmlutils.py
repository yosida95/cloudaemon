# -*- coding: utf-8 -*-

from xml.etree.ElementTree import (
    Element as XMLElement,
    tostring
)
from xml.dom import minidom


class Element(object):

    def __init__(self, tag, **attrib):
        self.tag = unicode(tag)
        self.attrib = dict((unicode(key), unicode(value))
                           for key, value in attrib.items())
        self._children = []
        self._text = None

    def get(self, key):
        return self.attrib[unicode(key)]

    def set(self, key, value):
        self.attrib[unicode(key)] = unicode(value)

    def get_text(self):
        return self._text

    def set_text(self, text):
        self._text = unicode(text)

    text = property(get_text, set_text)

    def append(self, child):
        if isinstance(child, Element) is False:
            raise ValueError

        self._children.append(child)

    def insert(self, index, child):
        if isinstance(child, Element) is False:
            raise ValueError

        self._children.insert(index, child)

    def remove(self, child):
        if child not in self._children:
            raise ValueError

        self._children.remove(child)

    def build(self):
        root = XMLElement(self.tag, attrib=self.attrib)
        if self._text:
            root.text = self._text
        for child in self._children:
            root.append(child.build())

        return root


class ModelBase(object):

    def __new__(cls, *args, **kwargs):
        inst = super(ModelBase, cls).__new__(cls)

        if u'__tagname__' not in cls.__dict__:
            raise ValueError

        inst._root = Element(cls.__dict__[u'__tagname__'],
                             **dict(cls.__dict__.get(u'__attribs__', [])))
        for key, value in cls.__dict__.items():
            if isinstance(value, Element):
                inst._root.append(value)
                setattr(inst, key, value)
            elif isinstance(value, ModelBase):
                inst._root.append(value._root)
                setattr(inst, key, value)

        return inst

    def __setattr__(self, name, value):
        if name in self.__dict__:
            if isinstance(self.__getattr__(name), Element)\
                    or isinstance(self.__getattr__(name), ModelBase):
                self._root.remove(self.__getattr__(name))
                self._root.append(value)
        else:
            if hasattr(self, u'_root') and name == u'_root':
                raise ValueError

        super(ModelBase, self).__setattr__(name, value)

    def __delattr__(self, name):
        if isinstance(self.__getattr__(name), Element)\
                or isinstance(self.__getattr__(name), ModelBase):
            self._root.remove(self.__getattr__(name))

        super(ModelBase, self).__delattr__(name)

    def set(self, name, value):
        self._root.set(name, value)

    def append_element(self, element):
        self._root.append(element)

    def remove_element(self, element):
        self._root.remove(element)

    def validate(self):
        return

    def to_xml(self):
        self.validate()
        dom_tree = minidom.parseString(tostring(self._root.build()))
        return dom_tree.toprettyxml(indent="    ")\
            .replace(u'<?xml version="1.0" ?>\n', u'')[:-1]
