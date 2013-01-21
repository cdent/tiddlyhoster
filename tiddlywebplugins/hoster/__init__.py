"""
Host customizable TiddlyWikis on TiddlyWeb.
"""

__version__ = '0.9.40'

import Cookie
import time
import urllib

from hashlib import md5
from httpexceptor import HTTP302, HTTP303, HTTP404, HTTP400

from tiddlyweb.model.policy import UserRequiredError, ForbiddenError
from tiddlyweb.model.user import User
from tiddlyweb.model.bag import Bag
from tiddlyweb.model.collections import Tiddlers
from tiddlyweb.model.policy import Policy
from tiddlyweb.model.recipe import Recipe
from tiddlyweb.model.tiddler import Tiddler
from tiddlyweb.store import (NoBagError, NoTiddlerError,
        NoUserError, NoRecipeError, StoreError)
from tiddlyweb.web.util import (server_base_url, encode_name,
        bag_url, recipe_url, tiddler_url)
from tiddlywebplugins.utils import replace_handler, do_html, require_role
from tiddlyweb.wikitext import render_wikitext
from tiddlywebplugins.hoster.instance import instance_tiddlers
from tiddlyweb.manage import make_command
from tiddlyweb.web.sendtiddlers import send_tiddlers

from tiddlywebplugins.hoster.template import send_template
from tiddlywebplugins.hoster.data import (
        get_stuff, get_user_object, get_member_names, first_time_check,
        get_friends, get_followers, get_email_tiddler, get_profile,
        ensure_public_recipe, ensure_private_recipe, get_notice,
        ensure_public_bag, ensure_protected_bag, ensure_user_bag,
        ensure_private_bag, get_bookmarked_recipes,
        get_favorited_bags, get_favorites, get_bookmarks,
        public_policy, protected_policy, private_policy)

def init(config):
    import tiddlywebwiki
    import tiddlywebplugins.register
    import tiddlywebplugins.wimporter
    import tiddlywebplugins.logout
    import tiddlywebplugins.form
    tiddlywebwiki.init(config)
    tiddlywebplugins.register.init(config)
    tiddlywebplugins.wimporter.init(config)
    tiddlywebplugins.logout.init(config)
    tiddlywebplugins.form.init(config)
    
    # XXX this clobbers?
    config['instance_tiddlers'] = instance_tiddlers

    if 'selector' in config:
        replace_handler(config['selector'], '/', dict(GET=front))
        config['selector'].add('/help', GET=help_page)
        config['selector'].add('/login', GET=login)
        config['selector'].add('/uploader', GET=uploader)
        config['selector'].add('/formeditor', GET=get_tiddler_edit,
                POST=post_tiddler_edit)
        config['selector'].add('/addemail', POST=add_email)
        config['selector'].add('/follow', POST=add_friend)
        config['selector'].add('/members', GET=members_list)
        config['selector'].add('/bagfavor', POST=bag_favor)
        config['selector'].add('/recipefavor', POST=recipe_favor)
        config['selector'].add('/bagpolicy', POST=entity_policy)
        config['selector'].add('/recipepolicy', POST=entity_policy)
        config['selector'].add('/createrecipe', GET=get_createrecipe,
                POST=post_createrecipe)
        config['selector'].add('/createbag', GET=get_createbag,
                POST=post_createbag)
        config['selector'].add('/feedbag[.{format}]', GET=public_stuff)
        config['selector'].add('/home', GET=get_home)
        # THE FOLLOWING MUST COME LAST
        config['selector'].add('/{userpage:segment}', GET=user_page)

        # XXX: disable the specialized extractor for now. The roles it
        # adds are not used (yet).
        #simple_cookie_index = config['extractors'].index('simple_cookie')
        #config['extractors'][simple_cookie_index] = 'tiddlywebplugins.hoster.extractor'

        new_serializer = ['tiddlywebplugins.hoster.serialization', 'text/html; charset=UTF-8']
        config['serializers']['text/html'] = new_serializer
    else:
        @make_command()
        def upstore(args):
            """Update the store structure."""
            from tiddlywebplugins.hoster.instance import store_structure
            from tiddlywebplugins.instancer import Instance
            from tiddlyweb.config import config
            instance = Instance('.', config)
            instance._init_store(store_structure)


@do_html()
def login(environ, start_response):
    user = environ['tiddlyweb.usersign']
    if user['name'] != 'GUEST' and 'MEMBER' in user['roles']:
        raise HTTP302(server_base_url(environ) + '/' + encode_name(user['name']))
    return send_template(environ, 'login.html')


@do_html()
@require_role('MEMBER')
def get_createbag(environ, start_response):
    return send_template(environ, 'bag.html', {
        'timestamp': int(time.time()), 'title': 'Create Bag'}) 


