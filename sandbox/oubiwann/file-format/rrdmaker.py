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
rra2 = RRA(cf='AVERAGE', xff=0.5, steps=6, rows=10)
rras.extend([rra1, rra2])
myRRD = RRD(filename, ds=dss, rra=rras, start=920804400)
myRRD.create()
myRRD.bufferValue('920805600', '12363')
myRRD.bufferValue('920805900', '12363')
myRRD.bufferValue('920806200', '12373')
myRRD.bufferValue('920806500', '12383')
myRRD.bufferValue('920806800', '12393')
myRRD.bufferValue('920807100', '12399')
myRRD.bufferValue('920807400', '12405')
myRRD.bufferValue('920807700', '12411')
myRRD.bufferValue('920808000', '12415')
myRRD.bufferValue('920808300', '12420')
myRRD.bufferValue('920808600', '12422')
myRRD.bufferValue('920808900', '12423')
myRRD.update()
