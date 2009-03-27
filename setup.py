from setuptools import setup

from pyrrd import meta
from pyrrd.util import dist


setup(name="PyRRD",
    version=meta.version,
    description=meta.description,
    author=meta.author,
    author_email=meta.author_email,
    url=meta.url,
    license=meta.license,
    packages=dist.findPackages(),
    long_description=dist.catReST(
        "docs/PRELUDE.txt",
        "README",
        "TODO",
        "docs/HISTORY.txt",
        "docs/ACKNOWLEDGEMENTS.txt",
        "docs/FOOTNOTES.txt",
        stop_on_errors=True,
        out=True),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: by End-User Class :: Advanced End Users",
        "Intended Audience :: by End-User Class :: System Administrators",
        "Intended Audience :: Science/Research",
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

