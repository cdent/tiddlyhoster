"""
Host customizable TiddlyWikis on TiddlyWeb.
"""

__version__ = '0.2'

import Cookie
import time
import urllib

from hashlib import md5

from tiddlyweb.model.policy import UserRequiredError, ForbiddenError
from tiddlyweb.model.user import User
from tiddlyweb.model.bag import Bag
from tiddlyweb.model.policy import Policy
from tiddlyweb.model.recipe import Recipe
from tiddlyweb.model.tiddler import Tiddler
from tiddlyweb.store import NoBagError, NoTiddlerError, NoUserError, NoRecipeError
from tiddlyweb.web.http import HTTP303, HTTP404, HTTP400
from tiddlyweb.web.util import server_base_url, encode_name, bag_url, recipe_url
from tiddlyweb.web.wsgi import HTMLPresenter
from tiddlywebplugins.utils import replace_handler, do_html, require_role
from tiddlyweb.wikitext import render_wikitext
from tiddlywebplugins.hoster.instance import instance_tiddlers
from tiddlyweb.serializations.html import Serialization as HTMLSerialization
from tiddlyweb.manage import make_command

from tiddlywebplugins.hoster.template import send_template
from tiddlywebplugins.hoster.data import (
        get_stuff, get_user_object, get_member_names, first_time_check,
        get_friends, get_followers, get_email_tiddler, get_profile,
        ensure_public_recipe, ensure_private_recipe,
        ensure_public_bag, ensure_protected_bag, ensure_user_bag,
        ensure_private_bag, get_favorited_bags, get_favorites,
        public_policy, protected_policy, private_policy)
from tiddlywebplugins.hoster.presenter import PrettyPresenter

def init(config):
    import tiddlywebwiki
    import tiddlywebplugins.register
    import tiddlywebplugins.wimporter
    tiddlywebwiki.init(config)
    tiddlywebplugins.register.init(config)
    tiddlywebplugins.wimporter.init(config)
    
    # XXX this clobbers?
    config['instance_tiddlers'] = instance_tiddlers

    if config['selector']:
        replace_handler(config['selector'], '/', dict(GET=front))
        config['selector'].add('/help', GET=help_page)
        config['selector'].add('/formeditor', GET=get_profiler, POST=post_profile)
        config['selector'].add('/addemail', POST=add_email)
        config['selector'].add('/follow', POST=add_friend)
        config['selector'].add('/logout', POST=logout)
        config['selector'].add('/members', GET=members_list)
        config['selector'].add('/bagfavor', POST=bag_favor)
        config['selector'].add('/bagpolicy', POST=entity_policy)
        config['selector'].add('/recipepolicy', POST=entity_policy)
        config['selector'].add('/createrecipe', GET=get_createrecipe,
                POST=post_createrecipe)
        config['selector'].add('/createbag', GET=get_createbag,
                POST=post_createbag)
        # THE FOLLOWING MUST COME LAST
        config['selector'].add('/{userpage:segment}', GET=user_page)

        presenter_index = config['server_response_filters'].index(HTMLPresenter)
        config['server_response_filters'][presenter_index] = PrettyPresenter
        # XXX: disable the specialized extractor for now. The roles it
        # adds are not used (yet).
        #simple_cookie_index = config['extractors'].index('simple_cookie')
        #config['extractors'][simple_cookie_index] = 'tiddlywebplugins.hoster.extractor'

        new_serializer = ['tiddlywebplugins.hoster.serialization', 'text/html; charset=UTF-8']
        config['serializers']['text/html'] = new_serializer
        config['serializers']['default'] = new_serializer
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
@require_role('MEMBER')
def get_createbag(environ, start_response):
    return send_template(environ, 'bag.html', {'timestamp': int(time.time())}) 


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
        bag.skinny = True
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
    return send_template(environ, 'recipe.html', {'timestamp': int(time.time())}) 


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
        bag.skinny = True
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
    return send_template(environ, 'members.html', {'members': members}) 


