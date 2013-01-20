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
    """
    Customize the output for hoster. When listing tiddlers,
    do a lot of interesting stuff. Otherwise wrap the
    HTML into a template: pretty.html.
    """

    def _footer(self):
        return ''

    def _header(self):
        return ''

    def _templatize(self, output):
        if isinstance(output, basestring):
            output = [output]
        data = {
                'output': output,
                'title': self.environ['tiddlyweb.title'],
        }
        return send_template(self.environ, 'pretty.html', data)

    def list_recipes(self, recipes):
        return self._templatize(HTMLSerialization.list_recipes(self, recipes))

    def list_bags(self, bags):
        return self._templatize(HTMLSerialization.list_bags(self, bags))

    def list_tiddlers(self, tiddlers):
        """
        If the URL is a list of bag tiddlers, we present a bag
        editing interface. Otherwise we use the parent serialization.
        """
        if (self.environ['wsgiorg.routing_args'][1].get('tiddler_name')):
            return HTMLSerialization.list_tiddlers(self, tiddlers)

        try:
            name = self.environ['wsgiorg.routing_args'][1]['bag_name']
            return self._bag_list(tiddlers)
        except KeyError: # not a bag link
            try:
                name = self.environ['wsgiorg.routing_args'][1]['recipe_name']
                name = urllib.unquote(name)
                name = unicode(name, 'utf-8')
                return self._recipe_list(tiddlers, name)
            except KeyError:
                return self._bag_list(tiddlers)

    def recipe_as(self, recipe):
        return self._templatize(HTMLSerialization.recipe_as(self, recipe))

    def bag_as(self, bag):
        return self._templatize(HTMLSerialization.bag_as(self, bag))

    def tiddler_as(self, tiddler):
        return self._templatize(HTMLSerialization.tiddler_as(self, tiddler))

    def _recipe_list(self, tiddlers, recipe_name):
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
                'recipe': recipe, 'tiddlers': tiddlers, 'representations': representations}
        del self.environ['tiddlyweb.title']
        return send_template(self.environ, 'recipelist.html', data)

    def _bag_list(self, tiddlers):
        if '/feedbag' in self.environ['selector.matches'][0]:
            representation_link = '%s/feedbag' % (self._server_prefix())
            bag = Bag('feedbag')
            bag.policy.manage = ["NONE"]
            bag.policy.delete = ["NONE"]
            bag.desc = 'Recent Public Stuff'
        else:
            name = self.environ['wsgiorg.routing_args'][1]['bag_name']
            name = urllib.unquote(name)
            name = name.decode('utf-8')
            representation_link = '%s/bags/%s/tiddlers' % (
                    self._server_prefix(), encode_name(name))
            bag = self.environ['tiddlyweb.store'].get(Bag(name))
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
                'bag': bag, 'tiddlers': tiddlers, 'representations': representations}
        del self.environ['tiddlyweb.title']
        return send_template(self.environ, 'baglist.html', data)
