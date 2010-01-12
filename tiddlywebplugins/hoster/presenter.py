"""
A replacement for the HTMLPresenter that allows
the use of templating.
"""

from tiddlyweb.web.wsgi import HTMLPresenter
from tiddlywebplugins.hoster.template import send_template

class PrettyPresenter(HTMLPresenter):

    def __call__(self, environ, start_response):
        output = self.application(environ, start_response)
        if self._needs_title(environ):
            if isinstance(output, basestring):
                output = [output]
            data = {
                    'output': output,
                    'title': environ['tiddlyweb.title'],
                    }
            return send_template(environ, 'pretty.html', data)
        return output
