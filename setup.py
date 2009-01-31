from setuptools import setup

version = open('VERSION').read().strip()

setup(name='PyRRD',
    version=version,
    description='An Object-Oriented Python Interface for RRD',
    author='Duncan McGreggor',
    author_email='duncan@adytum.us',
    url='http://code.google.com/p/pyrrd/',
    license='BSD',
    long_description='''PyRRD is a module that wraps RRDTool to
        allow for the greatest possible programmatic ease in creating,
        updating, querying and graphing RRD data.''',
    packages=[
        'pyrrd',
    ],
    include_package_data = False,
    exclude_package_data = { 
        '': ['*.sh', 'pyrrd/old/*'],
    },
)
'''
    classifiers = [f.strip() for f in """
    License :: OSI-Approved Open Source :: BSD License
    Development Status :: 4 - Alpha
    Intended Audience :: by End-User Class :: System Administrators
    Intended Audience :: Developers
    Intended Audience :: by End-User Class :: Advanced End Users
    Intended Audience :: by Industry or Sector :: Information Technology
    Intended Audience :: by Industry or Sector :: Telecommunications Industry
    Programming Language :: Python
    Topic :: Database
    Topic :: Formats and Protocols :: Data Formats
    Topic :: Multimedia :: Graphics :: Presentation
    Topic :: Software Development :: Object Oriented
    Topic :: System :: Networking :: Monitoring
    Topic :: System :: Systems Administration
    Topic :: Internet :: WWW/HTTP :: Site Management
    Topic :: Security
    Operating System :: Grouping and Descriptive Categories :: All POSIX (Linux/BSD/UNIX-like OSes)
    """.splitlines() if f.strip()],
'''
