from aecore import utils
from aecore.models import Config
from aecore.handlers import Jinja2Handler
from aecore.utils import flat_dict_to_nested_dict


class AEAuthHandler(Jinja2Handler):

    def login(self):
        providers = Config.get('aeauth').providers
        self.render_template('auth/login.html', {'providers': providers})

    def logout(self):
        c = Config.get('aecore')
        self.response.delete_cookie(
            c.cookie_key.encode('utf-8'),
            c.cookie_path.encode('utf-8'),
            c.cookie_domain)
        return self.redirect('/')

    def start(self, provider):
        self._handle_request(provider)

    def callback(self, provider, params):
        self._handle_request(provider, params)

    def _is_current_user_admin(self):
        from google.appengine.api import users
        return users.is_current_user_admin()

    def _handle_request(self, provider, params=None):
        provider_class = self._load_profile_class(provider)

        try:
            redirect_url, profile = provider_class.handle_request(self.request)
            if profile is not None:
                # if w have a logged in user add the auth_id.
                user = self.request.user
                if user is not None:
                    try:
                        user.add_auth_id(profile.key.id())
                        user.put()
                    except Exception, e:
                        # TODO if an exception is raised here's it's because the
                        # user has already create an account.
                        # Maybe we logout the user or migrate the old account.
                        pass
                # else get or create a user from the auth_id
                else:
                    user_model = self.request.get_user_model()
                    user = user_model.get_or_create_by_auth_id(profile.key.id())
                # if the user is not an owner of the profile add their ID
                if not profile.is_owner(user.key.id()):
                    profile.add_owner_id(user.key.id())
                    profile.put()
                # if the user is an admin and the role hasn't been added,
                # add the 'admin' role
                if self._is_current_user_admin() and not user.has_role('admin'):
                    user.add_roll('admin')
                    user.put()
                # TODO this should be deferred
                # Update the User's master profile with the information from
                # the newly created UserProfile.
                master_p = user.get_master_profile()
                master_p.merge_profile(profile.data)
                # TODO maybe this can be removed.
                # Currently this is necessary to update the session ID.
                if not self.request.user:
                    self.request.load_user(user.key.id())
        except Exception, e:
            redirect_url= Config.get('aeauth').login_url
            self.request.add_message(e.message, level='error')

        if redirect_url is None:
            redirect_url = self.request.get_redirect_url() or \
                           Config.get('aeauth').success_url
        self.redirect(redirect_url)

    def _load_profile_class(self, provider):
        try:
            pkey = 'aeauth.strategies.{}'.format(provider)
            profile_path = Config.get(pkey).user_profile_model
            profile_class = utils.import_class(profile_path)
        except AttributeError, e:
            raise AttributeError("You must provide the location of "\
                                 "the {0} user profile.".format(provider))
        return profile_class

class PasswordHandler(Jinja2Handler):

    def post(self):
        post_dict = flat_dict_to_nested_dict(self.request.POST)
        # confirm that required fields are provided.
        # We pop the password, because we don't want to send it to
        # ``get_person()``
        password = post_dict.pop('password')
        email = post_dict.get('email')

        if not email or not password or not utils.validate_email(email):
            message = u'Please provide a valid email and a password.'
            self.request.add_message(message, level='error')
            self.redirect(Config.get('aeauth').login_url)

        user = self.request.user
        # if we have a user update based on the dict and pass
        if user is not None:
            user.set_password(password)
#            user.add_email(email)
            user.put()
        # otherwise create a new one.
        else:
            user_model = self.request.get_user_model()
            user = user_model.get_or_create_by_email(email)
            # if we have a user check the password
            if user is not None:
                if not user.check_password(password):
                    message = u'The password that you\'ve provided ' \
                              u'does not match our records. ' \
                              u'Please try again.'
                    self.request.add_message(message, level='error')
                    self.redirect(Config.get('aeauth').login_url)
            # no User with that email create a new User
            else:
                user = user_model.create(email=email, password_raw=password)

        redirect_url = self.request.get_redirect_url() or\
                           Config.get('aeauth').success_url
        self.redirect(redirect_url)
