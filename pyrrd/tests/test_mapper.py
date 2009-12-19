from unittest import TestCase

from pyrrd.mapper import RRDMapper
from pyrrd.testing import dump
from pyrrd.util import NaN, XML


class FakeBackend(object):

    def __init__(self, tree):
        self.tree = tree

    def load(self, filename):
        return self.tree


class RRDMapperTestCase(TestCase):

    def setUp(self):
        self.tree = XML(dump.simpleDump01)

    def makeMapper(self):
        rrd = RRDMapper()
        rrd.filename = None
        rrd.backend = FakeBackend(self.tree)
        rrd.map()
        return rrd

    def test_map(self):
        rrd = self.makeMapper()
        self.assertEquals(rrd.version, 3)
        self.assertEquals(rrd.step, 300)
        self.assertEquals(rrd.lastupdate, 920804400)

    def test_mapDS(self):
        rrd = self.makeMapper()
        self.assertEquals(len(rrd.ds), 1)
        ds = rrd.ds[0]
        self.assertEquals(ds.name, "speed")
        self.assertEquals(ds.type, "COUNTER")
        self.assertEquals(ds.minimal_heartbeat, 600)
        self.assertEquals(ds.min, "NaN")
        self.assertEquals(ds.max, "NaN")

    def test_mapRRA(self):
        rrd = self.makeMapper()
        self.assertEquals(len(rrd.rra), 2)
        rra1 = rrd.rra[0]
        self.assertEquals(rra1.cf, "AVERAGE")
        self.assertEquals(rra1.pdp_per_row, 1)
        rra2 = rrd.rra[1]
        self.assertEquals(rra2.cf, "AVERAGE")
        self.assertEquals(rra2.pdp_per_row, 6)

    def test_mapRRAParams(self):
        rrd = self.makeMapper()
        rra1 = rrd.rra[0]
        self.assertEquals(rra1.xff, 0.5)
        rra2 = rrd.rra[1]
        self.assertEquals(rra2.xff, 0.5)

    def test_mapRRACDPPrep(self):
        rrd = self.makeMapper()
        ds1 = rrd.rra[0].ds
        self.assertEquals(len(ds1), 1)
        self.assertEquals(ds1[0].primary_value, 0.0)
        self.assertEquals(ds1[0].secondary_value, 0.0)
        self.assertEquals(str(ds1[0].value), str(NaN()))
        self.assertEquals(ds1[0].unknown_datapoints, 0)
        ds2 = rrd.rra[1].ds
        self.assertEquals(len(ds2), 1)
        self.assertEquals(len(ds1), 1)
        self.assertEquals(ds2[0].primary_value, 0.0)
        self.assertEquals(ds2[0].secondary_value, 0.0)
        self.assertEquals(str(ds2[0].value), str(NaN()))
        self.assertEquals(ds2[0].unknown_datapoints, 0)
