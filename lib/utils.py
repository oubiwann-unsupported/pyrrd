from time import mktime
from datetime import datetime

def epoch(dt_obj=None):
    '''
    >>> dt = datetime(1972, 8, 17)
    >>> epoch(dt)
    82879200
    >>> now = epoch()
    >>> type(now)
    <type 'int'>
    '''
    if not dt_obj:
        dt_obj = datetime.now()
    return int(mktime(dt_obj.timetuple()))
