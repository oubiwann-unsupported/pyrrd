'''
This is where we make the decisions about what to use for running
the actual rrdtool commands.

Once this is finished, there will be checks for the rrdtool python
bindings, if the that import fails, we will fall back on the external
pyrrd module.

For now, though, we are only using pyrrd.external.
'''

try:
    # XXX we're not going to let this pass for now, since we don't
    # support the python bindings yet
    raise NotImplementedError
    #import rrdtool
    #import bindings as rrdbackend
except:
    import external as rrdbackend

