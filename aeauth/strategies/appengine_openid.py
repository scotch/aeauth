from __future__ import absolute_import
from google.appengine.api import users
from aeauth.models import ProviderUserProfile
from aecore import types

__author__ = 'kyle.finley@gmail.com (Kyle Finley)'


class AppEngineOpenIDUserProfile(ProviderUserProfile):

    provider = 'appengine_openid'

    def get_profile_uid(self):
        user = users.get_current_user()
        if user.federated_identity():
            return user.federated_identity()
        else:
            return user.user_id()

    def set_person(self):
        user = users.get_current_user()
        person = types.Person()

        person.email                = user.email()
        person.id                   = user.user_id()
        person.url                  = user.federated_identity()
        person.username             = user.nickname()

        ### Accounts ###
        # You are required to create an account object for the providers
        # account. You may optionally add additional account, too.
        account                     = types.Account()
        account.name                = user.federated_provider()
        account.url                 = user.federated_identity()
        account.userid              = user.user_id()
        account.username            = user.nickname()
        person.accounts             = [account]

        return person

    @classmethod
    def handle_request(cls, request):
        user = users.get_current_user()
        if user is None:
            callback_url = cls.get_callback_url(
                domain=request.host_url, provider=cls.provider)
            provider_uri = request.GET['provider']
            redirect_url =  users.create_login_url(
                dest_url=callback_url, federated_identity=provider_uri)
            profile = None
        else:
            profile = cls()
            profile.person = profile.set_person()
            profile.set_key()
            redirect_url = None
        return redirect_url, profile