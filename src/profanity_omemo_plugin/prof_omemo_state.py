# -*- coding: utf-8 -*-
#
# Copyright 2017 René `reneVolution` Calles <info@renevolution.com>
#
# This file is part of Profanity OMEMO plugin.
#
# The Profanity OMEMO plugin is free software: you can redistribute it and/or
# modify it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# The Profanity OMEMO plugin is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY
# or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License for
# more details.
#
# You should have received a copy of the GNU General Public License along with
# the Profanity OMEMO plugin.  If not, see <http://www.gnu.org/licenses/>.
#
from __future__ import absolute_import
from __future__ import unicode_literals

import prof

from profanity_omemo_plugin.db import get_connection
from profanity_omemo_plugin.log import get_plugin_logger

logger = get_plugin_logger(__name__)

from profanity_omemo_plugin.omemo.state import OmemoState

# Monkeypatching trusted state until it has been implemented correctly
def _isTrusted(self, recipient_id, device_id):
    return True

OmemoState.isTrusted = _isTrusted


class DummyPLugin(object):
    def publish_bundle(self, account):
        pass


class ProfOmemoState(object):
    """ ProfOmemoState Singleton """

    __states = {}

    def __new__(cls, *args, **kwargs):
        account = ProfOmemoUser().account
        if ProfOmemoUser().fulljid:
            own_jid = ProfOmemoUser().fulljid.rsplit('/', 1)[0]
        else:
            own_jid = account

        if not own_jid:
            raise RuntimeError('No User connected.')

        if own_jid not in cls.__states:
            # create the OmemoState for the current user
            connection = get_connection(own_jid)
            new_state = OmemoState(own_jid, connection, account, DummyPLugin())
            cls.__states[own_jid] = new_state

        return cls.__states[own_jid]


class ProfActiveOmemoChats(object):

    _active = {}

    @classmethod
    def add(cls, contact_jid):
        raw_jid = cls.as_raw_jid(contact_jid)
        if raw_jid not in cls._active:
            cls._active[raw_jid] = {'deactivated': False}
            prof.log_info('Added {0} to active chats'.format(raw_jid))
        else:
            cls.activate(raw_jid)
            prof.log_info('Chat with {0} re-activated.')

    @classmethod
    def activate(cls, contact_jid):
        raw_jid = cls.as_raw_jid(contact_jid)
        cls._active[raw_jid] = {'deactivated': False}

    @classmethod
    def deactivate(cls, contact_jid):
        raw_jid = cls.as_raw_jid(contact_jid)
        user = cls._active.get(raw_jid)

        try:
            user['deactivated'] = True
        except KeyError:
            pass

    @classmethod
    def remove(cls, contact_jid):
        raw_jid = cls.as_raw_jid(contact_jid)
        try:
            del cls._active[raw_jid]
        except KeyError:
            pass

    @classmethod
    def account_is_registered(cls, contact_jid):
        raw_jid = cls.as_raw_jid(contact_jid)
        prof.log_info('Active Chats: [{0}]'.format(', '.join(cls._active)))
        active_user = cls._active.get(raw_jid)

        return active_user is not None

    @classmethod
    def account_is_active(cls, contact_jid):
        raw_jid = cls.as_raw_jid(contact_jid)
        prof.log_info('Active Chats: [{0}]'.format(', '.join(cls._active)))
        active_user = cls._active.get(raw_jid)
        if not active_user:
            return False

        return not active_user['deactivated']

    @classmethod
    def account_is_deactivated(cls, contact_jid):
        raw_jid = cls.as_raw_jid(contact_jid)
        active_user = cls._active.get(raw_jid)

        # if the user does not have an active session yet,
        # the user can't be deactivated
        if not active_user:
            return False

        return active_user['deactivated']

    @classmethod
    def reset(cls):
        cls._active = {}

    @staticmethod
    def as_raw_jid(contact_jid):
        raw_jid = None
        if contact_jid:
            raw_jid = contact_jid.rsplit('/', 1)[0]

        return raw_jid


class ProfOmemoUser(object):
    """ ProfOmemoUser Singleton """

    account = None
    fulljid = None

    @classmethod
    def set_user(cls, account, fulljid):
        cls.account = account
        cls.fulljid = fulljid

    @classmethod
    def reset(cls):
        cls.account = None
        cls.fulljid = None
