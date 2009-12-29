
from tiddlywebplugins.instancer.util import get_tiddler_locations
from tiddlywebwiki.instance import store_contents, store_structure

store_contents['hoster'] = ['file:basecontent/main.css.tid',
        'file:basecontent/drop.js.tid',
        'file:basecontent/bagmanage.js.tid',
        'file:basecontent/delete.gif.tid',
        'file:basecontent/json2.js.tid']

store_contents['commentsystem'] = ['file:basecontent/ViewTemplate.tid',
        'http://svn.tiddlywiki.org/Trunk/contributors/MichaelMahemoff/plugins/CommentsPlugin/CommentsPlugin.js',
        ]

store_contents['help'] = ['file:basecontent/WorkspaceConfig.tid']

store_structure['bags']['hoster'] = {
        'desc': 'useful stuff that hoster wants to use',
        'policy': {
            'read': [],
            'write': ['R:ADMIN'],
            'create': ['R:ADMIN'],
            'delete': ['R:ADMIN'],
            'manage': ['R:ADMIN'],
            'owner': 'administrator',
            }
        }

store_structure['bags']['helpcomments'] = {
        'desc': 'target bag for saving comments on help',
        'policy': {
            'read': [],
            'write': ['R:ADMIN'],
            'create': [],
            'delete': ['R:ADMIN'],
            'manage': ['R:ADMIN'],
            'owner': 'administrator',
            }
        }

store_structure['bags']['commentsystem'] = {
        'desc': 'comments mgt tools',
        'policy': {
            'read': [],
            'write': ['R:ADMIN'],
            'create': ['R:ADMIN'],
            'delete': ['R:ADMIN'],
            'manage': ['R:ADMIN'],
            'owner': 'administrator',
            }
        }

store_structure['bags']['help'] = {
        'desc': 'help documentation',
        'policy': {
            'read': [],
            'write': ['R:ADMIN'],
            'create': ['R:ADMIN'],
            'delete': ['R:ADMIN'],
            'manage': ['R:ADMIN'],
            'owner': 'administrator',
            }
        }

store_structure['recipes']['hoster'] = {
        'desc': 'useful stuff for the admin to edit',
        'policy': {
            'read': ['R:ADMIN'],
            'manage': ['R:ADMIN'],
            'owner': 'administrator',
            },
        'recipe': [
            ('system', ''),
            ('hoster', ''),
            ],
        }

store_structure['recipes']['help'] = {
        'desc': 'help wiki, with comments',
        'policy': {
            'read': [],
            'manage': ['R:ADMIN'],
            'owner': 'administrator',
            },
        'recipe': [
            ('system', ''),
            ('commentsystem', ''),
            ('help', ''),
            ('helpcomments', ''),
            ],
        }

instance_config = {
        'system_plugins': ['tiddlywebplugins.hoster'],
        'twanager_plugins': ['tiddlywebplugins.hoster'],
        'auth_systems': ['openid'],
        'css_uri': '/bags/hoster/tiddlers/main.css',
        'register.start_href': '/home',
        'cookie_age': '2592000',
        }

instance_tiddlers = get_tiddler_locations(store_contents,
        'tiddlywebplugins.hoster')
