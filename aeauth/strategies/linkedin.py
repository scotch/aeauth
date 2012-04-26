from __future__ import absolute_import
import json
from aeauth.strategies.oauth import OAuthUserProfile
from aecore import types


class LinkedInUserProfile(OAuthUserProfile):

    provider = 'linkedin'
    provider_url = 'linkedin.com'
    request_token_url = 'https://api.linkedin.com/uas/oauth/requestToken'
    access_token_url = 'https://api.linkedin.com/uas/oauth/accessToken'
    authorize_url = 'https://www.linkedin.com/uas/oauth/authenticate'

    def get_profile_uid(self):
        return self.person_raw.get('id')

    def set_person_raw(self):
        url = "http://api.linkedin.com/v1/people/~:({0})?format=json".format(
            self.config.fields)
        self.person_raw = self.get_url(url)

    def set_person(self):

        person = types.Person()
        raw = self.person_raw

        if not raw:
            raise AttributeError(message=u'person_raw not populated.')
        ## Required ##
        person.provider             = self.provider # u'facebook'
        person.id                   = raw.get('id') # u'12345'
        person.name                 = "{0} {1}".format(raw.get('firstName'), raw.get('lastName'))


        ### Accounts ###
        # You are required to create an account object for the providers
        # account. You may optionally add additional account, too.
        account                     = types.Account()
        account.name                = u'linkedin' # u'facebook'
        account.url                 = u'linkedin.com' # u'facebook.com'
        account.userid              = raw.get('id') # u'123456789'
        person.accounts             = [account]

        ## Optional ##

        ### Name Details ###
        person.givenName            = raw.get('firstName') # u'Joseph'
        person.familyName           = raw.get('lastName') # u'Smarr'

        ### Singular Fields ###
        person.url                  = raw.get('publicProfileUrl') # u'http://facebook.com/username'
        person.birthDate            = raw.get('dateOfBirth') # datetime.datetime(1969, 7, 20, 1, 12, 3, 723097)
        person.description          = raw.get('headline') # u'Longer description'
        person.image                = raw.get('pictureUrl') # u'http://awesome.jpg.to/'
#        person.gender               = raw.get('gender') # u'male'
#        person.location             = raw.get('currentLocation') # etype.Location(name=u'Springfield, VT')
#        person.relationshipStatus   = raw.get('relationshipStatus') # u'single'
#        person.locale               = raw.get('locale')
#
#        # TODO add placesLived
#
#        ## List Fields ##
#
#        ### Affiliation ###
#        if raw.get('organizations'):
#            for org in raw.get('organizations'):
#                organization                = types.Organization()
#                organization.name           = org.get('name') # u'FHSU'
#                organization.description    = org.get('description')  # u'tiger'
#                affiliation                 = types.Affiliation()
#                affiliation.name            = org.get('title') # u'BFA'
#                affiliation.department      = org.get('department') # u'Graphic Design'
#                affiliation.description     = org.get('description') # u'BFA Emphasis in Graphic Design'
#                affiliation.startDate       = datetime.datetime.strptime(org.get('startDate'), "%Y-%m-%dT%H:%M:%S") # datetime.datetime(2010, 1, 14, 10, 12, 3, 723097)
#                affiliation.endDate         = datetime.datetime.strptime(org.get('endDate'), "%Y-%m-%dT%H:%M:%S") # datetime.datetime(2012, 1, 14, 10, 12, 3, 723097)
#                affiliation.location        = types.Place(name=org.get('location')) # types.Place(name=u'Kansas USA')
#                # This next may not be necessary in the future
#                if org.get('type') == 'school':
#                    affiliation.itemtype      = u'EducationalOrganization' # u'EducationalOrganization'
#                person.affiliations.append(affiliation)
#
#        ### languages Spoken ###
#        if raw.get('languagesSpoken'):
#            person.languagesSpoken = [types.Language(name=o)
#                                      for o in raw.get('languagesSpoken')]
#
#        ### URLs ###
#        if raw.get('urls'):
#            person.urls = [types.URL(url=o.get('value'),
#                description=o.get('type')) for o in raw.get('urls')]
#
#        ### Emails ###
#        if raw.get('emails'):
#            person.emails = [types.Email(address=o.get('value'),
#                description=o.get('type')) for o in raw.get('emails')]
#
#        if person.emails:
#            person.email = person.emails[0].address # u'test@example.com'
#
        self.person = person
