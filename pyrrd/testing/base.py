import tempfile
from unittest import TestCase

from pyrrd.backend.external import create


class RRDBaseTestCase(TestCase):

    def setUp(self):
        self.rrdfile = tempfile.NamedTemporaryFile()
        self.filename = self.rrdfile.name
        parameters = (
            "--start 920804400 "
            "DS:speed:COUNTER:600:-10.1:10.3 "
            "RRA:AVERAGE:0.5:1:24 "
            "RRA:AVERAGE:0.5:6:10")
        create(self.filename, parameters)
