import webapp2
import os

routes = [
    webapp2.Route(r'/auth/login', handler='aeauth.handlers.AEAuthHandler:login', name='auth-login'),
    webapp2.Route(r'/auth/logout', handler='aeauth.handlers.AEAuthHandler:logout', name='auth-logout'),

    # Password handlers
    webapp2.Route(r'/auth/password', handler='aeauth.handlers.PasswordHandler', name='auth-password'),

    # All other providers
    webapp2.Route(r'/auth/<provider>', handler='aeauth.handlers.AEAuthHandler:start', name='auth-start'),
    webapp2.Route(r'/auth/<provider>/<params>', handler='aeauth.handlers.AEAuthHandler:callback', name='auth-start'),
    webapp2.Route(r'/auth/<provider>/<params>', handler='aeauth.handlers.AEAuthHandler:callback', name='auth-start'),
    ]

template_path = os.path.join(os.path.dirname(__file__), 'templates')

config = {
    'webapp2_extras.jinja2': {
        'template_path': ['templates', template_path],
        },
    }


application = webapp2.WSGIApplication(routes, config=config)
