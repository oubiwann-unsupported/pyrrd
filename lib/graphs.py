import rrdtool



class RRDGrapher:
    '''
    from rrd import RRDGrapher
    g = RRDGrapher()    
    g.setFilename('/home/oubiwann/public_html/test.gif')
    g.setFilename('test.gif')
    g.setStartSeconds('920804400')
    g.setEndSeconds('920808000')
    g.setSourceRRD('test.rrd')
    g.setDataSourceName('speed')
    g.setConsolidationFunction('AVERAGE')
    g.setVirtualName('myspeed')
    g.setLine2('myspeed', '#FF0000')
    g.generateImage()

    or

    from rrd import RRDGrapher
    g = RRDGrapher(filename='test.gif', s='920804400', e='920808000', rrd='test.rrd',
    dsn='speed', cf='AVERAGE', vname='myspeed')
    g.setLine2('myspeed', '#FF0000')
    g.generateImage()

    '''

    def __init__(self, filename=None, s=None, e=None, t=None, rrd=None, dsn=None, 
        cf=None, vname=None):

        self.filename = filename

        self.setStartSeconds(s)
        self.setEndSeconds(e)
        self.setTitle(t)
        self.setSourceRRD(rrd)
        self.setDataSourceName(dsn)
        self.setConsolidationFunction(cf)
        self.setVirtualName(vname)

        self.minor_grid = True
        self.height = 100
        self.width = 400
        self.interlaced = False
        self.imgformat = 'PNG'
        self.legend = True

    def setStartSeconds(self, seconds):
        if seconds:
            self.start_seconds = '--start=%s' % seconds
        else:
            self.start_seconds = None

    def setEndSeconds(self, seconds):
        if seconds:
            self.end_seconds = '--end=%s' % seconds
        else:
            self.end_seconds = None

    def setFilename(self, filename):
        self.filename = filename

    def setTitle(self, title=None):
        if title:
            self.title = '--title=%s' % title

    def setVirtualName(self, name):
        if name:
            self.virtual_name = 'DEF:%s=%s:%s:%s' % (name, self.source_rrd, self.data_source_name, self.consolidation_function)

    def setSourceRRD(self, filename):
        self.source_rrd = filename

    def setDataSourceName(self, name):
        self.data_source_name = name

    def setConsolidationFunction(self, cf):
        if cf:
            self.consolidation_function = cf

    def setVirtualDataSource(self, rpn_expression):
        if rpn_expression:
            self.virtual_data_source = 'CDEF:%s=%s' % (self.virtual_name, rpn_expression)

    def _setLine(self, number, virtual_name, color='', legend=''):
        if legend:
            legend = ':%s' % legend
        return 'LINE%s:%s%s%s' % (number, virtual_name, color, legend)

    def setLine1(self, virtual_name, color='', legend=''):
        self.line1 = self._setLine('1', virtual_name, color, legend)

    def setLine2(self, virtual_name, color='', legend=''):
        self.line2 = self._setLine('2', virtual_name, color, legend)

    def setLine3(self, virtual_name, color='', legend=''):
        self.line3 = self._setLine('3', virtual_name, color, legend)

    def getImageType(self):
        pass

    def setColors(self):
        pass

    def getHours(self):
        pass

    def getDuration(self):
        pass

    def getWidth(self):
        pass

    def getHeight(self):
        pass

    def getTotal(self):
        pass

    def getDebug(self):
        pass

    def generateImage(self):
        if self.start_seconds and self.end_seconds:
            rrdtool.graph(self.filename, self.start_seconds, self.end_seconds,
                self.virtual_name, self.line2)
        else:   
            rrdtool.graph(self.filename, self.virtual_name, self.line2)
