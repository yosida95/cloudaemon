#-*- coding: utf-8 -*-

from xml.etree.ElementTree import (
    Element,
    tostring
)

from .. import config


class XMLElement(object):

    def __init__(self, tag, **attrib):
        self.tag = unicode(tag)
        self.attrib = dict((unicode(key), unicode(value))
                           for key, value in attrib.items())
        self._children = []

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
        if isinstance(child, XMLElement) is False:
            raise ValueError

        self._children.append(child)

    def insert(self, index, child):
        if isinstance(child, XMLElement) is False:
            raise ValueError

        self._children.insert(index, child)

    def remove(self, child):
        if child not in self._children:
            raise ValueError

        self._children.remove(child)

    def build(self):
        root = Element(self.tag, attrib=self.attrib)
        for child in self._children:
            root.append(child.build())

        return root


class ModelBase(object):

    def __init__(self, tag, **kwargs):
        self.root = XMLElement(tag, **kwargs)

    def create_element(self, tag, **args):
        return XMLElement(tag, **args)

    def create_text_element(self, tag, text):
        element = XMLElement(tag)
        element.set_text(text)
        return element

    def validate(self):
        return

    def to_xml(self):
        self.validate()
        return tostring(self.root.build())


class InterfaceModel(ModelBase):

    def __init__(self, **kwargs):
        super(InterfaceModel, self).__init__(u'intarface', **kwargs)

        self.mac = self.create_element(u'mac')
        self.root.append(self.mac)

        self.target = self.create_element(u'target')
        self.root.append(self.target)

        self.source = self.create_element(u'source',
                                          bridge=config.host.network.bridge)
        self.root.append(self.source)

        self.model = self.create_element(u'model',
                                         type=config.guest.network.model)
        self.root.append(self.model)

    def validate(self):
        try:
            assert self.mac.get(u'address')
            assert self.target.get(u'dev')
        except KeyError:
            raise AssertionError

    def set_mac_address(self, value):
        self.mac.set(u'address', value)

    def set_target_dev(self, value):
        self.target.set(u'dev', value)

    def set_source_bridge(self, value):
        self.target.set(u'bridge', value)

    def set_model_type(self, value):
        self.model.set(u'type', value)
