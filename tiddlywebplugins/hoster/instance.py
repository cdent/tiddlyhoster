
from tiddlywebwiki.instance import (store_structure
        as tiddlywebwiki_store_structure)

store_structure = {}

store_structure['bags'] = tiddlywebwiki_store_structure['bags']
store_structure['recipes'] = tiddlywebwiki_store_structure['recipes']

store_contents = {}
store_contents['hoster'] = ['basecontent/main.css.tid',
        'basecontent/drop.js.tid',
        'basecontent/bagmanage.js.tid',
        'basecontent/generaterecipe.js.tid',
        'basecontent/recipemanage.js.tid',
        'basecontent/templater.js.tid',
        'basecontent/bagdesc.js.tid',
        'basecontent/json2.js.tid',
        'basecontent/ui-bg_flat_0_aaaaaa_40x100.png.tid',
        'basecontent/ui-bg_flat_75_ffffff_40x100.png.tid',
        'basecontent/ui-bg_glass_55_fbf9ee_1x400.png.tid',
        'basecontent/ui-bg_glass_65_ffffff_1x400.png.tid',
        'basecontent/ui-bg_glass_75_dadada_1x400.png.tid',
        'basecontent/ui-bg_glass_75_e6e6e6_1x400.png.tid',
        'basecontent/ui-bg_glass_95_fef1ec_1x400.png.tid',
        'basecontent/ui-bg_highlight-soft_75_cccccc_1x100.png.tid',
        'basecontent/ui-icons_222222_256x240.png.tid',
        'basecontent/ui-icons_2e83ff_256x240.png.tid',
        'basecontent/ui-icons_454545_256x240.png.tid',
        'basecontent/ui-icons_888888_256x240.png.tid',
        'basecontent/ui-icons_cd0a0a_256x240.png.tid',
        'basecontent/ui.css.tid',
        'basecontent/cat.png',
        'basecontent/pencil.png',
        'basecontent/delete.png',
        'basecontent/credits.tid',
        'basecontent/picture_add.png',
        'basecontent/cats.jpg']


store_contents['help'] = ['basecontent/WorkspaceConfig.tid']

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
}
