from setuptools import setup

from pyrrd import meta
from pyrrd.util import dist


setup(
    name=meta.display_name,
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
        "Intended Audience :: Information Technology",
        "Intended Audience :: System Administrators",
        "Programming Language :: Python",
        "Topic :: Database",
        "Topic :: Database :: Front-Ends",
        "Topic :: Multimedia :: Graphics",
        "Topic :: System :: Networking :: Monitoring",
        "Topic :: System :: Systems Administration",
        "License :: OSI Approved :: BSD License",
       ],
    )
