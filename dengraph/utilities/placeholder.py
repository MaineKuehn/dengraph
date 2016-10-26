class Placeholder(object):
    """
    Class for unique placeholders, e.g. default values, that pretty-print
    """
    def __init__(self, name):
        self.name = name

    def __str__(self):
        return self.name

    def __repr__(self):
        return '<%s %r at 0x%x>' % (self.__class__.__name__, self.name, id(self))

    def __eq__(self, other):
        if isinstance(self, other.__class__):
            return self.name == other.name
        return NotImplemented

    def __ne__(self, other):
        return not self == other

NOTSET = Placeholder(name='No Default')
