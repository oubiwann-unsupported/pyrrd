import re
from datetime import datetime

from utils import epoch
from backend import rrdbackend

def validateDSName(name):
    '''
    >>> vname = validateDSName('Zaphod Beeble-Brox!')
    Traceback (most recent call last):
    ValueError: Names must consist only of the characters A-Z, a-z, 0-9, _
    >>> vname = validateDSName('Zaphod_Bee_Brox')
    >>> vname = validateDSName('a'*18)
    >>> vname = validateDSName('a'*19)
    Traceback (most recent call last):
    ValueError: Names must be shorter than 19 characters
    '''
    if name != re.sub('[^A-Za-z0-9_]', '', name):
        raise ValueError, "Names must consist only of the characters " + \
            "A-Z, a-z, 0-9, _"
    if len(name) > 18:
        raise ValueError, "Names must be shorter than 19 characters"

def validateDSType(dstype):
    '''
    >>> validateDSType('counter')
    'COUNTER'
    >>> validateDSType('ford prefect')
    Traceback (most recent call last):
    ValueError: A data source type must be one of the following: GAUGE COUNTER DERIVE ABSOLUTE COMPUTE
    '''
    dstype = dstype.upper()
    valid = ['GAUGE', 'COUNTER', 'DERIVE', 'ABSOLUTE', 'COMPUTE']
    if dstype in valid:
        return dstype
    else:
        valid = ' '.join(valid)
        raise ValueError, 'A data source type must be one of the ' + \
            'following: %s' % valid

def validateRRACF(consolidation_function):
    '''
    >>> validateRRACF('Max')
    'MAX'
    >>> validateRRACF('Maximum')
    Traceback (most recent call last):
    ValueError: An RRA's consolidation function must be one of the following: AVERAGE MIN MAX LAST HWPREDICT SEASONAL DEVSEASONAL DEVPREDICT FAILURES
    >>> validateRRACF('Trisha MacMillan')
    Traceback (most recent call last):
    ValueError: An RRA's consolidation function must be one of the following: AVERAGE MIN MAX LAST HWPREDICT SEASONAL DEVSEASONAL DEVPREDICT FAILURES
    '''
    cf = consolidation_function.upper()
    valid = ['AVERAGE', 'MIN', 'MAX', 'LAST', 'HWPREDICT', 'SEASONAL',
        'DEVSEASONAL', 'DEVPREDICT', 'FAILURES']
    if cf in valid:
        return cf
    else:
        valid = ' '.join(valid)
        raise ValueError, "An RRA's consolidation function must be " + \
            "one of the following: %s" % valid