def public_stuff(environ, start_response):
    """
    A collection of the most recent stuff.
    A place where _all_ the content readable
    by the current user can be viewed.
    """
    user = get_user_object(environ)
    store = environ['tiddlyweb.store']
    kept_bags = get_stuff(store, store.list_bags(), user)
    tiddlers = Tiddlers()
    for bag in kept_bags:
        bag = store.get(bag)
        for tiddler in store.list_bag_tiddlers(bag):
            tiddlers.add(tiddler)
    return send_tiddlers(environ, start_response, tiddlers=tiddlers)


@require_role('MEMBER')
def post_createbag(environ, start_response):
    user = get_user_object(environ)
    store = environ['tiddlyweb.store']
    bag_name = environ['tiddlyweb.query'].get('bag', [''])[0]
    publicity = environ['tiddlyweb.query'].get('publicity', [''])[0]
    description = environ['tiddlyweb.query'].get('description', [''])[0]

    if not bag_name:
        raise HTTP400('missing data')

    bag = Bag(bag_name)

    try:
        bag = store.get(bag)
        raise HTTP400('bag exists')
    except NoBagError:
        pass
    if publicity == 'public':
        bag = ensure_public_bag(
                store, user['name'], desc=description, name=bag_name)
    elif publicity == 'protected':
        bag = ensure_protected_bag(
                store, user['name'], desc=description, name=bag_name)
    else:
        bag = ensure_private_bag(
                store, user['name'], desc=description, name=bag_name)

    # the bag has already been stored

    raise HTTP303('%s/tiddlers' % bag_url(environ, bag))


@do_html()
@require_role('MEMBER')
def get_createrecipe(environ, start_response):
    return send_template(environ, 'recipe.html', {
        'timestamp': int(time.time()), 'title': 'Create Recipe'}) 


@require_role('MEMBER')
def post_createrecipe(environ, start_response):
    user = get_user_object(environ)
    store = environ['tiddlyweb.store']
    recipe_name = environ['tiddlyweb.query'].get('recipe', [''])[0]
    bag_name = environ['tiddlyweb.query'].get('bag', [''])[0]
    publicity = environ['tiddlyweb.query'].get('publicity', [''])[0]
    description = environ['tiddlyweb.query'].get('description', [''])[0]
    if not bag_name or not recipe_name:
        raise HTTP400('missing data')

    recipe = Recipe(recipe_name)
    bag = Bag(bag_name)
    try:
        recipe = store.get(recipe)
        raise HTTP400('recipe exists')
    except NoRecipeError:
        pass

    try:
        bag = store.get(bag)
        try:
            bag.policy.allows(user, 'read')
        except (UserRequiredError, ForbiddenError):
            raise HTTP400('bag not readable')
    except NoBagError:
        bag.policy.owner = user['name']
        for constraint in ['read', 'write', 'create', 'delete', 'manage']:
            setattr(bag.policy, constraint, [user['name']])
        store.put(bag)

    if publicity == 'private':
        recipe.policy.read = [user['name']]
    else:
        recipe.policy.read = []
    recipe.policy.manage = [user['name']]
    recipe.policy.owner = user['name']
    recipe.desc = description
    recipe.set_recipe([
        ('system', ''),
        (bag.name, ''),
        ])
    store.put(recipe)

    raise HTTP303('%s/home' % server_base_url(environ))


@do_html()
def members_list(environ, start_response):
    store = environ['tiddlyweb.store']
    member_names = sorted(get_member_names(store))
    members = []
    for member in member_names:
        email = get_email_tiddler(store, member)
        email_md5 = md5(email.lower()).hexdigest()
        members.append((member, email_md5))
    return send_template(environ, 'members.html', {
        'members': members, 'title': 'Members'}) 


@require_role('MEMBER')
def entity_policy(environ, start_response):
    publicity = environ['tiddlyweb.query'].get('publicity', [''])[0]
    bag_name = environ['tiddlyweb.query'].get('bag', [''])[0]
    recipe_name = environ['tiddlyweb.query'].get('recipe', [''])[0]

    if bag_name:
        return _bag_policy(environ, bag_name, publicity)
    elif recipe_name:
        return _recipe_policy(environ, recipe_name, publicity)
    else:
        raise HTTP400('missing form data')


def _bag_policy(environ, bag_name, publicity):
    user = get_user_object(environ)
    store = environ['tiddlyweb.store']
    bag = Bag(bag_name)
    bag = store.get(bag)
    bag.policy.allows(user, 'manage')

    if publicity == 'custom':
        raise HTTP303(bag_url(environ, bag) + '/tiddlers')

    if publicity == 'public':
        bag.policy = public_policy(user['name'])
    elif publicity == 'protected':
        bag.policy = protected_policy(user['name'])
    else:
        bag.policy = private_policy(user['name'])

    store.put(bag)
    raise HTTP303(bag_url(environ, bag) + '/tiddlers')


