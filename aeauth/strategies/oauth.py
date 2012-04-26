# -*- coding: utf-8 -*-
"""
    aeauth.models.base
    ====================================

    Auth related models.

    :copyright: 2012 by Kyle Finley.
    :license: Apache Software License, see LICENSE for details.

"""
from __future__ import absolute_import
from apiclient.oauth import FlowThreeLegged
from aeauth.models import ProviderUserProfile
from google.appengine.ext import ndb
import httplib2
import cPickle as pickle
import json

__author__ = 'kyle.finley@gmail.com (Kyle Finley)'


class OAuthUserProfile(ProviderUserProfile):

    request_token_url = None
    access_token_url = None
    authorize_url = None

    # this is Python specific, but that's ok because it's short lived.
    flow = ndb.PickleProperty()

    def http(self):
        if not self.credentials.invalid:
            return self.credentials.authorize(httplib2.Http())
        return None

    def service(self, **kwargs):
        raise NotImplementedError()

    def get_url(self, url):
        res, results = self.http().request(url)
        if res.status is not 200:
            raise Exception(message=u'There was an error contacting the '\
                                          u'provider. Please try again.')
        return json.loads(results)

    def _handle_start(self, request):
        discovery = {
            'request': {
                'url': self.request_token_url,
                'parameters': {
                    },
                },
            'authorize': {
                'url': self.authorize_url,
                'parameters': {
                    'oauth_token': {
                        'required': True,
                        },
                    },
                },
            'access': {
                'url': self.access_token_url,
                'parameters': {
                    },
                },
            }
        self.flow = FlowThreeLegged(
            discovery=discovery,
            consumer_key=self.config.client_id,
            consumer_secret=self.config.client_secret,
            user_agent='aeauth'
        )
        callback_url = self.get_callback_url(
            request.host_url, self.provider)
        authorize_url = self.flow.step1_get_authorize_url(
            oauth_callback=callback_url)
        return authorize_url

    def _handle_callback(self, request):
        if self.flow is None:
            raise Exception(message=u'And Error has occurred. '\
                                          u'Please try again.')
        try:
            self.credentials = self.flow.step2_exchange(request.params)
        except Exception, e:
            import logging
            logging.error(e)
            raise Exception(message=u'And Error has occurred. '\
                                          u'Please try again.')
        self.set_person_raw()
        try:
            self.set_person()
            self.set_key()
        except Exception, e:
            import logging
            logging.error(e)
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
