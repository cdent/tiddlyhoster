"""
Send a template.
"""


from tiddlyweb import __version__ as VERSION
from tiddlywebplugins.templates import get_template
from tiddlywebplugins.hoster.data import get_user_object


def send_template(environ, template_name, template_data=None):
    if template_data == None:
        template_data = {}
    template = get_template(environ, template_name)
    server_prefix = environ['tiddlyweb.config']['server_prefix']
    user = get_user_object(environ)
    template_defaults = {
            #'message': 'test me you are a message',
            'version': VERSION,
            'user': user,
            'member_role': 'MEMBER',
            'title': '',
            'userpage': {
                'link': '%s/home' % server_prefix,
                'title': 'homepage',
                },
            'login': {
                'link': '%s/login' % server_prefix,
                'title': 'Login',
                },
            'help': {
                'link': '%s/help' % server_prefix,
                'title': 'Help',
                },
            'register': {
                'link': '%s/register' % server_prefix,
                'title': 'Register',
                },
            'server_prefix': server_prefix,
            'main_css': environ['tiddlyweb.config'].get(
                'hoster.main_css', 'main.css'),
            }
    template_defaults.update(template_data)
    return template.generate(template_defaults)
