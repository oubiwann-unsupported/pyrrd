import re

def validateVName(name):
    '''
    RRDTool vnames must be made up strings of the following characters:
         A-Z, a-z, 0-9, -,_ 
    and have a maximum length of 255 characters.
    >>> vname = validateVName('Zaphod Beeble-Brox!')
    Traceback (most recent call last):
    ValueError: Names must consist only of the characters A-Z, a-z, 0-9, -, _
    >>> vname = validateVName('Zaphod_Beeble-Brox')
    >>> vname = validateVName('a'*32)
    >>> vname = validateVName('a'*254)
    >>> vname = validateVName('a'*255)
    >>> vname = validateVName('a'*256)
    Traceback (most recent call last):
    ValueError: Names must be shorter than 255 characters
    '''
    if name != re.sub('[^A-Za-z0-9_-]', '', name):
        raise ValueError, "Names must consist only of the characters " + \
            "A-Z, a-z, 0-9, -, _"
    if len(name) > 255:
        raise ValueError, "Names must be shorter than 255 characters"
    return name

class DataDefinition(object):
    '''
    This object causes data to be fetched from the RRD file. The
    virtual name vname can then be used throughout the rest of the
    script. By default, an RRA which contains the correct consolidated
    data at an appropriate resolution will be chosen. The resolution
    can be overridden with the --step option. The resolution can
    again be overridden by specifying the step size. The time span
    of this data is the same as for the graph by default, you can
    override this by specifying start and end. Remember to escape
    colons in the time specification!
    
    If the resolution of the data is higher than the resolution of
    the graph, the data will be further consolidated. This may
    result in a graph that spans slightly more time than requested.
    Ideally each point in the graph should correspond with one CDP
    from an RRA. For instance, if your RRD has an RRA with a
    resolution of 1800 seconds per CDP, you should create an image
    with width 400 and time span 400*1800 seconds (use appropriate
    start and end times, such as --start end-8days8hours).
    
    If consolidation needs to be done, the CF of the RRA specified
    in the DEF itself will be used to reduce the data density. This
    behaviour can be changed using :reduce=<CF>. This optional
    parameter specifies the CF to use during the data reduction
    phase.
    
    >>> def1 = DataDefinition(vname='ds0a', 
    ... rrdfile='/home/rrdtool/data/router1.rrd', ds_name='ds0',
    ... cdef='AVERAGE')
    >>> def1
    DEF:ds0a=/home/rrdtool/data/router1.rrd:ds0:AVERAGE
    >>> def1.__repr__()
    'DEF:ds0a=/home/rrdtool/data/router1.rrd:ds0:AVERAGE'

    >>> def2 = DataDefinition(rrdfile='/home/rrdtool/data/router1.rrd')
    >>> def2.vname = 'ds0b'
    >>> def2.ds_name = 'ds0'
    >>> def2.cdef = 'AVERAGE'
    >>> def2.step = 1800
    >>> def2
    DEF:ds0b=/home/rrdtool/data/router1.rrd:ds0:AVERAGE:step=1800

    >>> def3 = DEF(vname='ds0c', ds_name='ds0', step=7200)
    >>> def3.rrdfile = '/home/rrdtool/data/router1.rrd'
    >>> def3
    DEF:ds0c=/home/rrdtool/data/router1.rrd:ds0:AVERAGE:step=7200
    '''
    def __init__(self, vname='', rrdfile='', ds_name='', cdef='AVERAGE',
        step=None, start=None, end=None, reduce=None):
        self.vname = validateVName(vname)
        self.rrdfile = rrdfile
        self.ds_name = ds_name
        self.cdef = cdef
        self.step = step
        self.start = start
        self.end = end
        self.reduce = reduce

    def __repr__(self):
        '''
	We override this method for preparing the class's data for
	use with RRDTool.

        Time representations must have their ':'s escaped, since
        the colon is the RRDTool separator for parameters.
        '''
        main = 'DEF:%(vname)s=%(rrdfile)s:%(ds_name)s:%(cdef)s' % self.__dict__
        tail = ''
        if self.step:
            tail += ':step=%s' % self.step
        if self.start:
            tail += ':start=%s' % self.start
        if self.end:
            tail += ':end=%s' % self.end
        if self.reduce:
            tail += ':reduce=%s' % self.reduce
        return main+tail

DEF = DataDefinition

class VariableDefinition(object):
    '''
    This object has two attributes:
        vname
        rpn_expr

    It generates a value and/or a time according to the RPN
    statements used. The resulting vname will, depending on the
    functions used, have a value and a time component. When you use
    this vname in another RPN expression, you are effectively
    inserting its value just as if you had put a number at that
    place. The variable can also be used in the various graph and
    print elements.

    Note that currently only agregation functions work in VDEF rpn
    expressions (a limitation of RRDTool, not PyRRD).
    '''
VDEF = VariableDefinition

class CalculationDefinition(object):
    '''
    This object creates a new set of data points (in memory only,
    not in the RRD file) out of one or more other data series.

    It has two attributes:
        vname
        rpn_expr

    The RPN instructions are used to evaluate a mathematical function
    on each data point. The resulting vname can then be used further
    on in the script, just as if it were generated by a DEF
    instruction.
    '''
CDEF = CalculationDefinition

class GraphPrint(object):
    '''
    This is the same as PRINT, but printed inside the graph.
    '''
GPRINT = GraphPrint

class GraphComment(object):
    '''
    Text is printed literally in the legend section of the graph.
    Note that in RRDtool 1.2 you have to escape colons in COMMENT
    text in the same way you have to escape them in *PRINT commands
    by writing '\:'.
    '''
