""" verifying functionality of pyrrd library"""
import datetime
import os
import unittest

from pyrrd.rrd import RRD, RRA, DS
from pyrrd.util import epoch

DSNAME = 'testds'
RRDFILENAME = 'testrrd'
def create_base_rrd():
    dss = []
    rras = []
    ds1 = DS(dsName=DSNAME,dsType="GAUGE",heartbeat=600)
    dss.append(ds1)
    rra_5min_avg_qtr = RRA(cf='AVERAGE', xff=0.5, steps=1, rows=30)
    rras.append(rra_5min_avg_qtr) 
    # create initial RRD starting 1 day ago...
    just_a_bit_ago = epoch(datetime.datetime.now())-86400
    thisRRDfile = RRD(RRDFILENAME, ds=dss, rra=rras, step=300, start=just_a_bit_ago)
    thisRRDfile.create()
    
def nuke_base_rrd():
    if os.path.exists(RRDFILENAME):
        os.remove(RRDFILENAME)
    
class AddtlRRDTestCase(unittest.TestCase):
    """ pyrrd unit tests """

    def setUp(self):
        """set up for pyrrd verification"""
        nuke_base_rrd()
    #
    def tearDown(self):
        """remove test RRD file is still around"""
        nuke_base_rrd()
    #
    def test_setup_teardown(self):
        """testing set up and tear down"""
        self.assertFalse(os.path.exists(RRDFILENAME))
        create_base_rrd()
        self.assertTrue(os.path.exists(RRDFILENAME))
        nuke_base_rrd()
        self.assertFalse(os.path.exists(RRDFILENAME))
    #
    def test_stupid_insert_error(self):
        """testing incorrect update calls, throwing exception
        http://code.google.com/p/pyrrd/issues/detail?id=19"""
        self.assertFalse(os.path.exists(RRDFILENAME))
        create_base_rrd()
        this_rrd = RRD(RRDFILENAME)
        # convert datetime object to seconds since epoch for RRD...
        now = datetime.datetime.now()
        now_int = epoch(now)
        this_rrd.bufferValue(now_int,612)
        this_rrd.bufferValue(now_int,612)
        self.assertRaises(Exception,this_rrd.update())        
    #
    def test_ds_value(self):
        """test ds value in RRD after multiple updates
        http://code.google.com/p/pyrrd/issues/detail?id=18"""
        nuke_base_rrd()
        create_base_rrd()
        this_rrd = RRD(RRDFILENAME)
        #convert datetime object to seconds since epoch for RRD...
        now = datetime.datetime.now()
        now_int = epoch(now)
        min5ago_int = epoch(now-datetime.timedelta(minutes=5))
        min10ago_int = epoch(now-datetime.timedelta(minutes=10))
        min15ago_int = epoch(now-datetime.timedelta(minutes=15))
        min20ago_int = epoch(now-datetime.timedelta(minutes=20))
        min25ago_int = epoch(now-datetime.timedelta(minutes=25))
        min30ago_int = epoch(now-datetime.timedelta(minutes=30))
        this_rrd.bufferValue(min30ago_int,12)
        this_rrd.bufferValue(min25ago_int,112)
        this_rrd.bufferValue(min20ago_int,212)
        this_rrd.bufferValue(min15ago_int,312)
        this_rrd.bufferValue(min10ago_int,412)
        this_rrd.bufferValue(min5ago_int,512)
        this_rrd.bufferValue(now_int,612)
        this_rrd.update()
        
        rrd2 = RRD(RRDFILENAME,mode="r")
        self.assertTrue(rrd2)
        self.assertEquals(len(rrd2.ds),1)
        data_dict1 = rrd2.ds[0].getData()
        self.assertEquals(data_dict1['name'],DSNAME)
        self.assertEquals(data_dict1['last_ds'],612)
    #
    def test_ds_value_again(self):
        """test ds value in RRD after multiple updates, again...
        http://code.google.com/p/pyrrd/issues/detail?id=18"""
        nuke_base_rrd()
        create_base_rrd()
        this_rrd = RRD(RRDFILENAME)
        #convert datetime object to seconds since epoch for RRD...
        now = datetime.datetime.now()
        now_int = epoch(now)
        min5ago_int = epoch(now-datetime.timedelta(minutes=5))
        min10ago_int = epoch(now-datetime.timedelta(minutes=10))
        min15ago_int = epoch(now-datetime.timedelta(minutes=15))
        min20ago_int = epoch(now-datetime.timedelta(minutes=20))
        min25ago_int = epoch(now-datetime.timedelta(minutes=25))
        min30ago_int = epoch(now-datetime.timedelta(minutes=30))
        this_rrd.bufferValue(min30ago_int,12)
        this_rrd.bufferValue(min25ago_int,112)
        this_rrd.bufferValue(min20ago_int,212)
        this_rrd.bufferValue(min15ago_int,312)
        this_rrd.bufferValue(min10ago_int,412)
        this_rrd.bufferValue(min5ago_int,512)
        this_rrd.bufferValue(now_int,612)
        this_rrd.update()
        
        rrd2 = RRD(RRDFILENAME,mode="r")
        self.assertTrue(rrd2)
        self.assertEquals(len(rrd2.ds),1)
        data_dict1 = rrd2.ds[0].getData()
        self.assertEquals(data_dict1['name'],DSNAME)
        self.assertEquals(data_dict1['last_ds'],612)
    #
                
if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromTestCase(PyRRDTests)
    unittest.TextTestRunner(verbosity=2).run(suite)
    nuke_base_rrd()

