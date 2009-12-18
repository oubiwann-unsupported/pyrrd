import os

from pyrrd.rrd import RRD, RRA, DS
from pyrrd.graph import DEF, CDEF, VDEF
from pyrrd.graph import LINE, AREA, GPRINT
from pyrrd.graph import ColorAttributes, Graph


filename = '%s.rrd' % os.path.splitext(os.path.basename(__file__))[0]

# Let's create and RRD file and dump some data in it
dss = []
rras = []
ds1 = DS(dsName='speed', dsType='COUNTER', heartbeat=600)
dss.append(ds1)
rra1 = RRA(cf='AVERAGE', xff=0.5, steps=1, rows=24)
rras.extend([rra1])
myRRD = RRD(filename, ds=dss, rra=rras, start=920804400)
myRRD.create()
myRRD.bufferValue('920805600', '12363')
myRRD.update()
