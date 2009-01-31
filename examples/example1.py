from pyrrd.rrd import RRD, RRA, DS
from pyrrd.graph import DEF, CDEF, VDEF
from pyrrd.graph import LINE, AREA, GPRINT
from pyrrd.graph import ColorAttributes, Graph

exampleNum = 1
filename = 'example%s.rrd' % exampleNum
graphfile = 'example%s.png' % exampleNum

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

# Let's set up the objects that will be added to the graph
def1 = DEF(rrdfile=myRRD.filename, vname='myspeed', dsName=ds1.name)
cdef1 = CDEF(vname='kmh', rpn='%s,3600,*' % def1.vname)
cdef2 = CDEF(vname='fast', rpn='kmh,100,GT,kmh,0,IF')
cdef3 = CDEF(vname='good', rpn='kmh,100,GT,0,kmh,IF')
vdef1 = VDEF(vname='mymax', rpn='%s,MAXIMUM' % def1.vname)
vdef2 = VDEF(vname='myavg', rpn='%s,AVERAGE' % def1.vname)
line1 = LINE(value=100, color='#990000', legend='Maximum Allowed')
area1 = AREA(defObj=cdef3, color='#006600', legend='Good Speed')
area2 = AREA(defObj=cdef2, color='#CC6633', legend='Too Fast')
line2 = LINE(defObj=vdef2, color='#000099', legend='My Average', stack=True)
gprint1 = GPRINT(vdef2, '%6.2lf kph')

# Now that we've got everything set up, let's make a graph
g = Graph(graphfile, start=920805000, end=920810000, vertical_label='km/h')
g.data.extend([def1, cdef1, cdef2, cdef3, vdef1, vdef2, line1, area1, area2, line2, gprint1])
g.write()
