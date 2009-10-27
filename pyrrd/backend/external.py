import sys
from subprocess import Popen, PIPE
try:
    from xml.etree import ElementTree
except ImportError:
    from elementtree import ElementTree

from pyrrd.backend import common


def _cmd(command, args):
    if sys.platform == 'win32':
        close_fds = False
    else:
        close_fds = True
    command = "rrdtool %s %s" % (command, args)
    process = Popen(command, shell=True, stdin=PIPE, stdout=PIPE,
                    close_fds=close_fds)
    stdout, stderr = (process.stdout, process.stderr)
    err = output = None
    try:
        err = stderr.read()
    except:
        output = stdout.read()
    if err:
        raise Exception, err
    else:
        return output


def concat(args):
    if isinstance(args, list):
        args = " ".join(args)
    return args


def create(filename, parameters):
    """
    >>> filename = '/tmp/test.rrd'
    >>> parameters = ' --start 920804400'
    >>> parameters += ' DS:speed:COUNTER:600:U:U'
    >>> parameters += ' RRA:AVERAGE:0.5:1:24'
    >>> parameters += ' RRA:AVERAGE:0.5:6:10'
    >>> create(filename, parameters)

    >>> import os
    >>> os.path.exists(filename)
    True

    >>> os.unlink(filename)
    >>> os.path.exists(filename)
    False
    """
    parameters = "%s %s" % (filename, concat(parameters))
    output = _cmd('create', parameters)


def update(filename, data, debug=False):
    """
    >>> filename = '/tmp/test.rrd'
    >>> parameters = ' --start 920804400'
    >>> parameters += ' DS:speed:COUNTER:600:U:U'
    >>> parameters += ' RRA:AVERAGE:0.5:1:24'
    >>> parameters += ' RRA:AVERAGE:0.5:6:10'
    >>> create(filename, parameters)

    >>> import os
    >>> os.path.exists(filename)
    True

    >>> update('/tmp/test.rrd',
    ...   '920804700:12345 920805000:12357 920805300:12363')
    >>> update('/tmp/test.rrd',
    ...   '920805600:12363 920805900:12363 920806200:12373')
    >>> update('/tmp/test.rrd',
    ...   '920806500:12383 920806800:12393 920807100:12399')
    >>> update('/tmp/test.rrd',
    ...   '920807400:12405 920807700:12411 920808000:12415')
    >>> update('/tmp/test.rrd',
    ...   '920808300:12420 920808600:12422 920808900:12423')

    >>> os.unlink(filename)
    >>> os.path.exists(filename)
    False
    """
    parameters = "%s %s" % (filename, concat(data))
    if debug:
        _cmd('updatev', parameters)
    else:
        _cmd('update', parameters)


def fetchRaw(filename, query):
    parameters = "%s %s" % (filename, concat(query))
    return _cmd('fetch', parameters).strip()


def fetch(filename, query):
    """
    >>> filename = '/tmp/test.rrd'
    >>> parameters = ' --start 920804400'
    >>> parameters += ' DS:speed:COUNTER:600:U:U'
    >>> parameters += ' RRA:AVERAGE:0.5:1:24'
    >>> parameters += ' RRA:AVERAGE:0.5:6:10'
    >>> create(filename, parameters)

    >>> import os
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
    output = fetchRaw(filename, concat(query))
    lines = [line for line in output.split('\n') if line]
    dsNames = lines[0].split()
    results = {
        "ds": {},
        "time": {},
        }
    for line in lines[2:]:
        time, data = line.split(":")
        data = [common.coerce(datum) for datum in data.split()]
        results["time"][int(time)] = dict(zip(dsNames, data))
        for dsName, datum in zip(dsNames, data):
            results["ds"].setdefault(dsName, [])
            results["ds"][dsName].append((int(time), common.coerce(datum)))
    return results


def dump(filename, outfile="", parameters=""):
    """
    >>> rrdfile = '/tmp/test.rrd'
    >>> parameters = ' --start 920804400'
    >>> parameters += ' DS:speed:COUNTER:600:U:U'
    >>> parameters += ' RRA:AVERAGE:0.5:1:24'
    >>> parameters += ' RRA:AVERAGE:0.5:6:10'
    >>> create(rrdfile, parameters)

    >>> xml = dump(rrdfile)
    >>> len(xml)
    3724
    >>> xml[0:30]
    '<!-- Round Robin Database Dump'

    >>> xmlfile = '/tmp/test.xml'
    >>> dump(rrdfile, xmlfile)

    >>> import os
    >>> os.path.exists(xmlfile)
    True

    >>> os.unlink(rrdfile)
    >>> os.unlink(xmlfile)
    """
    parameters = "%s %s %s" % (filename, outfile, concat(parameters))
    output = _cmd('dump', parameters)
    if not outfile:
        return output.strip()


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


def info(filename, obj):
    """
    """
    obj.printInfo()
    for ds in obj.ds:
        ds.printInfo()
    for index, rra in enumerate(obj.rra):
        rra.printInfo(index)

def graph(filename, parameters):
    """
    >>> filename = '/tmp/speed.png'
    >>> rrdfile = '/tmp/test.rrd'
    >>> parameters = ' --start 920804400'
    >>> parameters += ' DS:speed:COUNTER:600:U:U'
    >>> parameters += ' RRA:AVERAGE:0.5:1:24'
    >>> parameters += ' RRA:AVERAGE:0.5:6:10'
    >>> create(rrdfile, parameters)

    >>> import os
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
    parameters = "%s %s" % (filename, concat(parameters))
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
        params = common.buildParameters(obj, validParams)
        data = [ str(x) for x in obj.ds ]
        data += [ str(x) for x in obj.rra ]
        return (obj.filename, params + data)

    if function == 'update':
        validParams = ['template']
        params = common.buildParameters(obj, validParams)
        FIRST_VALUE = 0
        DATA = 1
        TIME_OR_DATA = 0
        if obj.values[FIRST_VALUE][DATA]:
            data = ['%s:%s' % (time, values)
                    for time, values in obj.values]
        else:
            data = [data for data, nil in obj.values]
        return (obj.filename, params + data)

    if function == 'fetch':
        validParams = ['resolution', 'start', 'end']
        params = common.buildParameters(obj, validParams)
        return (obj.filename, obj.cf, params)

    if function == 'info':
        return (obj.filename, obj)

    if function == 'graph':
        validParams = ['start', 'end', 'step', 'title',
            'vertical_label', 'width', 'height', 'only_graph',
            'upper_limit', 'lower_limit', 'rigid', 'alt_autoscale',
            'alt_autoscale_max', 'no_gridfit', 'x_grid', 'y_grid',
            'alt_y_grid', 'logarithmic', 'units_exponent', 'zoom',
            'font', 'font_render_mode', 'interlaced', 'no_legend',
            'force_rules_legend', 'tabwidth', 'base', 'color']
        params = common.buildParameters(obj, validParams)
        data = [ str(x) for x in obj.data ]
        return (obj.filename, params + data)


if __name__ == "__main__":
    import doctest
    doctest.testmod()
