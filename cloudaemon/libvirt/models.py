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
        if self._text:
            root.text = self._text
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


class SerialModel(ModelBase):

    def __init__(self, **kwargs):
        kwargs[u'type'] = u'pty'
        super(InterfaceModel, self).__init__(u'serial', **kwargs)

        self.target = self.create_element(u'target')
        self.root.append(self.target)

    def validate(self):
        try:
            assert self.target.get(u'port')
        except KeyError:
            raise AssertionError

    def set_target_port(self, value):
        self.target.set(u'port', value)


class ConsoleModel(ModelBase):

    def __init__(self, **kwargs):
        kwargs[u'type'] = u'pty'
        super(InterfaceModel, self).__init__(u'console', **kwargs)

        self.target = self.create_element(u'target')
        self.root.append(self.target)

    def validate(self):
        try:
            assert self.target.get(u'port')
        except KeyError:
            raise AssertionError

    def set_target_port(self, value):
        self.target.set(u'port', value)


class DiskModel(ModelBase):

    def __init__(self, **kwargs):
        assert kwargs.get(u'device')
        kwargs[u'type'] = u'file'
        super(DiskModel, self).__init__(u'disk', **kwargs)

        self.driver = self.create_element(u'driver',
                                          name=u'qemu', cache=u'none')
        self.root.append(self.driver)

        self.source = self.create_element(u'source')
        self.root.append(self.source)

        self.target = self.create_element(u'target')
        self.root.append(self.target)

        self.readonly = self.create_element(u'readonly')

    def validate(self):
        try:
            assert self.source.get(u'file')
            assert self.driver.get(u'type')
            assert self.target.get(u'dev')
            assert self.target.get(u'bus')
        except KeyError:
            raise AssertionError

    def set_readonly(self, readonly=True):
        if readonly:
            self.root.append(self.readonly)
        else:
            self.root.remove(self.readonly)

    def set_source_file(self, value):
        self.source.set(u'file', value)

    def set_driver_type(self, value):
        self.driver.set(u'type', value)

    def set_target_dev(self, value):
        self.target.set(u'dev', value)

    def set_target_bus(self, value):
        self.target.set(u'bus', value)


class GuestModel(ModelBase):

    def __init__(self, **kwargs):
        kwargs[u'type'] = u'kvm'
        if u'uuid' not in kwargs:
            raise AssertionError

        if u'name' not in kwargs:
            raise AssertionError

        uuid = kwargs.get(u'uuid')
        name = kwargs.get(u'name')
        del kwargs[u'uuid']
        del kwargs[u'name']

        super(GuestModel, self).__init__(u'guest', **kwargs)

        self.root.append(self.create_text_element(u'uuid', uuid))
        self.root.append(self.create_text_element(u'name', name))

        os = self.create_element(u'os')
        os_type = self.create_text_element(u'type', u'hvm')
        os_type.set(u'arch', u'i686')
        os.append(os_type)
        os.append(self.create_element(u'boot', dev=u'cdrom'))
        os.append(self.create_element(u'boot', dev=u'hd'))
        os.append(self.create_element(u'bootmenu', enable=u'yes'))
        self.root.append(os)

        self.root.append(self.create_element(u'clock', offset=u'utc'))

        self.root.append(self.create_text_element(u'on_poweroff', u'destroy'))
        self.root.append(self.create_text_element(u'on_reboot', u'restart'))
        self.root.append(self.create_text_element(u'on_crash', u'restart'))

        self.vcpu = self.create_element(u'vcpu')
        self.root.append(self.vcpu)

        self.memory = self.create_element(u'memory', unit=u'KiB')
        self.root.append(self.memory)

        self._currentMemory = self.create_element(u'currentMemory',
                                                  unit=u'KiB')
        self.root.append(self._currentMemory)

        self.devices = self.create_element(u'devices')
        self.devices.append(
            self.create_text_element(u'emulator', config.host.emulator)
        )
        self.root.append(self.devices)

    def validate(self):
        try:
            assert self.vcpu.get_text()
            assert self.memory.get_text()
            assert self._currentMemory.get_text()
        except KeyError:
            raise AssertionError

    def set_vcpu(self, value):
        self.vcpu.set_text(value)

    def set_memory(self, value):
        self.memory.set_text(value)
        self._currentMemory.set_text(value)

    def append_device(self, value):
        self.devices.append(value)

    def remove_device(self, value):
        self.devices.remove(value)
