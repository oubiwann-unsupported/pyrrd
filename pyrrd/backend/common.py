import re


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
