"""
Once we support the rrdtool bindings, this will be the wrapper we
use to prepare input for the rrdtool calls.

To use the pyrrd.external, we just send it strings. To use the
rrdtool bindings, we"ll need to provide pairs of strings for some
of the parameters.
"""
import rrdtool


def _cmd(command, args):
    function = getattr(rrdtool, command)
    function(*args)


def create(filename, parameters):
    """
    >>> filename = '/tmp/test.rrd'
    >>> parameters = [
    ...   '--start',
    ...   '920804400',
    ...   'DS:speed:COUNTER:600:U:U',
    ...   'RRA:AVERAGE:0.5:1:24',
    ...   'RRA:AVERAGE:0.5:6:10']
    >>> create(filename, parameters)

    # Check that the file's there:
    >>> import os
    >>> os.path.exists(filename)
    True

    # Cleanup:
    >>> os.unlink(filename)
    >>> os.path.exists(filename)
    False
    """
    parameters.insert(0, filename)
    output = _cmd('create', parameters)


# XXX remove redundancy between this and pyrrd.external.buildParameters and
# maybe put the result in pyrrd.util
def buildParameters(obj, validList):
    """
    >>> class TestClass(object):
    ...   pass
    >>> testClass = TestClass()
    >>> testClass.a = 1
    >>> testClass.b = 2
    >>> testClass.c = 3
    >>> buildParameters(testClass, ["a", "b"])
    ['--a', '1', '--b', '2']
    """
    params = []
    for param in validList:
        attr = str(getattr(obj, param))
        if attr:
            param = param.replace("_", "-")
            params.extend(["--%s" % param, attr])
    return params


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
