# -*- coding: utf-8 -*-
"""
    aeauth.strategies.oauth2
    ====================================

    Auth related models.

    :copyright: 2012 by Kyle Finley.
    :license: Apache Software License, see LICENSE for details.

"""
from __future__ import absolute_import
import json
from apiclient.discovery import build
from google.appengine.ext import ndb
from google.appengine.api import memcache
from aeauth.models import ProviderUserProfile
import httplib2
from oauth2client.client import OAuth2WebServerFlow
import cPickle as pickle


__author__ = 'kyle.finley@gmail.com (Kyle Finley)'


class OAuth2UserProfile(ProviderUserProfile):
    authorize_url = None
    token_url = None

    # this is Python specific, but that's ok because it's short lived.
    flow = ndb.PickleProperty()

    def http(self):
        if self.credentials is not None and not self.credentials.invalid:
            return self.credentials.authorize(httplib2.Http())
        return None

    def service(self, **kwargs):
        name = kwargs.get('name', 'plus')
        version = kwargs.get('version', 'v1')
        return build(name, version, http=httplib2.Http(memcache))

    def _get_url(self, url):
        res, results = self.http().request(url)
        if res.status is not 200:
            raise Exception(message=u'There was an error contacting the '\
                                      u'provider. Please try again.')
        return json.loads(results)

    get_url = _get_url

    def _handle_start(self, request):
        try:
            scope = self.config.scope
        except AttributeError:
            scope = ''
        self.flow = OAuth2WebServerFlow(
            client_id=self.config.client_id,
            client_secret=self.config.client_secret,
            scope=scope,
            auth_uri=self.authorize_url,
            token_uri=self.token_url,
        )
        # Store the request URI in 'state' so we can use it later
        self.flow.params['state'] = request.path_url
        callback_url = self.get_callback_url(
            request.host_url, self.provider)
        authorize_url = self.flow.step1_get_authorize_url(callback_url)
        return authorize_url

    def _handle_callback(self, request):
        if self.flow is None:
            raise Exception(message=u'And Error has occurred. '\
                                      u'Please try again.')
        try:
            self.credentials = self.flow.step2_exchange(request.params)
        except Exception, e:
            raise Exception(message=u'And Error has occurred. '\
                                      u'Please try again.')
        self.set_person_raw()
        self.set_person()
        self.set_key()
        # remove flow
        del self.flow
        return None

    @classmethod
    def handle_request(cls, request):
        # First check the session for an existing user_profile
        session_key = cls.get_session_key(cls.provider)
        existing_profile = request.session.data.get(session_key)
        if not existing_profile:
            # create a new profile
            obj = cls()
            redirect_url = obj._handle_start(request)
            request.session.data[session_key] = pickle.dumps(obj)
            profile = None
        else:
            try:
                obj = pickle.loads(existing_profile)
                redirect_url = obj._handle_callback(request)
                obj.put()
                profile = obj
            except Exception, e:
                raise Exception(
                    message=u'There was an error contacting the provider. '\
                            u'Please try again.')
            finally:
                request.session.data.pop(session_key)

        return redirect_url, profile