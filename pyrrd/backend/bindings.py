"""
Once we support the rrdtool bindings, this will be the wrapper we
use to prepare input for the rrdtool calls.

To use the pyrrd.external, we just send it strings. To use the
rrdtool bindings, we"ll need to provide pairs of strings for some
of the parameters.
"""
import rrdtool

from pyrrd.backend.common import buildParameters


def _cmd(command, args):
    function = getattr(rrdtool, command)
    function(*args)


def create(filename, parameters):
    """
    >>> rrdfile = '/tmp/test.rrd'
    >>> parameters = [
    ...   '--start',
    ...   '920804400',
    ...   'DS:speed:COUNTER:600:U:U',
    ...   'RRA:AVERAGE:0.5:1:24',
    ...   'RRA:AVERAGE:0.5:6:10']
    >>> create(rrdfile, parameters)

    # Check that the file's there:
    >>> import os
    >>> os.path.exists(rrdfile)
    True

    # Cleanup:
    >>> os.unlink(rrdfile)
    >>> os.path.exists(rrdfile)
    False
    """
    parameters.insert(0, filename)
    output = _cmd('create', parameters)


def update(filename, parameters, debug=False):
    """
    >>> rrdfile = '/tmp/test.rrd'
    >>> parameters = [
    ...   '--start',
    ...   '920804400',
    ...   'DS:speed:COUNTER:600:U:U',
    ...   'RRA:AVERAGE:0.5:1:24',
    ...   'RRA:AVERAGE:0.5:6:10']
    >>> create(rrdfile, parameters)

    >>> import os
    >>> os.path.exists(rrdfile)
    True

    >>> parameters = ['920804700:12345', '920805000:12357', '920805300:12363']
    >>> update(rrdfile, parameters)
    >>> parameters = ['920805600:12363', '920805900:12363','920806200:12373']
    >>> update(rrdfile, parameters)
    >>> parameters = ['920806500:12383', '920806800:12393','920807100:12399']
    >>> update(rrdfile, parameters)
    >>> parameters = ['920807400:12405', '920807700:12411', '920808000:12415']
    >>> update(rrdfile, parameters)
    >>> parameters = ['920808300:12420', '920808600:12422','920808900:12423']
    >>> update(rrdfile, parameters)

    >>> os.unlink(rrdfile)
    >>> os.path.exists(rrdfile)
    False
    """
    parameters.insert(0, filename)
    if debug:
        _cmd('updatev', parameters)
    else:
        _cmd('update', parameters)


def fetch(filename, query):
    pass


def dump(filename, outfile=None, parameters=""):
    pass


def load(filename):
    pass


def graph(filename, parameters):
    """
    >>> rrdfile = '/tmp/test.rrd'
    >>> parameters = [
    ...   '--start',
    ...   '920804400',
    ...   'DS:speed:COUNTER:600:U:U',
    ...   'RRA:AVERAGE:0.5:1:24',
    ...   'RRA:AVERAGE:0.5:6:10']
    >>> create(rrdfile, parameters)

    >>> import os
    >>> os.path.exists(rrdfile)
    True

    >>> parameters = ['920804700:12345', '920805000:12357', '920805300:12363']
    >>> update(rrdfile, parameters)
    >>> parameters = ['920805600:12363', '920805900:12363','920806200:12373']
    >>> update(rrdfile, parameters)
    >>> parameters = ['920806500:12383', '920806800:12393','920807100:12399']
    >>> update(rrdfile, parameters)
    >>> parameters = ['920807400:12405', '920807700:12411', '920808000:12415']
    >>> update(rrdfile, parameters)
    >>> parameters = ['920808300:12420', '920808600:12422','920808900:12423']
    >>> update(rrdfile, parameters)

    >>> parameters = [
    ...   '--start',
    ...   '920804400', 
    ...   '--end', 
    ...   '920808000',
    ...   '--vertical-label',
    ...   'km/h',
    ...   'DEF:myspeed=%s:speed:AVERAGE' % rrdfile,
    ...   'CDEF:realspeed=myspeed,1000,*',
    ...   'CDEF:kmh=myspeed,3600,*',
    ...   'CDEF:fast=kmh,100,GT,kmh,0,IF',
    ...   'CDEF:good=kmh,100,GT,0,kmh,IF',
    ...   'HRULE:100#0000FF:"Maximum allowed"',
    ...   'AREA:good#00FF00:"Good speed"',
    ...   'AREA:fast#00FFFF:"Too fast"',
    ...   'LINE2:realspeed#FF0000:Unadjusted']
    >>> graphfile = '/tmp/speed.png'
    >>> graph(graphfile, parameters)

    >>> os.path.exists(graphfile)
    True

    >>> os.unlink(rrdfile)
    >>> os.unlink(graphfile)
    """
    parameters.insert(0, filename)
    output = _cmd('graph', parameters)


def prepareObject(function, obj):
    """
    This is a funtion that serves to make interacting with the
    backend as transparent as possible. It"s sole purpose it to
    prepare the attributes and data of the various pyrrd objects
    for use by the functions that call out to rrdtool.

    For all of the rrdtool-methods in this module, we need to split
    the named parameters up into pairs, assebled all the stuff in
    the list obj.data, etc.

    This function will get called by methods in the pyrrd wrapper
    objects. For instance, most of the methods of pyrrd.rrd.RRD
    will call this function. In graph, Pretty much only the method
    pyrrd.graph.Graph.write() will call this function.
    """
    if function == 'create':
        validParams = ['start', 'step']
        params = buildParameters(obj, validParams)
        params += [str(x) for x in obj.ds]
        params += [str(x) for x in obj.rra]
        return (obj.filename, params)


if __name__ == "__main__":
    import doctest
    doctest.testmod()
