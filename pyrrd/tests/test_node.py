from unittest import TestCase

from pyrrd.node import RRDXMLNode
from pyrrd.testing import dump
from pyrrd.util import XML


class RRDXMLNodeTestCase(TestCase):

    def setUp(self):
        self.tree = XML(dump.simpleDump01)

    def test_creation(self):
        rrd = RRDXMLNode(self.tree)
        self.assertEquals(rrd.getAttribute("version"), "0003")
        self.assertEquals(rrd.getAttribute("step"), "300")
        self.assertEquals(rrd.getAttribute("lastupdate"), "920804400")

    def test_creationDS(self):
        dsChecks = [
            ("name", "speed"),
            ("type", "COUNTER"),
            ("minimal_heartbeat", "600"),
            ("min", "NaN"),
            ("max", "NaN"),
            ("last_ds", "UNKN"),
            ("value", "0.0000000000e+00"),
            ("unknown_sec", "0")]
        rrd = RRDXMLNode(self.tree)
        self.assertEquals(len(rrd.ds), 1)
        ds = rrd.ds[0]
        for name, value in dsChecks:
            self.assertEquals(ds.getAttribute(name), value)

    def test_creationRRA(self):
        rra1Checks = [
            ("cf", "AVERAGE"),
            ("pdp_per_row", "1")]
        rra2Checks = [
            ("cf", "AVERAGE"),
            ("pdp_per_row", "6")]
        rrd = RRDXMLNode(self.tree)
        self.assertEquals(len(rrd.rra), 2)
        rra1 = rrd.rra[0]
        for name, value in rra1Checks:
            self.assertEquals(rra1.getAttribute(name), value)
        rra2 = rrd.rra[1]
        for name, value in rra2Checks:
            self.assertEquals(rra2.getAttribute(name), value)

    def test_creationRRAParams(self):
        rrd = RRDXMLNode(self.tree)
        self.assertEquals(len(rrd.rra), 2)
        rra1 = rrd.rra[0]
        self.assertEquals(rra1.getAttribute("xff"), "5.0000000000e-01")
        rra2 = rrd.rra[1]
        self.assertEquals(rra2.getAttribute("xff"), "5.0000000000e-01")

    def test_creationRRACDPPrep(self):
        dsChecks = [
            ("primary_value", "0.0000000000e+00"),
            ("secondary_value", "0.0000000000e+00"),
            ("value", "NaN"),
            ("unknown_datapoints", "0")]
        rrd = RRDXMLNode(self.tree)
        cdpPrep1 = rrd.rra[0].cdp_prep
        self.assertEquals(len(cdpPrep1.ds), 1)
        for name, value in dsChecks:
            self.assertEquals(cdpPrep1.ds[0].getAttribute(name), value)
        cdpPrep2 = rrd.rra[1].cdp_prep
        self.assertEquals(len(cdpPrep2.ds), 1)
        for name, value in dsChecks:
            self.assertEquals(cdpPrep2.ds[0].getAttribute(name), value)

    def test_creationIncludeData(self):
        rrd = RRDXMLNode(self.tree, includeData=True)
