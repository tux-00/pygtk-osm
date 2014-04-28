#! /usr/bin/env python

# https://docs.python.org/2/distutils/setupscript.html

from distutils.core import setup
from distutils.command.build_py import build_py as _build_py

# http://babel.edgewall.org/wiki/Download

from babel.messages import frontend as babel
from os.path import abspath, dirname, join, normpath
WHERE_AM_I = abspath(dirname(__file__))

# http://stackoverflow.com/a/1712544/3391915

class po(_build_py):

    def run(self):
    
        import os, shutil, errno
        PO_DIR = join(WHERE_AM_I, 'po')
        LOCALE_DIR = join(WHERE_AM_I, 'locale')
        locales = []
        for file in os.listdir(PO_DIR):
            if file.endswith(".po"):
                locales.append(os.path.basename(file)[:-3])
        print(locales)
        filename = '%s.po' % self.distribution.get_name()
        for locale in locales:
            po_PO = join(PO_DIR, locale + '.po')
            lc_messages_dir = join(LOCALE_DIR, locale)
            lc_messages_dir = join(lc_messages_dir, 'LC_MESSAGES')
            if not os.path.exists(LOCALE_DIR):
                os.mkdir(LOCALE_DIR)
            if not os.path.exists(join(LOCALE_DIR, locale)):
                os.mkdir(join(LOCALE_DIR, locale))
            if not os.path.exists(lc_messages_dir):
                os.mkdir(lc_messages_dir)
            po_LOCALE = join(lc_messages_dir, filename) 
            shutil.copy(po_PO,po_LOCALE)
    
        # python setup.py compile_catalog --directory locale
        
        compiler = babel.compile_catalog(self.distribution)
        compiler.directory = LOCALE_DIR
        compiler.domain = self.distribution.get_name()
        compiler.run()
        

setup(name='pygtk-osm',
    version='0.0.9',
    description='OpenStreetMap GTK Viewer',
    author='Raph',
    author_email='raphb.bis@gmail.com',
    url='https://github.com/tux-00/osm',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python :: 2.7'
    ],
    cmdclass = {
        'compile_catalog': babel.compile_catalog,
        'extract_messages': babel.extract_messages,
        'init_catalog': babel.init_catalog,
        'update_catalog': babel.update_catalog,
        'po': po
    },
    license='GPLv3+'
)
# https://pypi.python.org/pypi?:action=browse
# https://pypi.python.org/pypi?%3Aaction=list_classifiers