class RRD(object):
    '''
    >>> dss = []
    >>> rras = []
    >>> filename = '/tmp/test.rrd'
    >>> dss.append(DataSource(dsName='speed', dsType='COUNTER', heartbeat=600))
    >>> rras.append(RRA(cf='AVERAGE', xff=0.5, steps=1, rows=24))
    >>> rras.append(RRA(cf='AVERAGE', xff=0.5, steps=6, rows=10))
    >>> my_rrd = RRD(filename, ds=dss, rra=rras, start=920804400)
    >>> my_rrd.create()
    >>> import os
    >>> os.path.exists(filename)
    True
    >>> my_rrd.bufferValue('920805600', '12363')
    >>> my_rrd.bufferValue('920805900', '12363')
    >>> my_rrd.bufferValue('920806200', '12373')
    >>> my_rrd.bufferValue('920806500', '12383')
    >>> my_rrd.update()
    >>> my_rrd.bufferValue('920806800', '12393')
    >>> my_rrd.bufferValue('920807100', '12399')
    >>> my_rrd.bufferValue('920807400', '12405')
    >>> my_rrd.bufferValue('920807700', '12411')
    >>> my_rrd.bufferValue('920808000', '12415')
    >>> my_rrd.bufferValue('920808300', '12420')
    >>> my_rrd.bufferValue('920808600', '12422')
    >>> my_rrd.bufferValue('920808900', '12423')
    >>> my_rrd.update()
    >>> len(my_rrd.values)
    0
    >>> os.unlink(filename)
    >>> os.path.exists(filename)
    False
    '''
    #>>> os.unlink(filename)
    def __init__(self, filename, start=None, step=300, ds=[], rra=[]):
        self.filename = filename
        if not start or isinstance(start, datetime):
            self.start = epoch(start)
        else:
            self.start = start
        self.ds = ds
        self.rra = rra
        self.values = []
        self.step = step

    def create(self, debug=False):
        data = rrdbackend.prepareObject('create', self)
        if debug: print data
        rrdbackend.create(*data)

    def bufferValue(self, time_or_data, *values):
        '''
        The parameter 'values' can either be a an n-tuple, but it
        is assumed that the order in which the values are sent is
        the order in which they will be applied to the DSs (i.e.,
        respectively... i.e., in the order that the DSs were added
        to the RRD).

        >>> my_rrd = RRD('somefile')
        >>> my_rrd.bufferValue('sometime', 'value')
        >>> my_rrd.update(debug=True, dry_run=True)
        ('somefile', ' sometime:value')
        >>> my_rrd.update(template='ds0', debug=True, dry_run=True)
        ('somefile', '--template ds0 sometime:value')
        >>> my_rrd.values = []

        >>> my_rrd.bufferValue('sometime:value')
        >>> my_rrd.update(debug=True, dry_run=True)
        ('somefile', ' sometime:value')
        >>> my_rrd.update(template='ds0', debug=True, dry_run=True)
        ('somefile', '--template ds0 sometime:value')
        >>> my_rrd.values = []

        >>> my_rrd.bufferValue('sometime', 'value1', 'value2')
        >>> my_rrd.bufferValue('anothertime', 'value3', 'value4')
        >>> my_rrd.update(debug=True, dry_run=True)
        ('somefile', ' sometime:value1:value2 anothertime:value3:value4')
        >>> my_rrd.update(template='ds1:ds0', debug=True, dry_run=True)
        ('somefile', '--template ds1:ds0 sometime:value1:value2 anothertime:value3:value4')
        >>> my_rrd.values = []

        >>> my_rrd.bufferValue('sometime:value')
        >>> my_rrd.bufferValue('anothertime:anothervalue')
        >>> my_rrd.update(debug=True, dry_run=True)
        ('somefile', ' sometime:value anothertime:anothervalue')
        >>> my_rrd.update(template='ds0', debug=True, dry_run=True)
        ('somefile', '--template ds0 sometime:value anothertime:anothervalue')
        >>> my_rrd.values = []
        '''
        values = ':'.join([ str(x) for x in values ])
        self.values.append((time_or_data, values))
    bufferValues = bufferValue

    def update(self, debug=False, template=None, dry_run=False):
        '''
        '''
        # XXX this needs a lot more testing with different data
        # sources and values
        self.template = template
        if self.values:
            data = rrdbackend.prepareObject('update', self)
            if debug: print data
            if not dry_run:
                rrdbackend.update(debug=debug, *data)
                self.values = []

    def fetch(self):
        '''
        '''
        # XXX obviously, we need to imnplement this

class DataSource(object):
    '''
    A single RRD can accept input from several data sources (DS),
    for example incoming and outgoing traffic on a specific
    communication line. With the DS configuration option you must
    define some basic properties of each data source you want to
    store in the RRD.

    ds-name is the name you will use to reference this particular
    data source from an RRD. A ds-name must be 1 to 19 characters
    long in the characters [a-zA-Z0-9_].

    DST defines the Data Source Type. The remaining arguments of a
    data source entry depend on the data source type. For GAUGE,
    COUNTER, DERIVE, and ABSOLUTE the format for a data source entry
    is:

        DS:ds-name:GAUGE | COUNTER | DERIVE | ABSOLUTE:heartbeat:min:max

    For COMPUTE data sources, the format is:

        DS:ds-name:COMPUTE:rpn-expression

    >>> ds = DataSource(dsName='speed', dsType='COUNTER', heartbeat=600)
    >>> ds
    DS:speed:COUNTER:600:U:U
    '''
    def __init__(self, dsName, dsType, heartbeat=None, minval='U',
        maxval='U', rpn=None):
        self.name = dsName
        self.type = dsType
        self.heartbeat = int(heartbeat)
        self.min = minval
        self.max = maxval
        self.rpn = rpn

    def __repr__(self):
        '''
        We override this method for preparing the class's data for
        use with RRDTool.

        Time representations must have their ':'s escaped, since
        the colon is the RRDTool separator for parameters.
        '''
        main = 'DS:%(name)s:%(type)s' % self.__dict__
        tail = ''
        if self.type == 'COMPUTE':
            tail += ':%s' % self.rpn
        else:
            tail += ':%(heartbeat)s:%(min)s:%(max)s' % self.__dict__
        return main+tail
