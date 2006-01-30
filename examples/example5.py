from math import sin, pi
from random import random

from pyrrd.rrd import RRD, RRA, DS
from pyrrd.graph import DEF, CDEF, VDEF
from pyrrd.graph import LINE, AREA, GPRINT
from pyrrd.graph import ColorAttributes, Graph

example_no = 5
filename = 'example%s.rrd' % example_no
datafile = 'example%s.data' % example_no
graphfile = 'example%s-%s.png'
graphfile_lg = 'example%s-%s-large.png'

hour = 60 * 60
day = 24 * hour
week = 7 * day
month = day * 30
quarter = month * 3
half = 365 * day / 2
year = 365 * day
times = [(3*hour,60), (12*hour,60), (day,60), (3*day,300)]

step = 60
start_time = 1138259700
end_time = 1138573200
max_steps = int((end_time-start_time)/step)

# Let's create and RRD file and dump some data in it
dss = []
ds1 = DS(ds_name='ds_in_pkts', ds_type='ABSOLUTE', heartbeat=900)
ds2 = DS(ds_name='ds_in_bits', ds_type='ABSOLUTE', heartbeat=900)
ds3 = DS(ds_name='ds_out_pkts', ds_type='ABSOLUTE', heartbeat=900)
ds4 = DS(ds_name='ds_out_bits', ds_type='ABSOLUTE', heartbeat=900)
dss.extend([ds1, ds2, ds3, ds4])

rras = []
# 1 days-worth of one-minute samples --> 60/1 * 24
rra1 = RRA(cf='AVERAGE', xff=0, steps=1, rows=1440) 
# 3 days-worth of five-minute samples --> 60/5 * 24 * 3
rra2 = RRA(cf='AVERAGE', xff=0, steps=5, rows=864)
# 30 days-worth of five-minute samples --> 60/60 * 24 * 30
rra3 = RRA(cf='AVERAGE', xff=0, steps=60, rows=720)
rras.extend([rra1, rra2, rra3])

my_rrd = RRD(filename, step=step, ds=dss, rra=rras, start=start_time)
my_rrd.create(debug=False)

# Let's suck in that data... the data file has the following format:
#  DS TIME:VALUE [TIME:VALUE [TIME:VALUE]...]
# and the lines are in a completely arbitrary order.
data = {}
# First, we need to get everything indexed by time
for line in open(datafile).readlines():
    line = line.strip()
    line_parts = line.split(' ')
    ds_name = line_parts[0]
    for timedatum in line_parts[1:]:
        time, datum = timedatum.split(':')
        # For each time index, let's have a dict
        data.setdefault(time, {})
        # Now let's add the DS names and its data for this time to the 
        # dict we just created
        data[time].setdefault(ds_name, datum)

# Sort everything by time
counter = 0
sorted_data = [ (i,data[i]) for i in sorted(data.keys()) ]
for time, ds_names in sorted_data:
    counter += 1
    val1 = ds_names.get(ds1.name) or 'U'
    val2 = ds_names.get(ds2.name) or 'U'
    val3 = ds_names.get(ds3.name) or 'U'
    val4 = ds_names.get(ds4.name) or 'U'
    # Add the values
    my_rrd.bufferValue(time, val1, val2, val3, val4)
    # Lets update the RRD/purge the buffer ever 100 entires
    if counter % 100 == 0:
        my_rrd.update(debug=False)

# Add anything remaining in the buffer
my_rrd.update(debug=False)

# Let's set up the objects that will be added to the graph
def1 = DEF(rrdfile=my_rrd.filename, vname='in', ds_name=ds1.name)
def2 = DEF(rrdfile=my_rrd.filename, vname='out', ds_name=ds2.name)
# Here we're just going to mulitply the in bits by 100, solely for
# the purpose of display
cdef1 = CDEF(vname='tenin', rpn='%s,%s,*' % (def1.vname, 100))
cdef2 = CDEF(vname='negout', rpn='%s,-1,*' % def2.vname)
area1 = AREA(def_obj=cdef1, color='#FFA902', legend='Bits In')
area2 = AREA(def_obj=cdef2, color='#A32001', legend='Bits Out')

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
g = Graph('dummy.png', end=end_time, vertical_label='Bits', 
    color=ca)
g.data.extend([def1, def2, cdef1, cdef2, area2, area1])

# Iterate through the different resoltions for which we want to 
# generate graphs.
for time, step in times:
    # First, the small graph
    g.filename = graphfile % (example_no, time)
    g.width = 400
    g.height = 100
    g.start=end_time - time
    g.step = step
    g.write(debug=False)
    
    # Then the big one
    g.filename = graphfile_lg % (example_no, time)
    g.width = 800
    g.height = 400
    g.write()
