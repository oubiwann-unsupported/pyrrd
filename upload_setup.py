from setuptools import setup

setup(
    name="PyRRD",
    version="0.0.7",
    description="An Object-Oriented Python Interface for RRD",
    author="Duncan McGreggor",
    author_email="duncan@canonical.com",
    url="http://code.google.com/p/pyrrd/",
    license="BSD",
    packages=['test', 'pyrrd', 'pyrrd.util'],
    long_description="""
        
~~~~~
PyRRD
~~~~~

.. contents::
   :depth: 1


========
Features
========

For docs, see the docstrings at the beginning of each class (and
many of the functions). They not only contain many of the standard
RRDTool docs, but they contain doctests which give you a hands-on,
how-it-works understanding of actual usage.

A quick review of features is available at the project wiki [#]_ . Example
code with graph image output is also available on the wiki [#]_ .


============
Introduction
============

PyRRD is an object-oriented wrapper for the command line graphing and
round-robin database utility, rrdtool [#]_ . PyRRD originally had two design
goals:

1. provide an interface to rrdtool that Python programmers would love, and

2. not depend upon the Python bindings for rrdtool.

The reasons for the former are obvious. The motivation for the latter were the
many people who had difficulty compiling the rrdtool bindings on their
operating system of choice.

The PyRRD project has plans of incorporating the Python bindings for those that
have them on their system so that they may enjoy both the speed benefits from
the bindings as well as the API usability from PyRRD.


============
Dependencies
============

Some parts of PyRRD make use of ElementTree for XML processing. If you have
Python 2.5 or greater, PyRRD will use xml.etree. If your Python version is less
than 2.5 and you want to use features that depend on XML processing (such as
dump function and the fetch/info methods), you will need to install
the ElementTree library [#]_ .



============
Installation
============

PyRRD is installed in the usual way::

  python setup.py install

You may also use PyRRD without installing it as long as you have ./ in your
PYTHONPATH and you are in the top-level directory (which has the pyrrd child
directory).


=====
Usage
=====

Create an RRD file programmatically::

    >>> from pyrrd.rrd import DataSource, RRA, RRD
    >>> filename = '/tmp/test.rrd'
    >>> dataSources = []
    >>> roundRobinArchives = []
    >>> dataSource = DataSource(
    ...     dsName='speed', dsType='COUNTER', heartbeat=600)
    >>> dataSources.append(dataSource)
    >>> roundRobinArchives.append(RRA(cf='AVERAGE', xff=0.5, steps=1, rows=24))
    >>> roundRobinArchives.append(RRA(cf='AVERAGE', xff=0.5, steps=6, rows=10))
    >>> myRRD = RRD(filename, ds=dataSources, rra=roundRobinArchives, 
    ...     start=920804400)
    >>> myRRD.create()

Let's check to see that the file exists::

    >>> import os
    >>> os.path.isfile(filename)
    True

In order to save writes to disk, PyRRD buffers values and then writes the
values to the RRD file at one go::

    >>> myRRD.bufferValue('920805600', '12363')
    >>> myRRD.bufferValue('920805900', '12363')
    >>> myRRD.bufferValue('920806200', '12373')
    >>> myRRD.bufferValue('920806500', '12383')
    >>> myRRD.update()

Let's add some more data::

    >>> myRRD.bufferValue('920806800', '12393')
    >>> myRRD.bufferValue('920807100', '12399')
    >>> myRRD.bufferValue('920807400', '12405')
    >>> myRRD.bufferValue('920807700', '12411')
    >>> myRRD.bufferValue('920808000', '12415')
    >>> myRRD.bufferValue('920808300', '12420')
    >>> myRRD.bufferValue('920808600', '12422')
    >>> myRRD.bufferValue('920808900', '12423')
    >>> myRRD.update()

If you're curious, you can take a look at your rrd file with the following::

    myRRD.info()

The output of that isn't printed here, 'cause it take up too much space.
However, it is very similar to the output of the similarly named rrdtool
command.

In order to create a graph, we'll need some data definitions. We'll also
throw in some calculated definitions and variable definitions for good
meansure::

    >>> from pyrrd.graph import DEF, CDEF, VDEF, LINE, AREA, GPRINT
    >>> def1 = DEF(rrdfile=myRRD.filename, vname='myspeed',
    ...     dsName=dataSource.name)
    >>> cdef1 = CDEF(vname='kmh', rpn='%s,3600,*' % def1.vname)
    >>> cdef2 = CDEF(vname='fast', rpn='kmh,100,GT,kmh,0,IF')
    >>> cdef3 = CDEF(vname='good', rpn='kmh,100,GT,0,kmh,IF')
    >>> vdef1 = VDEF(vname='mymax', rpn='%s,MAXIMUM' % def1.vname)
    >>> vdef2 = VDEF(vname='myavg', rpn='%s,AVERAGE' % def1.vname)

    >>> line1 = LINE(value=100, color='#990000', legend='Maximum Allowed')
    >>> area1 = AREA(defObj=cdef3, color='#006600', legend='Good Speed')
    >>> area2 = AREA(defObj=cdef2, color='#CC6633', legend='Too Fast')
    >>> line2 = LINE(defObj=vdef2, color='#000099', legend='My Average', 
    ...     stack=True)
    >>> gprint1 = GPRINT(vdef2, '%6.2lf kph')

Color is the spice of life. Let's spice it up a little::

    >>> from pyrrd.graph import ColorAttributes
    >>> ca = ColorAttributes()
    >>> ca.back = '#333333'
    >>> ca.canvas = '#333333'
    >>> ca.shadea = '#000000'
    >>> ca.shadeb = '#111111'
    >>> ca.mgrid = '#CCCCCC'
    >>> ca.axis = '#FFFFFF'
    >>> ca.frame = '#AAAAAA'
    >>> ca.font = '#FFFFFF'
    >>> ca.arrow = '#FFFFFF'

Now we can create a graph for the data in our RRD file::

    >>> from pyrrd.graph import Graph
    >>> graphfile = "/tmp/rrdgraph.png"
    >>> g = Graph(graphfile, start=920805000, end=920810000,
    ...     vertical_label='km/h', color=ca)
    >>> g.data.extend([def1, cdef1, cdef2, cdef3, vdef1, vdef2, line1, area1,
    ...     area2, line2, gprint1])
    >>> g.write()

Let's make sure it's there::

    >>> os.path.isfile(graphfile)
    True

Open that up in your favorite image browser and confirm that the appropriate
RRD graph is generated.

Let's clean up the files we've put in the temp directory::

    >>> os.unlink(filename)
    >>> os.unlink(graphfile)



==========
Known Bugs
==========

* No known bugs.

====
TODO
====

Near Term
---------

* Add wiki examples for using info and fetch

* Add a wrapper for the Python RRDTool bindings

  - Since the doctests are mostly to show API functionality, we'll need to add
    unit tests for both backends (cli wrapper and bindings wrapper).

  - The python bindings should be fairly straight-forward to support, since we
    should just be able to split on the parameters that are currently
    calculated.

* Allow for users to supply their own fd to pyrrd.graph.

* Allow for users to decide which backend will be used on an
  instance-by-instance basis.

* Update all examples for recent dates like example4 has been updated.

* Stop using actual file writes and doctests for file tests; use unit tests
  (and StringIO) instead.

Future
------

* Add an RPN class.

* Add a DS collection class that has a get() method for getting a
  particular DS by name.

* Add support for atomic operations.


=======
Changes
=======

From 0.0.6 to 0.0.7
-------------------

* Packaging improvements and loads of documentation.


From 0.0.5 to 0.0.6
-------------------

* Bug fix release (missing files in source package).


From 0.0.4 to 0.0.5
-------------------

* Added support for retrieving and displaying RRD from RRD files.

* Added an object mapper for RRD data (via XML files).

* Added community-contributed improvements.


From 0.0.3 to 0.0.4
-------------------

* Updated all the examples to work with the latest code.

* Added community-contributed bug fix for Windows users.


From 0.0.2 to 0.0.3
-------------------

* Minor code reorg.

* Fixed doctests.

* Various bug fixes.

* Examples updates.


From 0.0.1 to 0.0.2
-------------------

* Added license.

* Added unit tests.

* Added more examples.


From 0 to 0.0.1
---------------

* Reorganized RRD code as donated from the CoyMon project.

* Got basic rrdtool functionality represented as Python classes.

* Code cleanup.


================
Acknowledgements
================

The following members of the community have provided valuable contributions to
this project:

* Ravi Bhalotia

* Allen Lerner

* Mike Carrick and the U.S. Department of Veterans Affairs

* AdytumSolutions, Inc.

* nasvos

* Leem Smit

* Aaron Westendorf and Agora Games

Thanks!


==========
References
==========

.. [#] http://code.google.com/p/pyrrd/wiki/FrontPage?tm=6

.. [#] http://code.google.com/p/pyrrd/wiki/FullWorkingExamples

.. [#] http://oss.oetiker.ch/rrdtool/

.. [#] http://effbot.org/zone/element-index.htm



        """,
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: by End-User Class :: Advanced End Users",
        "Intended Audience :: by End-User Class :: System Administrators",
        "Intended Audience :: by Industry or Sector :: Information Technology",
        "Programming Language :: Python",
        "Topic :: Database",
        "Topic :: Formats and Protocols :: Data Formats",
        "Topic :: Multimedia :: Graphics :: Presentation",
        "Topic :: Software Development :: Object Oriented",
        "Topic :: System :: Networking :: Monitoring",
        "Topic :: System :: Systems Administration",
        "License :: OSI Approved :: BSD License",
       ],
    )

