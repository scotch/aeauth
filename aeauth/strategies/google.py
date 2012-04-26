from __future__ import absolute_import
import datetime
from aeauth.strategies.oauth2 import OAuth2UserProfile
from aecore import types


class GoogleUserProfile(OAuth2UserProfile):

    provider = 'google'
    provider_url = 'google.com'
    authorize_url = 'https://accounts.google.com/o/oauth2/auth'
    token_url = 'https://accounts.google.com/o/oauth2/token'

    def get_profile_uid(self, **kwargs):
        return self.person_raw.get('id')

    def set_person_raw(self):
        is_legacy = False
        res = {}
        try:
            res = self.service().people().get(userId='me').execute(self.http())
        except Exception, e:
            is_legacy = True

        # There's a bug where Google Plus doesn't return an email address.
        # So we'll retrieve it the old way and inject it into res.
        # We're also checking to se if this account is a legacy account,
        # in which case we'll perform the legacy user lookup.
        if is_legacy or 'emails' not in res:
            service = self.service(name='oauth2', version='v1')
            legacy_res = service.userinfo().get().execute(self.http())

            email = {
                'value': legacy_res.get('email'),
                'primary': True,
                'verified': legacy_res.get('verified_email')}
            res['emails'] = [email]

            if 'displayName' not in res:
                res['displayName'] = legacy_res.get('name')

            if 'name' not in res:
                res['name'] = {
                    'givenName': legacy_res.get('given_name'),
                    'familyName': legacy_res.get('family_name'),
                    }

            if 'url' not in res:
                res['url'] = legacy_res.get('link')

            if 'image' not in res:
                res['image'] = {'url': legacy_res.get('picture')}

            if 'locale' not in res:
                res['locale'] = legacy_res.get('locale')
        self.person_raw = res

    def set_person(self):

        person = types.Person()
        raw = self.person_raw

        if not raw:
            raise AttributeError(message=u'person_raw not populated.')
        ## Required ##
        person.provider             = self.provider # u'facebook'
        person.providerUrl          = self.provider_url # u'facebook.com'
        person.id                   = raw.get('id') # u'12345'
        person.name                 = raw.get('displayName') # u'Mr. Joseph Robert Smarr, Esq'

        ### Accounts ###
        # You are required to create an account object for the providers
        # account. You may optionally add additional account, too.
        account                     = types.Account()
        account.name                = u'google' # u'facebook'
        account.url                 = u'google.com' # u'facebook.com'
        account.userid              = raw.get('id') # u'123456789'
        person.accounts             = [account]

        ## Optional ##

        ### Name Details ###
        if raw.get('name'):
            person.givenName          = raw.get('name').get('givenName') # u'Joseph'
            person.additionalName     = raw.get('name').get('middleName') # u'Robert'
            person.familyName         = raw.get('name').get('familyName') # u'Smarr'
            person.honorificPrefix    = raw.get('name').get('honorificPrefix') # u'Mr.'
            person.honorificSuffix    = raw.get('name').get('honorificSuffix') # u'Esq.'

        ### Singular Fields ###
        person.url                  = raw.get('url') # u'http://facebook.com/username'
        person.birthDate            = raw.get('birthday') # datetime.datetime(1969, 7, 20, 1, 12, 3, 723097)
        person.description          = raw.get('aboutMe') # u'Longer description'
        if raw.get('image'):
            person.image                = raw.get('image').get('url') # u'http://awesome.jpg.to/'
        person.gender               = raw.get('gender') # u'male'
        person.location             = raw.get('currentLocation') # etype.Location(name=u'Springfield, VT')
        person.relationshipStatus   = raw.get('relationshipStatus') # u'single'
        person.locale               = raw.get('locale')

        # TODO add placesLived

        ## List Fields ##

        ### Affiliation ###
        if raw.get('organizations'):
            for org in raw.get('organizations'):
                organization                = types.Organization()
                organization.name           = org.get('name') # u'FHSU'
                organization.description    = org.get('description')  # u'tiger'
                affiliation                 = types.Affiliation()
                affiliation.name            = org.get('title') # u'BFA'
                affiliation.department      = org.get('department') # u'Graphic Design'
                affiliation.description     = org.get('description') # u'BFA Emphasis in Graphic Design'
                affiliation.startDate       = datetime.datetime.strptime(org.get('startDate'), "%Y-%m-%dT%H:%M:%S") # datetime.datetime(2010, 1, 14, 10, 12, 3, 723097)
                affiliation.endDate         = datetime.datetime.strptime(org.get('endDate'), "%Y-%m-%dT%H:%M:%S") # datetime.datetime(2012, 1, 14, 10, 12, 3, 723097)
                affiliation.location        = types.Place(name=org.get('location')) # types.Place(name=u'Kansas USA')
                # This next may not be necessary in the future
                if org.get('type') == 'school':
                    affiliation.itemtype      = u'EducationalOrganization' # u'EducationalOrganization'
                person.affiliations.append(affiliation)

        ### languages Spoken ###
        if raw.get('languagesSpoken'):
            person.languagesSpoken = [types.Language(name=o)
                                      for o in raw.get('languagesSpoken')]

        ### URLs ###
        if raw.get('urls'):
            person.urls = [types.URL(url=o.get('value'),
                description=o.get('type')) for o in raw.get('urls')]

        ### Emails ###
        if raw.get('emails'):
            person.emails = [types.Email(address=o.get('value'),
                description=o.get('type')) for o in raw.get('emails')]

        if person.emails:
            person.email = person.emails[0].address # u'test@example.com'

        self.person = person
        self.data = person.to_dict()

