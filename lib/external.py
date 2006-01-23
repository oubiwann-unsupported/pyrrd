import re
import os
import sys
from subprocess import call, Popen, PIPE

def _cmd(command, args):
    if isinstance(args, str):
        args = re.split('\s+', args.strip())
    elif isinstance(args, tuple):
        args = list(args)
    args = ['rrdtool', command] + args

    p = Popen(args, stdin=PIPE, stdout=PIPE, close_fds=True)
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

def create(filename, parameters):
    '''
    >>> filename = '/tmp/test.rrd'
    >>> parameters = ' --start 920804400'
    >>> parameters += ' DS:speed:COUNTER:600:U:U'
    >>> parameters += ' RRA:AVERAGE:0.5:1:24'
    >>> parameters += ' RRA:AVERAGE:0.5:6:10'
    >>> create(filename, parameters)
    >>> os.path.exists(filename)
    True
    '''
    parameters = '%s %s' % (filename, parameters)
    output = _cmd('create', parameters)

def update(filename, data):
    '''
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
    '''
    parameters = '%s %s' % (filename, data)
    output = _cmd('update', parameters)

def fetchRaw(filename, query):
    parameters = '%s %s' % (filename, query)
    return _cmd('fetch', parameters).strip()

def fetch(filename, query, results_as_generator=True):
    '''
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

    >>> ds_name, results = fetch('/tmp/test.rrd', 'AVERAGE --start 920804400 --end 920809200')
    >>> ds_name
    'speed'
    >>> results.next()
    (920804700, None)
    '''
    output = fetchRaw(filename, query)
    lines = output.split('\n')
    ds_name = lines[0]
    # lines[1] is blank
    results = generateResultLines(lines[2:])
    if results_as_generator:
        return (ds_name, results)
    else:
        return (ds_name, list(results))

def generateResultLines(lines):
    for line in lines:
        line = line.strip()
        time, value = re.split(':\s+', line)
        value = value.strip()
        if value.lower() in ['nan', 'unkn', 'u']:
            value = None
        else:
            value = float(value)
        yield (int(time.strip()), value)

def _test():
    import doctest, external
    return doctest.testmod(external)

if __name__ == '__main__':
    _test()