def logout(environ, start_response):
    cookie = Cookie.SimpleCookie()
    path = environ['tiddlyweb.config']['server_prefix']
    cookie['tiddlyweb_user'] = ''
    cookie['tiddlyweb_user']['path'] = '%s/' % path
    cookie['tiddlyweb_user']['expires'] = '%s' % (time.ctime(time.time()-6000))
    uri = server_base_url(environ)
    start_response('303 See Other', [
        ('Set-Cookie', cookie.output(header='')),
        ('Location', uri),
        ])
    return uri


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
    bag.skinny = True
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
def bag_favor(environ, start_response):
    user = get_user_object(environ)
    store = environ['tiddlyweb.store']
    ensure_user_bag(store, user['name'])
    new_favorite = environ['tiddlyweb.query'].get('bag', [''])[0]
    favorites = get_favorites(store, user['name'])
    # XXX I suppose a set would be okay here.
    if new_favorite and new_favorite not in favorites:
        favorites.append(new_favorite)
    tiddler = store.get(Tiddler('favorites', user['name']))
    tiddler.text = '\n'.join(favorites)
    store.put(tiddler)
    raise HTTP303('%s/home' % server_base_url(environ))


def add_friend(environ, start_response):
    user = get_user_object(environ)
    store = environ['tiddlyweb.store']
    ensure_user_bag(store, user['name'])
    new_friend = environ['tiddlyweb.query'].get('name', [''])[0]
    friends = get_friends(store, user['name'])
    if new_friend and new_friend not in friends:
        friends.append(new_friend)
    tiddler = store.get(Tiddler('friends', user['name']))
    tiddler.text = '\n'.join(friends)
    store.put(tiddler)
    raise HTTP303('%s/home' % server_base_url(environ))


def add_email(environ, start_response):
    user = get_user_object(environ)
    store = environ['tiddlyweb.store']
    ensure_user_bag(store, user['name'])
    tiddler = Tiddler('email', user['name'])
    email = environ['tiddlyweb.query'].get('email', [''])[0]
    tiddler.text = email
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
    return send_template(environ, 'home.html')


@do_html()
def user_page(environ, start_response):
    userpage = environ['wsgiorg.routing_args'][1]['userpage']
    user = environ['tiddlyweb.usersign']

    first_time_check(environ, user)

    if userpage == 'home':
        userpage = user['name']

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
    kept_recipes = get_stuff(store, store.list_recipes(), user, userpage)
    kept_bags = get_stuff(store, store.list_bags(), user, userpage)
    kept_favorites = get_stuff(store, get_favorited_bags(store, userpage),
            user)
    email = get_email_tiddler(store, userpage)
    email_md5 = md5(email.lower()).hexdigest()
    data = {'bags': kept_bags,
            'user_friends': user_friend_names,
            'friends': friends,
            'recipes': kept_recipes,
            'favorites': kept_favorites,
            'home': userpage,
            'profile': profile_html,
            'email': email,
            'email_md5': email_md5,
            'user': get_user_object(environ)}

    return send_template(environ, 'profile.html', data)


@do_html()
def get_profiler(environ, start_response):
    usersign = environ['tiddlyweb.usersign']
    store = environ['tiddlyweb.store']
    username = usersign['name']

    if not 'MEMBER' in usersign['roles']:
        raise HTTP404('bad edit')

    tiddler = get_profile(store, usersign, username)
    bag = Bag(tiddler.bag)
    bag.skinny = True
    bag = store.get(bag)
    bag.policy.allows(usersign, 'write')

    return_url = '%s/home' % server_base_url(environ)

    data = {}
    data['tiddler'] = tiddler
    data['return_url'] = return_url
    return send_template(environ, 'profile_edit.html', data)


def post_profile(environ, start_response):
    usersign = environ['tiddlyweb.usersign']
    text = environ['tiddlyweb.query'].get('text', [''])[0]
    title = environ['tiddlyweb.query'].get('title', [''])[0]
    bag = environ['tiddlyweb.query'].get('bag', [''])[0]
    return_url = environ['tiddlyweb.query'].get('return_url', ['/home'])[0]

    store = environ['tiddlyweb.store']

    tiddler = Tiddler(title, bag)
    tiddler.text = text
    tiddler.modifier = usersign['name']
    bag = Bag(bag)
    try:
        bag.skinny = True
        bag = store.get(bag)
    except NoBagError, exc:
        raise HTTP404('tiddler %s not found: %s' % (tiddler.title, exc))

    bag.policy.allows(usersign, 'write')

    store.put(tiddler)

    raise HTTP303(return_url)
