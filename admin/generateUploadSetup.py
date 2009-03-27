#!/usr/bin/python

from pyrrd import meta
from pyrrd.util import dist


template_file = "Resources/Templates/setup.py.tmpl"

fh = open(template_file)
template = fh.read()
fh.close()

data = {
    "display_name": meta.display_name,
    "version": meta.version,
    "description": meta.description,
    "author": meta.author,
    "author_email": meta.author_email,
    "url": meta.url,
    "license": meta.license,
    "packages": str(dist.findPackages()),
    "long_description": "\n" + dist.catReST(
        "docs/PRELUDE.txt",
        "README",
        "TODO",
        "docs/HISTORY.txt",
        "docs/ACKNOWLEDGEMENTS.txt",
        "docs/FOOTNOTES.txt",
        stop_on_errors=True,
        out=True),
    }

fh = open("upload_setup.py", "w+")
fh.write(template % data)
fh.close()
