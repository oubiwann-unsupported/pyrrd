import re
import os
import sys
from subprocess import call, Popen, PIPE
try:
    from xml.etree import ElementTree
except ImportError:
    from elementtree import ElementTree


def _cmd(command, args):
    args = 'rrdtool %s %s' % (command, args)
    if sys.platform == 'win32':
        close_fds = False
    else:
        close_fds = True
    p = Popen([args], shell=True, stdin=PIPE, stdout=PIPE, close_fds=close_fds)
    stdout, stderr = (p.stdout, p.stderr)
    err = output = None
    try:
        err = stderr.read()
    except:
        output = stdout.read()
    if err:
        raise Exception, err
    else:
        return output


def coerce(value):
    """
    >>> coerce("NaN")
    nan
    >>> coerce("nan")
    nan
    >>> coerce("Unkn")
    >>> coerce("u")
    >>> coerce("1")
    1.0
    >>> 0.039 < coerce("4.0000000000e-02") < 0.041
    True
    >>> 0.039 < coerce(4.0000000000e-02) < 0.041
    True
    """
    try:
        return float(value)
    except ValueError:
        if value.lower() in ['unkn', 'u']:
            return None
    raise ValueError, "Unexpected type for data (%s)" % value

 
def iterParse(lines):
    """
    >>> lines = [' 920804700: nan',
    ...  ' 920805000: 4.0000000000e-02',
    ...  ' 920805300: 2.0000000000e-02',
    ...  ' 920805600: 0.0000000000e+00',
    ...  ' 920805900: 0.0000000000e+00',
    ...  ' 920806200: 3.3333333333e-02',
    ...  ' 920806500: 3.3333333333e-02',
    ...  ' 920806800: 3.3333333333e-02',
    ...  ' 920807100: 2.0000000000e-02',
    ...  ' 920807400: 2.0000000000e-02',
    ...  ' 920807700: 2.0000000000e-02',
    ...  ' 920808000: 1.3333333333e-02',
    ...  ' 920808300: 1.6666666667e-02',
    ...  ' 920808600: 6.6666666667e-03',
    ...  ' 920808900: 3.3333333333e-03',
    ...  ' 920809200: nan']
    >>> g = iterParse(lines)
    >>> g.next()
    (920804700, nan)
    >>> g.next()
    (920805000, 0.040000000000000001)
    >>> len(list(g)) == len(lines) - 2
    True
    """
    for line in lines:
        line = line.strip()
        time, value = [x.strip() for x in re.split(':\s+', line)]
        yield (int(time), coerce(value))


def buildParameters(obj, validList):
    paramTemplate = ' --%s %s'
    params = ''
    for param in validList:
        attr = getattr(obj, param)
        if attr:
            param = param.replace('_', '-')
            params += paramTemplate % (param, attr)
    return params.strip()


def create(filename, parameters):
    """
    >>> filename = '/tmp/test.rrd'
    >>> parameters = ' --start 920804400'
    >>> parameters += ' DS:speed:COUNTER:600:U:U'
    >>> parameters += ' RRA:AVERAGE:0.5:1:24'
    >>> parameters += ' RRA:AVERAGE:0.5:6:10'
    >>> create(filename, parameters)
    >>> os.path.exists(filename)
    True

    >>> os.unlink(filename)
    >>> os.path.exists(filename)
    False
    """
    parameters = '%s %s' % (filename, parameters)
    output = _cmd('create', parameters)


def update(filename, data, debug=False):
    """
    >>> filename = '/tmp/test.rrd'
    >>> parameters = ' --start 920804400'
    >>> parameters += ' DS:speed:COUNTER:600:U:U'
    >>> parameters += ' RRA:AVERAGE:0.5:1:24'
    >>> parameters += ' RRA:AVERAGE:0.5:6:10'
    >>> create(filename, parameters)
    >>> os.path.exists(filename)
    True

    >>> update('/tmp/test.rrd', '920804700:12345 920805000:12357 920805300:12363')
    >>> update('/tmp/test.rrd', '920805600:12363 920805900:12363 920806200:12373')
    >>> update('/tmp/test.rrd', '920806500:12383 920806800:12393 920807100:12399')
    >>> update('/tmp/test.rrd', '920807400:12405 920807700:12411 920808000:12415')
    >>> update('/tmp/test.rrd', '920808300:12420 920808600:12422 920808900:12423')

    >>> os.unlink(filename)
    >>> os.path.exists(filename)
    False
    """
    parameters = '%s %s' % (filename, data)
    if debug:
        _cmd('updatev', parameters)
    else:
         _cmd('update', parameters)


