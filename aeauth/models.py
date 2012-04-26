# -*- coding: utf-8 -*-
"""
    aeauth.models
    ====================================

    Auth related models.

    :copyright: 2012 by Kyle Finley.
    :license: Apache Software License, see LICENSE for details.

"""
from __future__ import absolute_import
from google.appengine.ext import ndb
from aecore.models import Config
from aecore.models import UserProfile


__author__ = 'kyle.finley@gmail.com (Kyle Finley)'


class ProviderUserProfile(UserProfile):

    provider = None
    provider_url = None

    credentials = ndb.PickleProperty(indexed=False)

    @property
    def config(self):
        key = 'aeauth.strategies.{}'.format(self.provider)
        return Config.get(key)

    @staticmethod
    def get_callback_url(domain, provider):
        base_url = Config.get('aeauth').base_url
        return u'{0}{1}/{2}/callback'.format(domain, base_url, provider)

    @staticmethod
    def get_session_key(provider):
        return '_eauth_user_profile:{0}'.format(provider)

    def get_profile_uid(self, **kwargs):
        raise NotImplementedError()

    def set_key(self):
        self._key = self.get_key(self.provider, self.get_profile_uid())

    def set_person_raw(self, **kwargs):
        raise NotImplementedError()

    def set_person(self, **kwargs):
        raise NotImplementedError()

    @classmethod
    def handle_request(cls, request):
        raise NotImplementedError()

#    def _pre_put_hook(self):
#        self.options = self.Options.__dict__