COMMENT = GraphComment

class GraphVerticalLine(object):
    '''
    Draw a vertical line at time. Its color is composed from three
    hexadecimal numbers specifying the rgb color components (00 is
    off, FF is maximum) red, green and blue. Optionally, a legend
    box and string is printed in the legend section. time may be a
    number or a variable from a VDEF. It is an error to use vnames
    from DEF or CDEF here.
    '''
VRULE = GraphVerticalLine

class GraphLine(object):
    '''
    Draw a line of the specified width onto the graph. width can
    be a floating point number. If the color is not specified, the
    drawing is done 'invisibly'. This is useful when stacking
    something else on top of this line. Also optional is the legend
    box and string which will be printed in the legend section if
    specified. The value can be generated by DEF, VDEF, and CDEF.
    If the optional STACK modifier is used, this line is stacked
    on top of the previous element which can be a LINE or an AREA.

    When you do not specify a color, you cannot specify a legend.
    Should you want to use STACK, use the ``LINEx:<value>::STACK''
    form.
    '''
LINE = GraphLine

class GraphArea(GraphLine):
    '''
    See LINE, however the area between the x-axis and the line will
    be filled.
    '''
AREA = GraphArea

class GraphTick(object):
    '''
    Plot a tick mark (a vertical line) for each value of vname that
    is non-zero and not *UNKNOWN*. The fraction argument specifies
    the length of the tick mark as a fraction of the y-axis; the
    default value is 0.1 (10% of the axis). Note that the color
    specification is not optional.
    '''
TICK = GraphTick

class GraphShift(object):
    '''
    Using this command RRDtool will graph the following elements
    with the specified offset. For instance, you can specify an
    offset of ( 7*24*60*60 = ) 604'800 seconds to ``look back'' one
    week. Make sure to tell the viewer of your graph you did this
    ... As with the other graphing elements, you can specify a
    number or a variable here.
    '''
SHIFT = GraphShift

class GraphXGrid(object):
    '''
    The x-axis label is quite complex to configure. If you don't
    have very special needs it is probably best to rely on the
    autoconfiguration to get this right. You can specify the string
    none to suppress the grid and labels altogether.

    The grid is defined by specifying a certain amount of time in
    the ?TM positions. You can choose from SECOND, MINUTE, HOUR,
    DAY, WEEK, MONTH or YEAR. Then you define how many of these
    should pass between each line or label. This pair (?TM:?ST)
    needs to be specified for the base grid (G??), the major grid
    (M??) and the labels (L??). For the labels you also must define
    a precision in LPR and a strftime format string in LFM. LPR
    defines where each label will be placed. If it is zero, the
    label will be placed right under the corresponding line (useful
    for hours, dates etcetera). If you specify a number of seconds
    here the label is centered on this interval (useful for Monday,
    January etcetera).

        --x-grid MINUTE:10:HOUR:1:HOUR:4:0:%X

    This places grid lines every 10 minutes, major grid lines every
    hour, and labels every 4 hours. The labels are placed under the
    major grid lines as they specify exactly that time.

        --x-grid HOUR:8:DAY:1:DAY:1:0:%A

    This places grid lines every 8 hours, major grid lines and
    labels each day. The labels are placed exactly between two major
    grid lines as they specify the complete day and not just midnight.
    '''

class GraphYGrid(object):
    '''
    Y-axis grid lines appear at each grid step interval. Labels are
    placed every label factor lines. You can specify -y none to
    suppress the grid and labels altogether. The default for this
    option is to automatically select sensible values.
    '''

class Graph(object):
    '''
    rrdtool graph needs data to work with, so you must use one or
    more data definition statements to collect this data. You are
    not limited to one database, it's perfectly legal to collect
    data from two or more databases (one per statement, though).

    If you want to display averages, maxima, percentiles, etcetera
    it is best to collect them now using the variable definition
    statement. Currently this makes no difference, but in a future
    version of rrdtool you may want to collect these values before
    consolidation.

    The data fetched from the RRA is then consolidated so that there
    is exactly one datapoint per pixel in the graph. If you do not
    take care yourself, RRDtool will expand the range slightly if
    necessary. Note, in that case the first and/or last pixel may
    very well become unknown!

    Sometimes data is not exactly in the format you would like to
    display it. For instance, you might be collecting bytes per
    second, but want to display bits per second. This is what the
    data calculation command is designed for. After consolidating
    the data, a copy is made and this copy is modified using a
    rather powerful RPN command set.

    When you are done fetching and processing the data, it is time
    to graph it (or print it). This ends the rrdtool graph sequence.
    '''
    def __init__(self, filename, start=None, end=None, step=None, 
        title='', vertical_label='', width=None, height=None,
        only_graph=None, upper_limit=None, lower_limit=None,
        rigid=False, alt_autoscale=None, alt_autoscale_max=None,
        no_gridfit=False, x_grid=None, y_grid=None, 
        alt_y_grid=False, logarithmic=False, units_exponent=None,
        units_length=None, lazy=False, imginfo=None, color=None,
        zoom=None, font=None, font_render_mode=None,
        font_smoothing_threshold=None, slope_mode=None,
        imgformat=None, interlaced=False, no_legend=False,
        force_rules_legend=False, tabwidth=None, base=None):

        self.filename = filename
        self.start = start

        if filename.strip() == '-':
            # send to stdout
            pass

def _test():
    import doctest, graph
    return doctest.testmod(graph)

if __name__ == '__main__':
    _test()

