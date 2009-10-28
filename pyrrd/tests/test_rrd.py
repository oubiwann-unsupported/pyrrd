from unittest import TestCase

from pyrrd.rrd import DataSource, RRA, RRD


class RRDTestCase(TestCase):

    def test_creationDefaults(self):
        filename = '/tmp/test.rrd'
        rrd = RRD(filename, start=920804400)
        self.assertEquals(rrd.filename, filename)
        self.assertEquals(rrd.ds, [])
        self.assertEquals(rrd.rra, [])
        self.assertEquals(rrd.values, [])
        self.assertEquals(rrd.step, 300)
        self.assertEquals(rrd.lastupdate, None)

    def test_creation(self):
        dss = []
        rras = []
        filename = '/tmp/test.rrd'
        dss.append(DataSource(dsName='speed', dsType='COUNTER', heartbeat=600))
        rras.append(RRA(cf='AVERAGE', xff=0.5, steps=1, rows=24))
        rras.append(RRA(cf='AVERAGE', xff=0.5, steps=6, rows=10))
        rrd = RRD(filename, ds=dss, rra=rras, start=920804400)
        self.assertEquals(rrd.filename, filename)
        self.assertEquals(repr(rrd.ds), "[DS:speed:COUNTER:600:U:U]")
        self.assertEquals(
            repr(rrd.rra),
            "[RRA:AVERAGE:0.5:1:24, RRA:AVERAGE:0.5:6:10]")
        self.assertEquals(rrd.values, [])
        self.assertEquals(rrd.step, 300)
        self.assertEquals(rrd.lastupdate, None)

    def test_creationDSsAndRRAs(self):
        dss1 = []
        rras1 = []
        filename = '/tmp/test1.rrd'
        dss1.append(DataSource(dsName='speed', dsType='COUNTER', heartbeat=600))
        rras1.append(RRA(cf='AVERAGE', xff=0.5, steps=1, rows=24))
        rras1.append(RRA(cf='AVERAGE', xff=0.5, steps=6, rows=10))
        rrd1 = RRD(filename, ds=dss1, rra=rras1, start=920804400)
        self.assertEquals(repr(rrd1.ds), "[DS:speed:COUNTER:600:U:U]")
        self.assertEquals(
            repr(rrd1.rra),
            "[RRA:AVERAGE:0.5:1:24, RRA:AVERAGE:0.5:6:10]")

        filename = '/tmp/test2.rrd'
        rrd2 = RRD(filename, start=920804400)
        self.assertEquals(rrd2.ds, [])
        self.assertEquals(rrd2.rra,[])

        dss3 = []
        rras3 = []
        filename = '/tmp/test3.rrd'
        dss3.append(DataSource(dsName='speed', dsType='COUNTER', heartbeat=300))
        rras3.append(RRA(cf='AVERAGE', xff=0.5, steps=2, rows=24))
        rras3.append(RRA(cf='AVERAGE', xff=0.5, steps=12, rows=10))
        rrd3 = RRD(filename, ds=dss3, rra=rras3, start=920804400)

        self.assertEquals(repr(rrd3.ds), "[DS:speed:COUNTER:300:U:U]")
        self.assertEquals(
            repr(rrd3.rra),
            "[RRA:AVERAGE:0.5:2:24, RRA:AVERAGE:0.5:12:10]")