def fetchRaw(filename, query):
    parameters = '%s %s' % (filename, query)
    return _cmd('fetch', parameters).strip()


def fetch(filename, query):
    """
    >>> filename = '/tmp/test.rrd'
    >>> parameters = ' --start 920804400'
    >>> parameters += ' DS:speed:COUNTER:600:U:U'
    >>> parameters += ' RRA:AVERAGE:0.5:1:24'
    >>> parameters += ' RRA:AVERAGE:0.5:6:10'
    >>> create(filename, parameters)
    >>> os.path.exists(filename)
    True

    >>> update('/tmp/test.rrd', '920804700:12345 920805000:12357 920805300:12363')
    >>> update('/tmp/test.rrd', '920805600:12363 920805900:12363 920806200:12373')
    >>> update('/tmp/test.rrd', '920806500:12383 920806800:12393 920807100:12399')
    >>> update('/tmp/test.rrd', '920807400:12405 920807700:12411 920808000:12415')
    >>> update('/tmp/test.rrd', '920808300:12420 920808600:12422 920808900:12423')

    >>> results = fetch('/tmp/test.rrd', 'AVERAGE --start 920804400 --end 920809200')

    # Results are provided in two ways, one of which is by the data source
    # name:
    >>> sorted(results["ds"].keys())
    ['speed']

    # accessing a DS entry like this gives of a (time, data) tuple:
    >>> results["ds"]["speed"][0]
    (920805000, 0.040000000000000001)

    # The other way of accessing the results data is by data source time
    # entries:
    >>> keys = sorted(results["time"].keys())
    >>> len(keys)
    16
    >>> keys[0:6]
    [920805000, 920805300, 920805600, 920805900, 920806200, 920806500]
    >>> results["time"][920805000]
    {'speed': 0.040000000000000001}

    The benefits of using an approach like this become obvious when the RRD
    file has multiple DSs and RRAs.

    >>> os.unlink(filename)
    """
    output = fetchRaw(filename, query)
    lines = [line for line in output.split('\n') if line]
    dsNames = lines[0].split()
    results = {
        "ds": {},
        "time": {},
        }
    for line in lines[2:]:
        time, data = line.split(":")
        data = [coerce(datum) for datum in data.split()]
        results["time"][int(time)] = dict(zip(dsNames, data))
        for dsName, datum in zip(dsNames, data):
            results["ds"].setdefault(dsName, [])
            results["ds"][dsName].append((int(time), coerce(datum)))
    return results


def dump(filename, outfile=None, parameters=""):
    """
    >>> filename = '/tmp/test.rrd'
    >>> parameters = ' --start 920804400'
    >>> parameters += ' DS:speed:COUNTER:600:U:U'
    >>> parameters += ' RRA:AVERAGE:0.5:1:24'
    >>> parameters += ' RRA:AVERAGE:0.5:6:10'
    >>> create(filename, parameters)
    >>> xml = dump(filename)
    >>> len(xml)
    3724
    >>> xml[0:30]
    '<!-- Round Robin Database Dump'
    """
    parameters = '%s %s' % (filename, parameters)
    output = _cmd('dump', parameters).strip()
    if not outfile:
        return output
    fh = open(outfile, "w+")
    fh.write(output)
    fh.close()


def load(filename):
    """
    Load RRD data via the RRDtool XML dump into an ElementTree.

    >>> filename = '/tmp/test.rrd'
    >>> parameters = ' --start 920804400'
    >>> parameters += ' DS:speed:COUNTER:600:U:U'
    >>> parameters += ' RRA:AVERAGE:0.5:1:24'
    >>> parameters += ' RRA:AVERAGE:0.5:6:10'
    >>> create(filename, parameters)
    >>> tree = load(filename)
    >>> [x.tag for x in tree]
    ['version', 'step', 'lastupdate', 'ds', 'rra', 'rra']
    """
    xml = dump(filename)
    return ElementTree.fromstring(xml)


