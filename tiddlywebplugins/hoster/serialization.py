"""
Replacement HTML serialization for TidldyHoster.

If the URL is a list of bag tiddlers, we present a bag
editing interface. Otherwise we use the parent serialization.
"""

import urllib

from tiddlyweb.serializations.html import Serialization as HTMLSerialization
from tiddlyweb.model.policy import UserRequiredError, ForbiddenError
from tiddlyweb.model.bag import Bag
from tiddlyweb.model.recipe import Recipe
from tiddlyweb.web.util import encode_name

from tiddlywebplugins.hoster.template import send_template
from tiddlywebplugins.hoster.data import determine_publicity, get_user_object

class Serialization(HTMLSerialization):

    def list_tiddlers(self, bag):
        """
        If the URL is a list of bag tiddlers, we present a bag
        editing interface. Otherwise we use the parent serialization.
        """
        if (self.environ['wsgiorg.routing_args'][1].get('tiddler_name')):
            return HTMLSerialization.list_tiddlers(self, bag)

        try:
            name = self.environ['wsgiorg.routing_args'][1]['bag_name']
            return self._bag_list(bag)
        except KeyError: # not a bag link
            try:
                name = self.environ['wsgiorg.routing_args'][1]['recipe_name']
                name = urllib.unquote(name)
                name = unicode(name, 'utf-8')
                return self._recipe_list(bag, name)
            except KeyError:
                if bag.name == 'feedbag':
                    return self._bag_list(bag)
                return HTMLSerialization.list_tiddlers(self, bag)

    def _recipe_list(self, bag, recipe_name):
        representation_link = '%s/recipes/%s/tiddlers' % (
                self._server_prefix(), encode_name(recipe_name))
        representations = self._tiddler_list_header(representation_link)
        user_object = get_user_object(self.environ)
        recipe = self.environ['tiddlyweb.store'].get(Recipe(recipe_name))
        publicity = ''
        try:
            recipe.policy.allows(user_object, 'manage')
            policy = recipe.policy
            if policy.read == [user_object['name']]:
                publicity = 'private'
            elif policy.read == []:
                publicity = 'public'
            else:
                publicity = 'custom'
            delete = True
        except (UserRequiredError, ForbiddenError):
            policy = None
            delete = False
        data = {'title': 'TiddlyHoster Recipe %s' % recipe.name, 'policy': policy,
                'publicity': publicity, 'delete': delete,
                'recipe': recipe, 'bag': bag, 'representations': representations}
        del self.environ['tiddlyweb.title']
        return send_template(self.environ, 'recipelist.html', data)


    def _bag_list(self, bag):
        if bag.name == 'feedbag':
            representation_link = '%s/feedbag' % (self._server_prefix())
        else:
            representation_link = '%s/bags/%s/tiddlers' % (
                    self._server_prefix(), encode_name(bag.name))
        representations = self._tiddler_list_header(representation_link)
        user_object = get_user_object(self.environ)
        publicity = ''
        try:
            bag.policy.allows(user_object, 'manage')
            policy = bag.policy
            publicity = determine_publicity(user_object, policy)
        except (UserRequiredError, ForbiddenError):
            policy = None
        try:
            bag.policy.allows(user_object, 'delete')
            delete = True
        except (UserRequiredError, ForbiddenError):
            delete = False
        data = {'title': 'TiddlyHoster Bag %s' % bag.name, 'policy': policy,
                'publicity': publicity, 'delete': delete,
                'bag': bag, 'representations': representations}
        del self.environ['tiddlyweb.title']
        return send_template(self.environ, 'baglist.html', data)
