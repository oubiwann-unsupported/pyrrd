from cStringIO import StringIO
import os
import sys
import tempfile
from unittest import TestCase

from pyrrd.backend import bindings
from pyrrd.exceptions import ExternalCommandError
from pyrrd.rrd import DataSource, RRA, RRD


class BindingsBackendTestCase(TestCase):

    def setUp(self):
        self.ds = [
            DataSource(dsName="speed", dsType="COUNTER", heartbeat=600)]
        self.rra = [
            RRA(cf="AVERAGE", xff=0.5, steps=1, rows=24),
            RRA(cf="AVERAGE", xff=0.5, steps=6, rows=10)]
        self.rrdfile = tempfile.NamedTemporaryFile()
        self.rrd = RRD(self.rrdfile.name, ds=self.ds, rra=self.rra, 
                       start=920804400, backend=bindings)
        self.rrd.create()

    def test_infoWriteMode(self):
        expectedOutput = """
            rra = [{'rows': 24, 'database': None, 'cf': 'AVERAGE', 'cdp_prep': None, 'beta': None, 'seasonal_period': None, 'steps': 1, 'window_length': None, 'threshold': None, 'alpha': None, 'pdp_per_row': None, 'xff': 0.5, 'ds': [], 'gamma': None, 'rra_num': None}, {'rows': 10, 'database': None, 'cf': 'AVERAGE', 'cdp_prep': None, 'beta': None, 'seasonal_period': None, 'steps': 6, 'window_length': None, 'threshold': None, 'alpha': None, 'pdp_per_row': None, 'xff': 0.5, 'ds': [], 'gamma': None, 'rra_num': None}]
            filename = /tmp/tmpQCLRj0
            start = 920804400
            step = 300
            values = []
            ds = [{'name': 'speed', 'min': 'U', 'max': 'U', 'unknown_sec': None, 'minimal_heartbeat': 600, 'value': None, 'rpn': None, 'type': 'COUNTER', 'last_ds': None}]
            ds[speed].name = speed
            ds[speed].min = U
            ds[speed].max = U
            ds[speed].minimal_heartbeat = 600
            ds[speed].type = COUNTER
            rra[0].rows = 24
            rra[0].cf = AVERAGE
            rra[0].steps = 1
            rra[0].xff = 0.5
            rra[0].ds = []
            rra[1].rows = 10
            rra[1].cf = AVERAGE
            rra[1].steps = 6
            rra[1].xff = 0.5
            rra[1].ds = []
            """.strip().split("\n")
        output = StringIO()
        self.assertTrue(os.path.exists(self.rrdfile.name))
        self.rrd.info(useBindings=True, stream=output)
        for obtained, expected in zip(
            output.getvalue().split("\n"), expectedOutput):
            if obtained.startswith("filename"):
                self.assertTrue(expected.strip().startswith("filename"))
            else:
                self.assertEquals(obtained.strip(), expected.strip())

    def test_infoReadMode(self):
        expectedOutput = """
            filename = "/tmp/tmpP4bTTy"
            rrd_version = "0003"
            step = 300
            last_update = 920804400
            header_size = 800
            ds[speed].index = 0
            ds[speed].type = "COUNTER"
            ds[speed].minimal_heartbeat = 600
            ds[speed].min = NaN
            ds[speed].max = NaN
            ds[speed].last_ds = "U"
            ds[speed].value = 0.0000000000e+00
            ds[speed].unknown_sec = 0
            rra[0].cf = "AVERAGE"
            rra[0].rows = 24
            rra[0].cur_row = 3
            rra[0].pdp_per_row = 1
            rra[0].xff = 5.0000000000e-01
            rra[0].cdp_prep[0].value = NaN
            rra[0].cdp_prep[0].unknown_datapoints = 0
            rra[1].cf = "AVERAGE"
            rra[1].rows = 10
            rra[1].cur_row = 2
            rra[1].pdp_per_row = 6
            rra[1].xff = 5.0000000000e-01
            rra[1].cdp_prep[0].value = NaN
            rra[1].cdp_prep[0].unknown_datapoints = 0
            """
        rrd = RRD(filename=self.rrdfile.name, mode="r", backend=bindings)
        output = StringIO()
        self.assertTrue(os.path.exists(self.rrdfile.name))
        rrd.info(useBindings=True, stream=output)
        for obtained, expected in zip(
            output.getvalue().split("\n"), expectedOutput):
            print "obtained:", obtained
            print "expected:", expected
            if obtained.startswith("filename"):
                self.assertTrue(expected.strip().startswith("filename"))
            else:
                self.assertEquals(obtained.strip(), expected.strip())
        sys.stdout = originalStdout