def graph(filename, parameters):
    """
    >>> filename = '/tmp/speed.png'
    >>> rrdfile = '/tmp/test.rrd'
    >>> parameters = ' --start 920804400'
    >>> parameters += ' DS:speed:COUNTER:600:U:U'
    >>> parameters += ' RRA:AVERAGE:0.5:1:24'
    >>> parameters += ' RRA:AVERAGE:0.5:6:10'
    >>> create(rrdfile, parameters)
    >>> os.path.exists(rrdfile)
    True

    >>> update('/tmp/test.rrd', '920804700:12345 920805000:12357 920805300:12363')
    >>> update('/tmp/test.rrd', '920805600:12363 920805900:12363 920806200:12373')
    >>> update('/tmp/test.rrd', '920806500:12383 920806800:12393 920807100:12399')
    >>> update('/tmp/test.rrd', '920807400:12405 920807700:12411 920808000:12415')
    >>> update('/tmp/test.rrd', '920808300:12420 920808600:12422 920808900:12423')

    >>> parameters = ' --start 920804400 --end 920808000'
    >>> parameters += ' --vertical-label km/h'
    >>> parameters += ' DEF:myspeed=%s:speed:AVERAGE' % rrdfile
    >>> parameters += ' CDEF:realspeed=myspeed,1000,*'
    >>> parameters += ' CDEF:kmh=myspeed,3600,*'
    >>> parameters += ' CDEF:fast=kmh,100,GT,kmh,0,IF'
    >>> parameters += ' CDEF:good=kmh,100,GT,0,kmh,IF'
    >>> parameters += ' HRULE:100#0000FF:"Maximum allowed"'
    >>> parameters += ' AREA:good#00FF00:"Good speed"'
    >>> parameters += ' AREA:fast#00FFFF:"Too fast"'
    >>> parameters += ' LINE2:realspeed#FF0000:Unadjusted'
    >>> if os.path.exists(filename):
    ...   os.unlink(filename)
    >>> graph(filename, parameters)
    >>> os.path.exists(filename)
    True

    >>> os.unlink(rrdfile)
    >>> os.unlink(filename)
    """
    parameters = '%s %s' % (filename, parameters)
    _cmd('graph', parameters)


def prepareObject(function, obj):
    """
    This is a funtion that serves to make interacting with the
    backend as transparent as possible. It's sole purpose it to
    prepare the attributes and data of the various pyrrd objects
    for use by the functions that call out to rrdtool.

    For all of the rrdtool-methods in this module, we need a filename
    and then parameters -- both as strings. That's it.

    This function will get called by methods in the pyrrd wrapper
    objects. For instance, most of the methods of pyrrd.rrd.RRD
    will call this function. In graph, Pretty much only the method
    pyrrd.graph.Graph.write() will call this function.
    """
    if function == 'create':
        validParams = ['start', 'step']
        params = buildParameters(obj, validParams)
        data = ' '.join([ str(x) for x in obj.ds ])
        data += ' ' + ' '.join([ str(x) for x in obj.rra ])
        return (obj.filename, "%s %s" % (params, data))

    if function == 'update':
        validParams = ['template']
        params = buildParameters(obj, validParams)

        FIRST_VALUE = 0
        DATA = 1
        TIME_OR_DATA = 0
        if obj.values[FIRST_VALUE][DATA]:
            data = ' '.join([ '%s:%s' % (time, values)
                for time, values in obj.values ])
        else:
            data = ' '.join([ data for data, nil in obj.values ])
        return (obj.filename, "%s %s" % (params, data))

    if function == 'fetch':
        # XXX add support
        validParams = ['resolution', 'start', 'end']
        params = buildParameters(obj, validParams)
        return (obj.filename, "%s %s" % (obj.cf, params))

    if function == 'info':
        # the command line tool is not used to get the info; parsed dump output
        # is used instead
        pass

    if function == 'graph':
        validParams = ['start', 'end', 'step', 'title',
            'vertical_label', 'width', 'height', 'only_graph',
            'upper_limit', 'lower_limit', 'rigid', 'alt_autoscale',
            'alt_autoscale_max', 'no_gridfit', 'x_grid', 'y_grid',
            'alt_y_grid', 'logarithmic', 'units_exponent', 'zoom',
            'font', 'font_render_mode', 'interlaced', 'no_legend',
            'force_rules_legend', 'tabwidth', 'base', 'color']
        params = buildParameters(obj, validParams)
        data = ' '.join([ str(x) for x in obj.data ])
        return (obj.filename, "%s %s" % (params, data))


def _test():
    from doctest import testmod
    return testmod()


if __name__ == '__main__':
    _test()