def _recipe_policy(environ, recipe_name, publicity):
    user = get_user_object(environ)
    store = environ['tiddlyweb.store']
    recipe = Recipe(recipe_name)
    recipe = store.get(recipe)
    recipe.policy.allows(user, 'manage')

    if publicity == 'custom':
        raise HTTP303(recipe_url(environ, recipe) + '/tiddlers')

    if publicity == 'public':
        recipe.policy.read = []
    else:
        recipe.policy.read = [user['name']]

    store.put(recipe)
    raise HTTP303(recipe_url(environ, recipe) + '/tiddlers')


@require_role('MEMBER')
def recipe_favor(environ, start_response):
    user = get_user_object(environ)
    store = environ['tiddlyweb.store']
    ensure_user_bag(store, user['name'])
    new_bookmark = environ['tiddlyweb.query'].get('recipe', [''])[0]
    bookmarks = get_bookmarks(store, user['name'])
    # XXX I suppose a set would be okay here.
    if new_bookmark and new_bookmark not in bookmarks:
        bookmarks.append(new_bookmark)
    tiddler = Tiddler('bookmarks', user['name'])
    try:
        tiddler = store.get(tiddler)
    except NoTiddlerError:
        pass # is okay if tiddler doesn't exist yet
    tiddler.text = '\n'.join(bookmarks)
    tiddler.modifier = user['name']
    store.put(tiddler)
    raise HTTP303('%s/home' % server_base_url(environ))


@require_role('MEMBER')
def bag_favor(environ, start_response):
    user = get_user_object(environ)
    store = environ['tiddlyweb.store']
    ensure_user_bag(store, user['name'])
    new_favorite = environ['tiddlyweb.query'].get('bag', [''])[0]
    favorites = get_favorites(store, user['name'])
    # XXX I suppose a set would be okay here.
    if new_favorite and new_favorite not in favorites:
        favorites.append(new_favorite)
    tiddler = Tiddler('favorites', user['name'])
    try:
        tiddler = store.get(tiddler)
    except NoTiddlerError:
        pass # is okay if tiddler doesn't exist yet
    tiddler.text = '\n'.join(favorites)
    tiddler.modifier = user['name']
    store.put(tiddler)
    raise HTTP303('%s/home' % server_base_url(environ))


@require_role('MEMBER')
def add_friend(environ, start_response):
    user = get_user_object(environ)
    store = environ['tiddlyweb.store']
    ensure_user_bag(store, user['name'])
    new_friend = environ['tiddlyweb.query'].get('name', [''])[0]
    friends = get_friends(store, user['name'])
    if new_friend and new_friend not in friends:
        friends.append(new_friend)
    tiddler = Tiddler('friends', user['name'])
    try:
        tiddler = store.get(tiddler)
    except NoTiddlerError:
        pass # is okay if tiddler doesn't exist yet
    tiddler.text = '\n'.join(friends)
    tiddler.modifier = user['name']
    store.put(tiddler)
    raise HTTP303('%s/home' % server_base_url(environ))


def add_email(environ, start_response):
    user = get_user_object(environ)
    store = environ['tiddlyweb.store']
    ensure_user_bag(store, user['name'])
    tiddler = Tiddler('email', user['name'])
    email = environ['tiddlyweb.query'].get('email', [''])[0]
    tiddler.text = email
    tiddler.modifier = user['name']
    store.put(tiddler)
    raise HTTP303('%s/home' % server_base_url(environ))


@do_html()
def help_page(environ, start_response):
    from tiddlyweb.web.handler.recipe import get_tiddlers
    environ['wsgiorg.routing_args'][1]['recipe_name'] = 'help'
    environ['tiddlyweb.type'] = 'text/x-tiddlywiki'
    return get_tiddlers(environ, start_response)


@do_html()
def front(environ, start_response):
    user = environ['tiddlyweb.usersign']
    if user['name'] != 'GUEST' and 'MEMBER' in user['roles']:
        raise HTTP302(server_base_url(environ) + '/' + encode_name(user['name']))
    return send_template(environ, 'home.html', { 'title': 'Welcome'})


def get_home(environ, start_response):
    user = environ['tiddlyweb.usersign']
    if user['name'] == 'GUEST' or 'MEMBER' not in user['roles']:
        raise HTTP302(server_base_url(environ) + '/')
    else:
        raise HTTP302(server_base_url(environ) + '/' + encode_name(user['name']))


