import sys
from esky import bdist_esky
from distutils.core import setup

# for windows
# > python setup.py bdist_esky

VERSION = "1.1"

if sys.platform in ['win32','cygwin','win64']:

    # Use bdist_esky instead of py2exe

    setup(
        name = "KeithNumClient",
        version = VERSION ,
        #  All executables are listed in the "scripts" argument
        scripts = ["client_nonqued.py"],
        options = {"bdist_esky": {
                  "freezer_module":"py2exe",
                }}
    )

# for mac
# > python setup.py bdist_esky
elif sys.platform == 'darwin':
    setup(
        name = "KeithNumClient",
        version = VERSION ,
         scripts = ["client_nonqued.py"],
        options = {"bdist_esky": {
                    "freezer_module":"py2app"
                 }}
    )
else:
    setup(
        name = "KeithNumClient",
        version = VERSION ,
        #  All executables are listed in the "scripts" argument
        scripts = ["client_nonqued.py"],
    )
