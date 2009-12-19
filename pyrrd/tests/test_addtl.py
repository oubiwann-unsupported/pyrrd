import datetime
import os
import tempfile
import unittest

from pyrrd.exceptions import ExternalCommandError
from pyrrd.rrd import DataSource, RRA, RRD
from pyrrd.util import epoch


class AddtlRRDTestCase(unittest.TestCase):

    def setUp(self):
        ds = [ 
            DataSource(dsName="speed", dsType="COUNTER", heartbeat=600)]
        rra = [ 
            RRA(cf="AVERAGE", xff=0.5, steps=1, rows=24),
            RRA(cf="AVERAGE", xff=0.5, steps=6, rows=10)]
        self.rrdfile = tempfile.NamedTemporaryFile()
        self.rrd = RRD(self.rrdfile.name, ds=ds, rra=rra, start=920804400)
        self.rrd.create()

    def test_updateError(self):
        self.rrd.bufferValue(1261214678, 612)
        self.rrd.bufferValue(1261214678, 612)
        self.assertRaises(ExternalCommandError, self.rrd.update)
        try:
            self.rrd.update()
        except ExternalCommandError, error:
            self.assertEquals(str(error), 
            ("ERROR: illegal attempt to update using time 1261214678 "
             "when last update time is 1261214678 (minimum one second step)"))
