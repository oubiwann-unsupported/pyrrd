'''
Once we support the rrdtool bindings, this will be the wrapper we
use to prepare input for the rrdtool calls.

To use the pyrrd.external, we just send it strings. To use the
rrdtool bindings, we'll need to provide pairs of strings for some
of the parameters.
'''

def prepareObject(obj):
    '''
    This is a funtion that serves to make interacting with the
    backend as transparent as possible. It's sole purpose it to
    prepare the attributes and data of the various pyrrd objects
    for use by the functions that call out to rrdtool.

    For all of the rrdtool-methods in this module, we need to split
    the named parameters up into pairs, assebled all the stuff in
    the list obj.data, etc.

    This function will get called by methods in the pyrrd wrapper
    objects. For instance, most of the methods of pyrrd.rrd.RRD
    will call this function. In graph, Pretty much only the method
    pyrrd.graph.Graph.write() will call this function.
    '''
