from __future__ import absolute_import
import datetime
from aeauth.strategies.oauth2 import OAuth2UserProfile
from aecore import types


RELATIONSHIP_MAP = {
    'Single': 'single',
    'In a relationship': 'in_a_relationship',
    'Engaged': 'engaged',
    'Married': 'married',
    "It's complicated": 'its_complicated',
    'In an open relationship': 'open_relationship',
    'Widowed': 'widowed',
    'Separated': 'separated',
    'Divorced': 'divorced',
    'In a domestic partnership': 'in_domestic_partnership',
    'In a civil union': 'in_civil_union',
    }

class FacebookUserProfile(OAuth2UserProfile):

    provider = 'facebook'
    provider_url = 'facebook.com'
    authorize_url = 'https://graph.facebook.com/oauth/authorize'
    token_url = 'https://graph.facebook.com/oauth/access_token'

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
        self.person_raw = self.get_url('https://graph.facebook.com/me')

    def set_person(self):

        person = types.Person()
        raw = self.person_raw

        if not raw:
            raise AttributeError(message=u'person_raw not populated.')

        ## Required ##
        person.provider             = self.provider # u'facebook'
        person.id                   = raw.get('id') # u'12345'
        person.name                 = raw.get('name') # u'Mr. Joseph Robert Smarr, Esq'

        ### Accounts ###
        # You are required to create an account object for the providers
        # account. You may optionally add additional account, too.
        account                     = types.Account()
        account.name                = u'facebook' # u'facebook'
        account.url                 = u'facebook.com' # u'facebook.com'
        account.userid              = raw.get('id') # u'123456789'
        account.username            = raw.get('username') # u'scotchmedia'
        person.accounts             = [account]

        ## Optional ##

        ### Name Details ###
        person.givenName            = raw.get('first_name') # u'Joseph'
        person.additionalName       = raw.get('middle_name') # u'Robert'
        person.familyName           = raw.get('last_name') # u'Smarr'

        ### Singular Fields ###
        person.url                  = raw.get('link') # u'http://facebook.com/username'
        person.birthDate            = raw.get('birthday') # datetime.datetime(1969, 7, 20, 1, 12, 3, 723097)
        person.description          = raw.get('bio') # u'Longer description'
        # TODO set email from emails
        person.email                = None # u'test@example.com'
        person.image                = u'http://graph.facebook.com/{}/picture?type=square'.format(raw.get('id'))  # u'http://awesome.jpg.to/'
        person.gender               = raw.get('gender') # u'male'
        person.location             = raw.get('location') # etype.Location(name=u'Springfield, VT')
        person.relationshipStatus   = RELATIONSHIP_MAP.get(raw.get('relationship_status')) # u'single'
        person.locale               = raw.get('locale')
        person.utcOffset            = unicode(raw.get('timezone')) # u'-06:00'
        person.verified             = raw.get('verified') # True

        # TODO add placesLived

        ## List Fields ##

        ### Affiliation ###
        raw_work = raw.get('work')
        raw_edu = raw.get('education')
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

        affiliations = []
        if raw_work:
            for i in raw_work:
                #### Work ####
                work                = types.Organization()
                work.name           = i.get('employer') # u'Scotch Media, LLC.'
#                work.url            = None # u'http://www.scotchmedia.com'
#                work.description    = None # u'neat.'
                work.location       = types.Place(i.get('location')) # etype.Location(name=u'Kansas USA')
                org                 = types.Affiliation()
                org.name            = i.get('position') # u'CCO'
#                org.description     = None # u'Chief Creative Officer'
                org.organization    = work # types.Organization()
#                org.department      = None # u'Creative'
                org.startDate       = datetime.datetime.strptime(raw.get('start_date'), "%Y-%m-%dT%H:%M:%S") # datetime.datetime(2010, 1, 14, 10, 12, 3, 723097)
                org.endDate         = datetime.datetime.strptime(raw.get('end_date'), "%Y-%m-%dT%H:%M:%S") # datetime.datetime(2012, 1, 14, 10, 12, 3, 723097)
                org.location        = types.Place(i.get('location')) # etype.Location(name=u'Kansas USA')
                affiliations.append(org)
        if raw_edu:
            for i in raw_edu:
                #### School ####
                # TODO test and add additional fields here.
                school              = types.Organization()
#                school.address      = address
                school.name         = i.get('school').get('name') # u'FHSU'
#                school.url          = None # u'http://www.fhsu.edu'
                school.description  = i.get('school').get('type') # u'tiger'
#                school.location     = None # etype.Location(name=u'Hays, Kansas USA')
                org                 = types.Organization
#                org.name            = None # u'BFA'
#                org.department      = None # u'Graphic Design'
#                org.description     = None # u'Emphasis in conceptual design'
#                org.startDate       = None # datetime.datetime(2010, 1, 14, 10, 12, 3, 723097)
#                org.endDate         = None # datetime.datetime(2012, 1, 14, 10, 12, 3, 723097)
#                org.location        = None # etype.Location(name=u'Kansas USA')
                # This next may not be necessary in the future
                org.itemtype        = u'EducationalOrganization' # u'EducationalOrganization'
                affiliations.append(org)
        person.affiliations         = affiliations

        ### URLs ###
        url                         = types.URL()
        url.description             = u'website' # u'work'
        url.url                     = raw.get('website') # u'http://www.scotchmedia.com'
        url.primary                 = True # True
        person.urls                 = [url]
        
        ### Emails ###
#        if raw.get('emails'):
#            person.emails = [types.Email(address=o.get('value'),
#                description=o.get('type')) for o in raw.get('emails')]

        self.person = person
