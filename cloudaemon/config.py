#-*- coding: utf-8 -*-


class Configurator(object):

    def __init__(self, config):
        self.config = config

    def __getattr__(self, key):
        if key in self.config:
            if isinstance(self.config[key], dict):
                self.config[key] = self.__class__(self.config[key])

            return self.config[key]
        else:
            raise AttributeError


host = Configurator({
    u'network': {
        u'bridge': u'br0'
    }
})


guest = Configurator({
    u'network': {
        u'model': u'virtio'
    }
})
