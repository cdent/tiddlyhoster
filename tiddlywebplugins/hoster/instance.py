
from tiddlywebplugins.instancer.util import get_tiddler_locations
from tiddlywebwiki.instance import store_contents, store_structure

store_contents['hoster'] = ['file:basecontent/main.css.tid',
        'file:basecontent/drop.js.tid',
        'file:basecontent/bagmanage.js.tid',
        'file:basecontent/generaterecipe.js.tid',
        'file:basecontent/recipemanage.js.tid',
        'file:basecontent/templater.js.tid',
        'file:basecontent/bagdesc.js.tid',
        'file:basecontent/json2.js.tid',
        'file:basecontent/ui-bg_flat_0_aaaaaa_40x100.png.tid',
        'file:basecontent/ui-bg_flat_75_ffffff_40x100.png.tid',
        'file:basecontent/ui-bg_glass_55_fbf9ee_1x400.png.tid',
        'file:basecontent/ui-bg_glass_65_ffffff_1x400.png.tid',
        'file:basecontent/ui-bg_glass_75_dadada_1x400.png.tid',
        'file:basecontent/ui-bg_glass_75_e6e6e6_1x400.png.tid',
        'file:basecontent/ui-bg_glass_95_fef1ec_1x400.png.tid',
        'file:basecontent/ui-bg_highlight-soft_75_cccccc_1x100.png.tid',
        'file:basecontent/ui-icons_222222_256x240.png.tid',
        'file:basecontent/ui-icons_2e83ff_256x240.png.tid',
        'file:basecontent/ui-icons_454545_256x240.png.tid',
        'file:basecontent/ui-icons_888888_256x240.png.tid',
        'file:basecontent/ui-icons_cd0a0a_256x240.png.tid',
        'file:basecontent/ui.css.tid',
        'file:basecontent/cat.png',
        'file:basecontent/pencil.png',
        'file:basecontent/delete.png',
        'file:basecontent/credits.tid',
        'file:basecontent/picture_add.png',
        'file:basecontent/cats.jpg',
        ]

#store_contents['commentsystem'] = ['file:basecontent/ViewTemplate.tid',
#        'http://svn.tiddlywiki.org/Trunk/contributors/MichaelMahemoff/plugins/CommentsPlugin/CommentsPlugin.js',
#        ]

store_contents['help'] = ['file:basecontent/WorkspaceConfig.tid']

store_structure['bags']['notifications'] = {
        'desc': 'Latest notifications from the system.',
        'policy': {
            'read': [],
            'write': ['R:ADMIN'],
            'create': ['R:ADMIN'],
            'delete': ['R:ADMIN'],
            'manage': ['R:ADMIN'],
            'owner': 'administrator',
            }
        }

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

# store_structure['bags']['commentsystem'] = {
#         'desc': 'comments mgt tools',
#         'policy': {
#             'read': [],
#             'write': ['R:ADMIN'],
#             'create': ['R:ADMIN'],
#             'delete': ['R:ADMIN'],
#             'manage': ['R:ADMIN'],
#             'owner': 'administrator',
#             }
#         }

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
        'auth_systems': ['tiddlywebplugins.openid2'],
        'css_uri': '/bags/hoster/tiddlers/main.css',
        'register.start_href': '/home',
        'cookie_age': '2592000',
        }

instance_tiddlers = get_tiddler_locations(store_contents,
        'tiddlywebplugins.hoster')
