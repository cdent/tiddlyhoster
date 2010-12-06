"""
Routines for manipulating hoster data.

Just as a way of extracting some stuff to another file,
for now.
"""

from tiddlyweb.control import filter_tiddlers
from tiddlyweb.model.tiddler import Tiddler
from tiddlyweb.store import (StoreError, NoTiddlerError, NoBagError,
        NoRecipeError)
from tiddlyweb.model.policy import UserRequiredError, ForbiddenError, Policy
from tiddlyweb.model.user import User
from tiddlyweb.model.recipe import Recipe
from tiddlyweb.model.bag import Bag

from tiddlywebplugins.utils import ensure_bag

def get_followers(store, username):
    """
    Get all the users who have username as a friend.
    """
    member_names = get_member_names(store)
    followers = []
    for member_name in member_names:
        if member_name == username:
            continue
        if username in get_friends(store, member_name):
            followers.append(member_name)
    return followers


def get_bookmarks(store, username):
    tiddler = Tiddler('bookmarks', username)
    try:
        tiddler = store.get(tiddler)
        bookmarks = tiddler.text.splitlines()
    except NoTiddlerError:
        bookmarks = []
    return bookmarks


def get_favorites(store, username):
    tiddler = Tiddler('favorites', username)
    try:
        tiddler = store.get(tiddler)
        favorites = tiddler.text.splitlines()
    except NoTiddlerError:
        favorites = []
    return favorites


def get_favorited_bags(store, username):
    favorites = get_favorites(store, username)
    bags = []
    for favorite in favorites:
        try:
            bag = Bag(favorite)
            bags.append(store.get(bag))
        except NoBagError:
            pass # don't care if it doesn't exist
    return bags


def get_bookmarked_recipes(store, username):
    bookmarks = get_bookmarks(store, username)
    recipes = []
    for bookmark in bookmarks:
        try:
            recipe = Recipe(bookmark)
            recipes.append(store.get(recipe))
        except NoRecipeError:
            pass # don't care if it doesn't exist
    return recipes


def get_friends(store, username):
    """
    Get the list of all users that username has chosen to follow.
    """
    tiddler = Tiddler('friends', username)
    try:
        tiddler = store.get(tiddler)
        friends = tiddler.text.splitlines()
    except NoTiddlerError:
        friends = []
    return friends


def get_member_names(store):
    """
    Get all the username that have the role MEMBER.
    """
    def _reify_user(username):
        return store.get(username)
    names = (user.usersign for user in store.list_users() if
            'MEMBER' in _reify_user(user).list_roles())
    return names


def get_email_tiddler(store, userpage):
    try:
        tiddler = Tiddler('email', userpage)
        tiddler = store.get(tiddler)
    except NoTiddlerError:
        tiddler.text = ''
    return tiddler.text


def get_notice(environ):
    store = environ['tiddlyweb.store']
    try:
        tiddlers = filter_tiddlers(store.list_bag_tiddlers(Bag('notifications')),
                'sort=-modified;limit=1', environ=environ)
        tiddler = store.get(tiddlers.next())
    except (StopIteration, StoreError):
        tiddler = Tiddler('profile')
        tiddler.text = "''No Current Notifications''.\n"
    return tiddler


def get_profile(store, user, userpage):
    try:
        tiddler = Tiddler('profile', userpage)
        tiddler = store.get(tiddler)
    except NoTiddlerError:
        if user['name'] == userpage:
            ensure_user_bag(store, userpage)
            tiddler.text = '!!!You can make a profile!\n'
        else:
            tiddler.text = '!!!No profile yet!\n'
    return tiddler

def get_stuff(store, entities, user, owner=None):
    """
    Get a sub-list of recipes or bags from the provided
    list which is readable by the given user and owned
    by the user represented given owner.
    """
    kept_entities = []
    for entity in entities:
        entity = store.get(entity)
        try:
            entity.policy.allows(user, 'read')
            if owner and not entity.policy.owner == owner:
                continue
            kept_entities.append(entity)
        except (UserRequiredError, ForbiddenError):
            pass
    return kept_entities