DS = DataSource

class RRA(object):
    '''
    The purpose of an RRD is to store data in the round robin
    archives (RRA). An archive consists of a number of data values
    or statistics for each of the defined data-sources (DS) and is
    defined with an RRA line.

    When data is entered into an RRD, it is first fit into time
    slots of the length defined with the -s option, thus becoming
    a primary data point.

    The data is also processed with the consolidation function (CF)
    of the archive. There are several consolidation functions that
    consolidate primary data points via an aggregate function:
    AVERAGE, MIN, MAX, LAST. The format of RRA line for these
    consolidation functions is:

        RRA:AVERAGE | MIN | MAX | LAST:xff:steps:rows

    xff The xfiles factor defines what part of a consolidation
    interval may be made up from *UNKNOWN* data while the consolidated
    value is still regarded as known.

    steps defines how many of these primary data points are used
    to build a consolidated data point which then goes into the
    archive.

    rows defines how many generations of data values are kept in
    an RRA.

    >>> rra1 = RRA(cf='AVERAGE', xff=0.5, steps=1, rows=24)
    >>> rra1
    RRA:AVERAGE:0.5:1:24
    >>> rra2 = RRA(cf='AVERAGE', xff=0.5, steps=6, rows=10)
    >>> rra2
    RRA:AVERAGE:0.5:6:10
    '''
    def __init__(self, cf, xff=None, steps=None, rows=None, alpha=None,
        beta=None, seasonal_period=None, rra_num=None, gamma=None,
        threshold=None, window_length=None):
        self.cf = cf
        self.xff = xff
        self.steps = steps
        self.rows = rows
        self.alpha = alpha
        self.beta = beta
        self.gamma = gamma
        self.seasonal_period = seasonal_period
        self.rra_num = rra_num
        self.threshold = threshold
        self.window_length = window_length

    def __repr__(self):
        '''
        We override this method for preparing the class's data for
        use with RRDTool.

        Time representations must have their ':'s escaped, since
        the colon is the RRDTool separator for parameters.
        '''
        main = 'RRA:%(cf)s' % self.__dict__
        tail = ''
        if self.cf in ['AVERAGE', 'MIN', 'MAX', 'LAST']:
            tail += ':%(xff)s:%(steps)s:%(rows)s' % self.__dict__
        elif self.cf == 'HWPREDICT':
            tail += ':%(rows)s:%(alpha)s:%(beta)s' % self.__dict__
            tail += ':%(seasonal_period)s:%(rra_num)s' % self.__dict__
        elif self.cf == 'SEASONAL':
            tail += ':%(seasonal_period)s:%(gamma)s:%(rra_num)s' % (
                self.__dict__)
        elif self.cf == 'DEVSEASONAL':
            tail += ':%(seasonal_period)s:%(gamma)s:%(rra_num)s' % (
                self.__dict__)
        elif self.cf == 'DEVPREDICT':
            tail += ':%(rows)s:%(rra_num)s' % self.__dict__
        elif self.cf == 'FAILURES':
            tail += ':%(rows)s:%(threshold)s' % self.__dict__
            tail += ':%(window_length)s:%(rra_num)s' % self.__dict__
        return main+tail

class Query(object):
    pass

def _test():
    import doctest, rrd
    return doctest.testmod(rrd)

if __name__ == '__main__':
    _test()

