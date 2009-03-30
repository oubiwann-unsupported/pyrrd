"""
Once we support the rrdtool bindings, this will be the wrapper we
use to prepare input for the rrdtool calls.

To use the pyrrd.external, we just send it strings. To use the
rrdtool bindings, we"ll need to provide pairs of strings for some
of the parameters.
"""
import rrdtool

from pyrrd.backend import external
from pyrrd.backend.common import buildParameters


def _cmd(command, args):
    function = getattr(rrdtool, command)
    return function(*args)


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


def fetch(filename, parameters, useBindings=False):
    """
    By default, this function does not use the bindings for fetch. The reason
    for this is we want default compatibility with the data output/results from
    the fetch method for both the external and bindings modules.

    If a developer really wants to use the native bindings to get the fetch
    data, they may do so by explicitly setting the useBindings parameter. This
    will return data in the Python Python bindings format, though.

    Do be aware, though, that the PyRRD format is much easier to get data out
    of in a sensible manner (unless you really like the RRDTool approach).

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

    >>> parameters = ['AVERAGE', '--start', '920804400', '--end', '920809200']
    >>> results = fetch(rrdfile, parameters, useBindings=True)

    >>> results[0]
    (920804400, 920809500, 300)
    >>> results[1]
    ('speed',)
    >>> len(results[2])
    18

    # For more info on the PyRRD data format, see the docstring for
    # pyrrd.external.fetch.
    >>> parameters = ['AVERAGE', '--start', '920804400', '--end', '920809200']
    >>> results = fetch(rrdfile, parameters, useBindings=False)
    >>> sorted(results["ds"].keys())
    ['speed']
    
    >>> os.unlink(rrdfile)
    >>> os.path.exists(rrdfile)
    False
    """
    if useBindings:
        parameters.insert(0, filename)
        return _cmd('fetch', parameters)
    else:
        return external.fetch(filename, " ".join(parameters))


def dump(filename, outfile="", parameters=[]):
    """
    The rrdtool Python bindings don't have support for dump, so we need to use
    the external dump function.

    >>> rrdfile = '/tmp/test.rrd'
    >>> parameters = [
    ...   '--start',
    ...   '920804400',
    ...   'DS:speed:COUNTER:600:U:U',
    ...   'RRA:AVERAGE:0.5:1:24',
    ...   'RRA:AVERAGE:0.5:6:10']
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
    parameters = " ".join(parameters)
    output = external.dump(filename, outfile, parameters)
    if output:
        return output.strip()


def load(filename):
    """
    The rrdtool Python bindings don't have support for load, so we need to use
    the external load function.

    >>> rrdfile = '/tmp/test.rrd'
    >>> parameters = [
    ...   '--start',
    ...   '920804400',
    ...   'DS:speed:COUNTER:600:U:U',
    ...   'RRA:AVERAGE:0.5:1:24',
    ...   'RRA:AVERAGE:0.5:6:10']
    >>> create(rrdfile, parameters)

    >>> tree = load(rrdfile)
    >>> [x.tag for x in tree]
    ['version', 'step', 'lastupdate', 'ds', 'rra', 'rra']
    """
    return external.load(filename)


def info(filename, obj=None, useBindings=False):
    """
    Similarly to the fetch function, the info function uses
    pyrrd.backend.external by default. This is due to the fact that 1) the
    output of the RRD info module is much more easily legible, and 2) it is
    very similar in form to the output produced by the "rrdtool info" command.
    The output produced by the rrdtool Python bindings is a data structure and
    more difficult to view.

    However, if that output is what you desire, then simply set the useBindings
    parameter to True.
    """
    if useBindings:
        from pprint import pprint
        pprint(_cmd('info', [filename]))
    else:
        external.info(filename, obj)


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
    # XXX add the rest of them!!
    if function == 'update':
        pass

    if function == 'fetch':
        pass

    if function == 'info':
        return (obj.filename, obj)

    if function == 'graph':
        pass


if __name__ == "__main__":
    import doctest
    doctest.testmod()