def get_user_object(environ):
    user = environ['tiddlyweb.usersign']
    if user['name'] == 'GUEST':
        user['pretty_name'] = 'GUEST'
    elif 'MEMBER' in user['roles']:
        store = environ['tiddlyweb.store']
        userobject = store.get(User(user['name']))
        if userobject.note:
            user['pretty_name'] = userobject.note
        else:
            user['pretty_name'] = user['name']
    else:
        user['pretty_name'] = user['name']
    return user


def determine_publicity(user, policy):
    name = user['name']
    if (policy.read == [name] and
        policy.write == [name] and
        policy.create == [name] and
        policy.delete == [name] and
        policy.manage == [name]):
        return 'private'
    if (policy.read == [] and
        policy.write == [name] and
        policy.create == [name] and
        policy.delete == [name] and
        policy.manage == [name]):
        return 'protected'
    if (policy.read == [] and
        policy.write == [] and
        policy.create == [] and
        policy.delete == [] and
        policy.manage == [name]):
        return 'public'
    return 'custom'


def ensure_private_recipe(store, username):
    name = '%s-private' % username
    pname = '%s-public' % username
    recipe = Recipe(name)
    recipe.policy.read = [username]
    recipe.policy.manage = [username]
    recipe.policy.owner = username
    recipe.set_recipe([
        ('system', ''),
        (pname, ''),
        (name, ''),
        ])
    store.put(recipe)


def ensure_public_recipe(store, username):
    name = '%s-public' % username
    recipe = Recipe(name)
    recipe.policy.read = []
    recipe.policy.manage = [username]
    recipe.policy.owner = username
    recipe.set_recipe([
        ('system', ''),
        (name, ''),
        ])
    store.put(recipe)


def ensure_public_bag(store, username, desc='',  name=None):
    policy = _public_policy(username)
    if name == None:
        name = '%s-public' % username
    return ensure_bag(name, store, policy, description=desc)

def ensure_protected_bag(store, username, desc='', name=None):
    policy = _protected_policy(username)
    if name == None:
        name = '%s-protected' % username
    return ensure_bag(name, store, policy, description=desc)

def ensure_private_bag(store, username, desc='', name=None):
    policy = _private_policy(username)
    if name == None:
        name = '%s-private' % username
    return ensure_bag(name, store, policy, description=desc)


def ensure_user_bag(store, userpage):
    policy = {}
    policy['manage'] = ['R:ADMIN']

    for constraint in ['read', 'write', 'create', 'delete']:
        policy[constraint] = [userpage]

    policy['owner'] = userpage

    ensure_bag(userpage, store, policy)


def first_time_check(environ, user):
    username = user['name']
    store = environ['tiddlyweb.store']
    try:
        bag = Bag(username)
        store.get(bag)
    except NoBagError:
        ensure_public_bag(store, username)
        ensure_private_bag(store, username)
        ensure_public_recipe(store, username)
        ensure_private_recipe(store, username)
        ensure_user_bag(store, username)


def public_policy(username):
    return _policy_dict_to_policy(_public_policy(username))


def protected_policy(username):
    return _policy_dict_to_policy(_protected_policy(username))


def private_policy(username):
    return _policy_dict_to_policy(_private_policy(username))


def _public_policy(username):
    policy = {}
    policy['manage'] = [username]
    for constraint in ['read', 'write', 'create', 'delete']:
        policy[constraint] = []
    policy['owner'] = username
    return policy


def _protected_policy(username):
    policy = {}
    policy['read'] = []
    for constraint in ['write', 'create', 'delete', 'manage']:
        policy[constraint] = [username]
    policy['owner'] = username
    return policy


def _private_policy(username):
    policy = {}
    for constraint in ['read', 'write', 'create', 'delete', 'manage']:
        policy[constraint] = [username]
    policy['owner'] = username
    return policy


def _policy_dict_to_policy(policy_dict):
    policy = Policy()
    for constraint in policy_dict:
        setattr(policy, constraint, policy_dict[constraint])
    return policy
