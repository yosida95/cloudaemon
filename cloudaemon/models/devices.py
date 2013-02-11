#-*- coding: utf-8 -*-

from . import (
    TemplateElement,
    TemplateMixin
)


class Console(TemplateMixin):
    __tag_name__ = u'console'
    required_values = [
        u'target__port'
    ]

    target = TemplateElement(u'target')


class Serial(TemplateMixin):
    __tag_name__ = u'serial'
    required_values = [
        u'target__port'
    ]

    target = TemplateElement(u'target')


class _Filter(TemplateMixin):
    __tag_name__ = u'filter'
    required_attributes = [
        u'parameter__value'
    ]

    parameter = TemplateElement(u'parameter', name=u'IP')


class NIC(TemplateMixin):
    __tag_name__ = u'interface'
    required_values = [
        u'source__bridge',
        u'model__type',
        u'mac__address',
        u'filter__parameter__value'
    ]

    source = TemplateElement(u'source')
    model = TemplateElement(u'model')
    mac = TemplateElement(u'mac')
    filter = _Filter(filter=u'clean-traffic')
