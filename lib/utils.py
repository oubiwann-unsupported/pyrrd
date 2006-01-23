from time import mktime
from datetime import datetime

def epoch(dt_obj=None):
    if not dt_obj:
        dt_obj = datetime.now()
    return int(mktime(dt_obj.timetuple()))
