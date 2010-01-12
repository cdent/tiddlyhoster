
from tiddlyweb.web.extractors.simple_cookie import Extractor as SimpleExtractor

from tiddlywebplugins.hoster.data import get_friends, get_followers

class Extractor(SimpleExtractor):

    def extract(self, environ, start_response):
        results = SimpleExtractor.extract(self, environ, start_response)
        if results:
            store = environ['tiddlyweb.store']
            user_dict = results
            username = user_dict['name']
            users_friends = get_friends(store, username)
            friended_user = get_followers(store, username)

            for friend in users_friends:
                user_dict['roles'].append('%s-is-friend' % friend)
            for friend in friended_user:
                user_dict['roles'].append('friend-of-%s' % friend)

            return user_dict
        return results
