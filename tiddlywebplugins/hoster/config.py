
PACKAGE_NAME = 'tiddlywebplugins.hoster'

config = {
        'instance_pkgstores': ['tiddlywebplugins.console', 'tiddlywebwiki',
            PACKAGE_NAME],
        'auth_systems': ['tiddlywebplugins.openid2'],
        'css_uri': '/bags/hoster/tiddlers/main.css',
        'register.start_href': '/home',
        'cookie_age': '2592000',
}
