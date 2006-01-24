from math import sin, pi
from random import random

from pyrrd.rrd import RRD, RRA, DS
from pyrrd.graph import DEF, CDEF, VDEF
from pyrrd.graph import LINE, AREA, GPRINT
from pyrrd.graph import ColorAttributes, Graph

example_no = 4
filename = 'example%s.rrd' % example_no
graphfile = 'example%s.png' % example_no
graphfile_lg = 'example%s-large.png' % example_no

day = 24 * 60 * 60
week = 7 * day
month = day * 30
quarter = month * 3
half = 365 * day / 2
year = 365 * day

start_time = 1122876000
end_time = 1136012400
step = 300
max_steps = int((end_time-start_time)/step)

# Let's create and RRD file and dump some data in it
dss = []
ds1 = DS(ds_name='speed', ds_type='GAUGE', heartbeat=900)
ds2 = DS(ds_name='silliness', ds_type='GAUGE', heartbeat=900)
ds3 = DS(ds_name='insanity', ds_type='GAUGE', heartbeat=900)
ds4 = DS(ds_name='dementia', ds_type='GAUGE', heartbeat=900)
dss.extend([ds1, ds2, ds3, ds4])

rras = []
rra1 = RRA(cf='AVERAGE', xff=0.5, steps=24, rows=1460)
rras.append(rra1)

my_rrd = RRD(filename, ds=dss, rra=rras, start=start_time)
my_rrd.create()

# let's generate some data...
current_time = start_time
for i in xrange(max_steps):
    current_time += step
    # lets update the RRD/purge the buffer ever 100 entires
    if i % 100 == 0:
        my_rrd.update(debug=False)
    # let's do two different sets of periodic values
    value1 = int(sin(i % 200) * 1000)
    value2 = int(sin( (i % 2000)/(200*random()) ) * 200)
    value3 = int(sin( (i % 4000)/(400*random()) ) * 400)
    value4 = int(sin( (i % 6000)/(600*random()) ) * 600)
    # when you pass more than one value to update buffer like this,
    # they get applied to the DSs in the order that the DSs were
    # "defined" or added to the RRD object.
    my_rrd.bufferValue(current_time, value1, value2, value3, value4)
# add anything remaining in the buffer
my_rrd.update()

# Let's set up the objects that will be added to the graph
def1 = DEF(rrdfile=my_rrd.filename, vname='myspeed', ds_name=ds1.name)
def2 = DEF(rrdfile=my_rrd.filename, vname='mysilliness', ds_name=ds2.name)
def3 = DEF(rrdfile=my_rrd.filename, vname='myinsanity', ds_name=ds3.name)
def4 = DEF(rrdfile=my_rrd.filename, vname='mydementia', ds_name=ds4.name)
vdef1 = VDEF(vname='myavg', rpn='%s,AVERAGE' % def1.vname)
area1 = AREA(def_obj=def1, color='#FFA902', legend='Raw Data 4')
area2 = AREA(def_obj=def2, color='#DA7202', legend='Raw Data 3')
area3 = AREA(def_obj=def3, color='#BD4902', legend='Raw Data 2')
area4 = AREA(def_obj=def4, color='#A32001', legend='Raw Data 1')
line1 = LINE(def_obj=vdef1, color='#01FF13', legend='Average', stack=True)

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
start_time = end_time - 3 * month
g = Graph(graphfile, start=start_time, end=end_time, vertical_label='data', color=ca)
g.data.extend([def1, def2, def3, def4, vdef1, area4, area3, area2, area1])
g.write()

g.filename = graphfile_lg
g.width = 800
g.height = 400
g.write()
