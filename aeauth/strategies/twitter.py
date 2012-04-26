from __future__ import absolute_import

from aeauth.strategies.oauth import OAuthUserProfile
from aecore import types


class TwitterUserProfile(OAuthUserProfile):

    provider = 'twitter'
    provider_url = 'twitter.com'
    request_token_url = 'https://api.twitter.com/oauth/request_token'
    access_token_url = 'https://api.twitter.com/oauth/access_token'
    authorize_url = 'https://api.twitter.com/oauth/authorize'

    def get_profile_uid(self):
        return self.person_raw.get('id')

    def set_person_raw(self):
        self.person_raw = self.get_url(
            'https://api.twitter.com/1/account/verify_credentials.json')

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
        account.name                = u'twitter' # u'facebook'
        account.url                 = u'twitter.com' # u'facebook.com'
        account.userid              = str(raw.get('id')) # u'123456789'
        account.username            = raw.get('screen_name') # u'scotchmedia'
        person.accounts             = [account]

        ## Optional ##

        ### Singular Fields ###
        person.url                  = u'https://twitter.com/{}'.format(raw.get('user_anme')) # u'http://facebook.com/username'
        person.description          = raw.get('description') # u'Longer description'
        person.image                = raw.get('profile_image_url') # u'http://awesome.jpg.to/'
        if raw.get('location'):
            person.location             = types.Place(name=raw.get('location'))
        person.locale               = raw.get('lang')
        person.utcOffset            = str(raw.get('utc_offset')) # u'-06:00'
        person.verified             = raw.get('verified') # True

        ## List Fields ##

        ### Affiliation ###

        ### URLs ###
        url                         = types.URL()
        url.description             = u'website' # u'work'
        url.url                     = raw.get('website') # u'http://www.scotchmedia.com'
        url.primary                 = True # True
        person.urls                 = [url]

        self.person = person
