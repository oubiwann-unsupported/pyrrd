from pyrrd.node import RRDXMLNode
from pyrrd.external import load


class Mapper(object):
    """
    """
    __slots__ = []
    __skip_repr__ = []

    def setAttributes(self, attributes):
        for name, value in attributes.items():
            setattr(self, name, value)

    def getData(self):
        items = {}
        for name in self.__slots__:
            if name not in self.__skip_repr__:
                items[name] = getattr(self, name, None)
        return items

    def map(self, node):
        """
        """
        self.setAttributes(node.attributes)

    def printInfo(self):
        for name, value in self.getData().items():
            print "%s = %s" % (name, str(value))


class RowMapper(Mapper):
    """
    """
    __slots__ = ["v"]


class DatabaseMapper(Mapper):
    """
    """
    __slots__ = ["rows"]
    __skip_repr__ = ["rows"]
    rows = []


class CDPrepDSMapper(Mapper):
    """
    """
    __slots__ = [
        "primary_value",
        "secondary_value",
        "value",
        "unknown_datapoints",
        ]

    def printInfo(self, prefix, index):
        for name, value in self.getData().items():
            print "%s.cdp_prep[%s].%s = %s" % (prefix, index, name, str(value))


class CDPPrepMapper(Mapper):
    """
    """
    __slots__ = ["ds"]
    __skip_repr__ = ["ds"]
    ds = []


class RRAMapper(Mapper):
    """
    """
    __slots__ = [
        "cf",
        "pdp_per_row",
        "xff",
        "cdp_prep",
        "ds",
        "steps",
        "rows",
        "alpha",
        "beta",
        "seasonal_period",
        "rra_num",
        "gamma",
        "threshold",
        "window_length",
        "database",
        ]
    __skip_repr__ = ["ds"]
    ds = []

    def map(self, node):
        super(RRAMapper, self).map(node)
        for subNode in node.cdp_prep.ds:
            ds = CDPrepDSMapper()
            ds.map(subNode)
            self.ds.append(ds)

    def getData(self):
        data = super(RRAMapper, self).getData()
        data["ds"] = [ds.getData() for ds in self.ds]
        return data

    def printInfo(self, index):
        prefix = "rra[%s]" % index
        for name, value in self.getData().items():
            print "%s.%s = %s" % (prefix, name, str(value))
        for index, ds in enumerate(self.ds):
            ds.printInfo(prefix, index)


class DSMapper(Mapper):
    """
    """
    __slots__ = [
        "name",
        "type",
        "minimal_heartbeat",
        "min",
        "max",
        "last_ds",
        "value",
        "unknown_sec",
        "rpn",
        ]

    def printInfo(self):
        for name, value in self.getData().items():
            if name != self.name:
                print "ds[%s].%s = %s" % (self.name, name, str(value))


class RRDMapper(Mapper):
    """
    """
    __slots__ = [
        "version",
        "step",
        "lastupdate",
        "ds",
        "rra",
        "values",
        "start",
        "filename",
        ]
    __skip_repr__ = ["ds", "rra"]
    ds = []
    rra = []

    def getData(self):
        """
        """
        #if not (self.ds or self.rra):
        #    self.map()
        data = super(RRDMapper, self).getData()
        data["ds"] = [ds.getData() for ds in self.ds]
        data["rra"] = [rra.getData() for rra in self.rra]
        return data

    def map(self):
        """
        """
        tree = load(self.filename)
        node = RRDXMLNode(tree)
        super(RRDMapper, self).map(node)
        for subNode in node.ds:
            ds = DSMapper()
            ds.map(subNode)
            self.ds.append(ds)
        for subNode in node.rra:
            rra = RRAMapper()
            rra.map(subNode)
            self.rra.append(rra)


def _test():
    from doctest import testmod
    testmod()


if __name__ == '__main__':
    _test()

