
AUTHOR = 'Chris Dent'
AUTHOR_EMAIL = 'cdent@peermore.com'
NAME = 'tiddlywebplugins.hoster'
DESCRIPTION = 'A hoster for TiddlyWikis'

import mangler
import os
from setuptools import setup, find_packages

# update in __init__ too please
VERSION = '0.9.40'


setup(
        namespace_packages = ['tiddlywebplugins'],
        name = NAME,
        version = VERSION,
        description = DESCRIPTION,
        long_description=file(
            os.path.join(os.path.dirname(__file__), 'README')).read(),
        author = AUTHOR,
        scripts = ['betsy'],
        url = 'http://pypi.python.org/pypi/%s' % NAME,
        packages = find_packages(exclude='test'),
        author_email = AUTHOR_EMAIL,
        platforms = 'Posix; MacOS X; Windows',
        install_requires = ['setuptools',
            'tiddlyweb>=1.4.0',
            'tiddlywebplugins.utils',
            'tiddlywebplugins.templates>=0.8',
            'tiddlywebwiki',
            'tiddlywebplugins.wimporter>=0.8',
            'tiddlywebplugins.register',
            'tiddlywebplugins.instancer>=0.3.2',
            'tiddlywebplugins.openid2',
            'tiddlywebplugins.logout',
            'tiddlywebplugins.form',
            'httpexceptor',
            ],
        include_package_data = True,
        zip_safe = False,
        )
