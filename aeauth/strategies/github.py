from __future__ import absolute_import

from aeauth.strategies.oauth2 import OAuth2UserProfile
from aecore import types
import json

class GithubUserProfile(OAuth2UserProfile):

    provider = 'github'
    provider_url = 'github.com'
    authorize_url = 'https://github.com/login/oauth/authorize'
    token_url = 'https://github.com/login/oauth/access_token'

    def get_url(self, url):
        """
        Override to append ?access_token={token}
        :param url:
            String representing the url to fetch
        :return:
            Response from provider.
        """
        url = "{}?access_token={}".format(url, self.credentials.access_token)
        return self._get_url(url)

    def get_profile_uid(self):
        return self.person_raw.get('id')

    def set_person_raw(self):
        self.person_raw = self.get_url('https://api.github.com/user')

    def set_person(self):
        person = types.Person()
        raw = self.person_raw

        if not raw:
            raise AttributeError(message=u'person_raw not populated.')

        ## Required ##
        person.provider             = self.provider # u'facebook'
        person.id                   = str(raw.get('id')) # u'12345'
        person.name                 = raw.get('name') # u'Mr. Joseph Robert Smarr, Esq'

        ### Accounts ###
        # You are required to create an account object for the providers
        # account. You may optionally add additional account, too.
        account                     = types.Account()
        account.name                = u'github' # u'facebook'
        account.url                 = u'github.com' # u'facebook.com'
        account.userid              = str(raw.get('id')) # u'123456789'
        account.username            = raw.get('username') # u'scotchmedia'
        person.accounts             = [account]

        ## Optional ##

        ### Singular Fields ###
        person.email                = raw.get('email')
        person.url                  = raw.get('html_url') # u'http://facebook.com/username'
        person.description          = raw.get('bio') # u'Longer description'
        person.image                = raw.get('avatar_url') # u'http://awesome.jpg.to/'
        person.location             = raw.get('location') # etype.Location(name=u'Springfield, VT')

        ## List Fields ##

        ### Affiliation ###

        ### URLs ###
        url                         = types.URL()
        url.description             = u'blog' # u'work'
        url.url                     = raw.get('blog') # u'http://www.scotchmedia.com'
        url.primary                 = True # True
        person.urls                 = [url]

        self.person = person