@do_html()
def user_page(environ, start_response):
    userpage = environ['wsgiorg.routing_args'][1]['userpage']
    user = environ['tiddlyweb.usersign']

    userpage = _decode_name(userpage)

    first_time_check(environ, user)

    store = environ['tiddlyweb.store']

    # If we try to go to a user page that doesn't exist,
    # just go to the home page. XXX maybe should 404 instead.
    try:
        userpage_user = User(userpage)
        userpage_user = store.get(userpage_user)
    except NoUserError:
        pass # roles will be empty
    if 'MEMBER' not in userpage_user.list_roles():
        raise HTTP404('%s has no page' % userpage)

    user_friend_names = get_friends(store, user['name'])
    friend_names = sorted(get_friends(store, userpage))
    friends = []
    for name in friend_names:
        email = get_email_tiddler(store, name)
        email_md5 = md5(email.lower()).hexdigest()
        friends.append((name, email_md5))

    profile_tiddler = get_profile(store, user, userpage)
    profile_html = render_wikitext(profile_tiddler, environ)
    notice_tiddler = get_notice(environ)
    notice_html = render_wikitext(notice_tiddler, environ)
    kept_recipes = get_stuff(store, store.list_recipes(), user, userpage)
    kept_bags = get_stuff(store, store.list_bags(), user, userpage)
    kept_favorites = get_stuff(store, get_favorited_bags(store, userpage),
            user)
    kept_bookmarks = get_stuff(store, get_bookmarked_recipes(store, userpage),
            user)
    email = get_email_tiddler(store, userpage)
    email_md5 = md5(email.lower()).hexdigest()
    data = {'bags': kept_bags,
            'user_friends': user_friend_names,
            'friends': friends,
            'recipes': kept_recipes,
            'favorites': kept_favorites,
            'bookmarks': kept_bookmarks,
            'home': userpage,
            'profile': profile_html,
            'notice': {'html': notice_html,
                'modified': notice_tiddler.modified},
            'title': userpage,
            'email': email,
            'email_md5': email_md5,
            'user': get_user_object(environ)}

    return send_template(environ, 'profile.html', data)

@do_html()
def uploader(environ, start_response):
    usersign = environ['tiddlyweb.usersign']
    store = environ['tiddlyweb.store']
    bag_name = environ['tiddlyweb.query'].get('bag', [''])[0]
    username = usersign['name']
    if not 'MEMBER' in usersign['roles']:
        raise HTTP404('bad edit')
    try:
        bag = Bag(bag_name)
        bag = store.get(bag)
        bag.policy.allows(usersign, 'write')
    except NoBagError:
        raise HTTP404('bad edit')
    data = {}
    data['bag'] = bag_name
    return send_template(environ, 'uploader.html', data)


@do_html()
def get_tiddler_edit(environ, start_response):
    usersign = environ['tiddlyweb.usersign']
    store = environ['tiddlyweb.store']
    title = environ['tiddlyweb.query'].get('title', [''])[0]
    bag_name = environ['tiddlyweb.query'].get('bag', [''])[0]
    username = usersign['name']

    if not 'MEMBER' in usersign['roles']:
        raise HTTP404('bad edit')

    if not title and not bag_name:
        tiddler = get_profile(store, usersign, username)
        page_title = 'Edit Profile'
        return_url = '%s/home' % server_base_url(environ)
    elif not title:
        tiddler = Tiddler('', bag_name)
        page_title = 'Edit New Tiddler'
        return_url = ''
    else:
        tiddler = Tiddler(title, bag_name)
        page_title = 'Edit %s' % title
        return_url = tiddler_url(environ, tiddler)
        try:
            tiddler = store.get(tiddler)
        except StoreError:
            pass
    bag = Bag(tiddler.bag)
    bag = store.get(bag)
    bag.policy.allows(usersign, 'write')


    data = {}
    data['tiddler'] = tiddler
    data['return_url'] = return_url
    data['title'] = page_title
    return send_template(environ, 'profile_edit.html', data)


def post_tiddler_edit(environ, start_response):
    usersign = environ['tiddlyweb.usersign']
    text = environ['tiddlyweb.query'].get('text', [''])[0]
    title = environ['tiddlyweb.query'].get('title', [''])[0]
    bag = environ['tiddlyweb.query'].get('bag', [''])[0]
    return_url = environ['tiddlyweb.query'].get('return_url', [''])[0]

    store = environ['tiddlyweb.store']

    tiddler = Tiddler(title, bag)
    tiddler.text = text
    tiddler.modifier = usersign['name']
    bag = Bag(bag)
    try:
        bag = store.get(bag)
    except NoBagError, exc:
        raise HTTP404('tiddler %s not found: %s' % (tiddler.title, exc))

    bag.policy.allows(usersign, 'write')

    store.put(tiddler)

    if not return_url:
        return_url = tiddler_url(environ, tiddler)

    raise HTTP303(return_url)


def _decode_name(name):
    return urllib.unquote(name).decode('utf-8')
