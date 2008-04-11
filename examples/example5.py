from math import sin, pi
from random import random

from pyrrd.rrd import RRD, RRA, DS
from pyrrd.graph import DEF, CDEF, VDEF
from pyrrd.graph import LINE, AREA, GPRINT
from pyrrd.graph import ColorAttributes, Graph

exampleNum = 5
filename = 'example%s.rrd' % exampleNum
datafile = 'example%s.data' % exampleNum
graphfile = 'example%s-%s.png'
graphfileLg = 'example%s-%s-large.png'

hour = 60 * 60
day = 24 * hour
week = 7 * day
month = day * 30
quarter = month * 3
half = 365 * day / 2
year = 365 * day
times = [(3*hour,60), (12*hour,60), (day,60), (3*day,300)]

step = 60
startTime = 1138259700
endTime = 1138573200
maxSteps = int((endTime-startTime)/step)

# Let's setup some data sources for our RRD
dss = []
ds1 = DS(dsName='ds_in_pkts', dsType='ABSOLUTE', heartbeat=900)
ds2 = DS(dsName='ds_in_bits', dsType='ABSOLUTE', heartbeat=900)
ds3 = DS(dsName='ds_out_pkts', dsType='ABSOLUTE', heartbeat=900)
ds4 = DS(dsName='ds_out_bits', dsType='ABSOLUTE', heartbeat=900)
dss.extend([ds1, ds2, ds3, ds4])

# An now let's setup how our RRD will archive the data
rras = []
# 1 days-worth of one-minute samples --> 60/1 * 24
rra1 = RRA(cf='AVERAGE', xff=0, steps=1, rows=1440) 
# 7 days-worth of five-minute samples --> 60/5 * 24 * 7
rra2 = RRA(cf='AVERAGE', xff=0, steps=5, rows=2016)
# 30 days-worth of five-minute samples --> 60/60 * 24 * 30
rra3 = RRA(cf='AVERAGE', xff=0, steps=60, rows=720)
rras.extend([rra1, rra2, rra3])

# With those setup, we can now created the RRD
myRRD = RRD(filename, step=step, ds=dss, rra=rras, start=startTime)
myRRD.create(debug=False)

# Let's suck in that data... the data file has the following format:
#  DS TIME:VALUE [TIME:VALUE [TIME:VALUE]...]
# and the lines are in a completely arbitrary order.
data = {}
# First, we need to get everything indexed by time
for line in open(datafile).readlines():
    line = line.strip()
    lineParts = line.split(' ')
    dsName = lineParts[0]
    for timedatum in lineParts[1:]:
        time, datum = timedatum.split(':')
        # For each time index, let's have a dict
        data.setdefault(time, {})
        # Now let's add the DS names and its data for this time to the 
        # dict we just created
        data[time].setdefault(dsName, datum)

# Sort everything by time
counter = 0
sortedData = [ (i,data[i]) for i in sorted(data.keys()) ]
for time, dsNames in sortedData:
    counter += 1
    val1 = dsNames.get(ds1.name) or 'U'
    val2 = dsNames.get(ds2.name) or 'U'
    val3 = dsNames.get(ds3.name) or 'U'
    val4 = dsNames.get(ds4.name) or 'U'
    # Add the values
    myRRD.bufferValue(time, val1, val2, val3, val4)
    # Lets update the RRD/purge the buffer ever 100 entires
    if counter % 100 == 0:
        myRRD.update(debug=False)

# Add anything remaining in the buffer
myRRD.update(debug=False)

# Let's set up the objects that will be added to the graph
def1 = DEF(rrdfile=myRRD.filename, vname='in', dsName=ds1.name)
def2 = DEF(rrdfile=myRRD.filename, vname='out', dsName=ds2.name)
# Here we're just going to mulitply the in bits by 100, solely for
# the purpose of display
cdef1 = CDEF(vname='hundredin', rpn='%s,%s,*' % (def1.vname, 100))
cdef2 = CDEF(vname='negout', rpn='%s,-1,*' % def2.vname)
area1 = AREA(defObj=cdef1, color='#FFA902', legend='Bits In')
area2 = AREA(defObj=cdef2, color='#A32001', legend='Bits Out')

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
g = Graph('dummy.png', end=endTime, vertical_label='Bits', 
    color=ca)
g.data.extend([def1, def2, cdef1, cdef2, area2, area1])
g.title = '"In- and Out-bound Traffic Across Local Router"'
#g.logarithmic = ' '

# Iterate through the different resoltions for which we want to 
# generate graphs.
for time, step in times:
    # First, the small graph
    g.filename = graphfile % (exampleNum, time)
    g.width = 400
    g.height = 100
    g.start=endTime - time
    g.step = step
    g.write(debug=False)
    
    # Then the big one
    g.filename = graphfileLg % (exampleNum, time)
    g.width = 800
    g.height = 400
    g.write()
