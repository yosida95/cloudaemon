#-*- coding: utf-8 -*-

from .. import config
from ..xmlutils import (
    Element,
    ModelBase
)


class SerialModel(ModelBase):
    __tagname__ = u'serial'
    __attribs__ = (
        (u'type', u'pty'),
    )

    target = Element(u'target', port=0)

    def set_target_port(self, value):
        self.target.set(u'port', value)


class ConsoleModel(ModelBase):
    __tagname__ = u'console'
    __attribs__ = (
        (u'type', u'pty'),
    )

    target = Element(u'target', port=0)

    def set_target_port(self, value):
        self.target.set(u'port', value)


class InterfaceModel(ModelBase):
    __tagname__ = u'interface'
    __attribs__ = (
        (u'type', u'bridge'),
    )

    mac = Element(u'mac')
    target = Element('target')
    source = Element(u'source', bridge=config.host.network.bridge)
    model = Element(u'model', type=config.guest.network.model)

    def __init__(self, mac_addresss):
        self.mac.set(u'address', mac_addresss)

    def set_target_dev(self, value):
        self.target.set(u'dev', value)

    def set_source_bridge(self, value):
        self.source.set(u'source', value)

    def set_model_type(self, value):
        self.model.set(u'type', value)


class DiskModel(ModelBase):
    __tagname__ = u'disk'
    __attribs__ = (
        (u'type', u'file'),
    )

    driver = Element(u'driver', name=u'qemu', cache=u'none')
    source = Element(u'source')
    target = Element(u'target')

    def __init__(self, device, readonly=False):
        self.set(u'device', device)
        if readonly:
            self.append_element(Element(u'readonly'))

    def set_driver_type(self, value):
        self.driver.set(u'type', value)

    def set_source_file(self, value):
        self.source.set(u'file', value)

    def set_target_dev(self, value):
        self.target.set(u'dev', value)

    def set_target_bus(self, value):
        self.target.set(u'bus', value)


class OSModel(ModelBase):
    __tagname__ = u'os'

    type = Element(u'type')
    boot_cdrom = Element(u'boot', dev=u'cdrom')
    boot_hd = Element(u'boot', dev=u'hd')
    boot_menu = Element(u'bootmenu', enable=u'yes')

    def set_type(self, value):
        self.type.set_text(value)

    def set_type_arch(self, value):
        self.type.set(u'arch', value)


class DevicesModel(ModelBase):
    __tagname__ = u'devices'

    emulator = Element(u'emulator')
    graphics = Element(u'graphics', keymap=u'en-us', autoport=u'no')
    serial = SerialModel()
    console = ConsoleModel()

    def set_emulator_path(self, value):
        self.emulator.set(u'path', value)

    def set_graphics_type(self, value):
        self.graphics.set(u'type', value)

    def set_graphics_port(self, value):
        self.graphics.set(u'port', value)

    def append_device(self, device):
        _device = device._root if isinstance(device, ModelBase) else device
        self.append_element(_device)

    def remove_device(self, device):
        _device = device._root if isinstance(device, ModelBase) else device
        self.remove_element(_device)


class DomainModel(ModelBase):
    __tagname__ = u'domain'

    uuid = Element(u'uuid')
    name = Element(u'name')
    os = OSModel()
    vcpu = Element(u'vcpu')
    memory = Element(u'memory', unit=u'KiB')
    currentMemory = Element(u'currentMemory', unit=u'KiB')
    devices = DevicesModel()
    on_poweroff = Element(u'on_poweroff')
    on_reboot = Element(u'on_reboot')
    on_crash = Element(u'on_crash')
    clock = Element(u'clock', offset=u'utc')

    def __init__(self, type, uuid, name, vcpu, memory_kb):
        self.set(u'type', type)
        self.uuid.set_text(uuid)
        self.name.set_text(name)
        self.vcpu.set_text(vcpu)
        self.memory.set_text(memory_kb)
        self.currentMemory.set_text(memory_kb)

    def set_on_poweroff(self, value):
        self.on_poweroff.set_text(value)

    def set_on_reboot(self, value):
        self.on_reboot.set_text(value)

    def set_on_crash(self, value):
        self.on_crash.set_text(value)
