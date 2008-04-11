from math import sin
from random import random

from pyrrd.rrd import RRD, RRA, DS
from pyrrd.graph import DEF, CDEF, VDEF
from pyrrd.graph import LINE, AREA, GPRINT
from pyrrd.graph import ColorAttributes, Graph

exampleNum = 3
filename = 'example%s.rrd' % exampleNum
graphfile = 'example%s.png' % exampleNum
graphfile_lg = 'example%s-large.png' % exampleNum

day = 24 * 60 * 60
week = 7 * day
month = day * 30
quarter = month * 3
half = 365 * day / 2
year = 365 * day

startTime = 1122876000
endTime = 1136012400
step = 300
maxSteps = int((endTime-startTime)/step)

# Let's create and RRD file and dump some data in it
dss = []
rras = []
ds1 = DS(dsName='speed', dsType='GAUGE', heartbeat=900)
dss.append(ds1)
rra1 = RRA(cf='AVERAGE', xff=0.5, steps=24, rows=1460)
rras.append(rra1)

myRRD = RRD(filename, ds=dss, rra=rras, start=startTime)
myRRD.create()

# let's generate some data...
currentTime = startTime
for i in xrange(maxSteps):
    currentTime += step
    # lets update the RRD/purge the buffer ever 100 entires
    if i % 100 == 0 and myRRD.values:
        #print "updating RRD..."
        myRRD.update(debug=False)
    # let's do periodic values
    value = int(sin(i % 200) * 1000)
    myRRD.bufferValue(currentTime, value)
# add anything remaining in the buffer
myRRD.update()

# Let's set up the objects that will be added to the graph
def1 = DEF(rrdfile=myRRD.filename, vname='myspeed', dsName=ds1.name)
vdef1 = VDEF(vname='myavg', rpn='%s,AVERAGE' % def1.vname)
area1 = AREA(defObj=def1, color='#FFA902', legend='Raw Data')
line1 = LINE(defObj=vdef1, color='#01FF13', legend='Average', stack=True)

# Let's configure some custom colors for the graph
ca = ColorAttributes()
ca.back = '#333333'
ca.canvas = '#333333'
ca.shadea = '#000000'
ca.shadeb = '#111111'
ca.mgrid = '#CCCCCC'
ca.axis = '#FFFFFF'
ca.frame = '#AAAAAA'
ca.font = '#FFFFFF'
ca.arrow = '#FFFFFF'

# Now that we've got everything set up, let's make a graph
startTime = endTime - 3 * month
g = Graph(graphfile, start=startTime, end=endTime, vertical_label='data', color=ca)
g.data.extend([def1, vdef1, area1])
g.write()

g = Graph(graphfile_lg, start=startTime, end=endTime, vertical_label='data', color=ca)
g.width = 800
g.height = 400
g.data.extend([def1, vdef1, area1])
g.write()
