# -*- coding: utf-8 -*-
import os

try:
  from lxml import etree as ET
except ImportError:
    # fallback to the default ElementTree module
    import xml.etree.ElementTree as ET

import prof

try:
    from omemo.state import OmemoState
except ImportError:
    prof.log_error(u'Could not initiate python-omemo')
    raise

""" Plugin to allow to encrypt/decrypt messages using axolotl

Workflow:

- Init
    Create Keypair if not existent
    Create sqlite db if necessary
    Announce own device to support OMEMO

- Receive Messages
    - Get devicelist updates and cache them
    - If a device receives an update  -> check if own device is still announced.
      If not re-announce

    Furthermore, a device MUST announce it’s IdentityKey, a signed PreKey,
    and a list of PreKeys in a separate, per-device PEP node.
    The list SHOULD contain 100 PreKeys, but MUST contain no less than 20.

- Build a Session
    - fetch their bundle

- Sending a Message
    In order to send a chat message, its <body> first has to be encrypted.
    The client MUST use fresh, randomly generated key/IV pairs with AES-128 in
    Galois/Counter Mode (GCM). For each intended recipient device, i.e. both
    own devices as well as devices associated with the contact, this key is
    encrypted using the corresponding long-standing axolotl session.
    Each encrypted payload key is tagged with the recipient device’s ID.
    This is all serialized into a MessageElement,
    which is transmitted in a <message> as follows:


- Sending a key
    The client may wish to transmit keying material to the contact. This
    first has to be generated. The client MUST generate a fresh, randomly
    generated key/IV pair. For each intended recipient device, i.e. both own
    devices as well as devices associated with the contact, this key is
    encrypted using the corresponding long-standing axolotl session.
    Each encrypted payload key is tagged with the recipient device’s ID.
    This is all serialized into a KeyTransportElement,
    omitting the <payload> as follows:

"""
HOME = os.path.expanduser("~")
XDG_DATA_HOME = os.environ.get("XDG_DATA_HOME",
                               os.path.join(HOME, ".local", "share"))

__OMEMO_SESSIONS = {}
__REQ_INCR = {}

################################################################################
# Convenience methods
################################################################################


def _get_local_data_path():
    # TODO: get current username
    current_user = u'sqlitedb@local'
    safe_username = current_user.replace(u'@', u'_at_')

    return os.path.join(XDG_DATA_HOME, u'profanity', u'omemo', safe_username)


def _get_db_path():
    return os.path.join(_get_local_data_path(), u'omemo.db')


def _get_request_increment(req_type):
    global __REQ_INCR
    last_req_id = __REQ_INCR.get(req_type)
    if last_req_id:
        # increment the last request id
        req_id = last_req_id + 1
    else:
        # we need to set an initial request id
        req_id = 1

    __REQ_INCR[req_type] = req_id

    return u'{0}{1}'.format(req_type, req_id)

################################################################################
# Stanza handling
################################################################################


def _create_fetch_bundle_request(sender, recipient, device_id):
    bundle_req_root = ET.Element('iq')
    bundle_req_root.set('from', sender)
    bundle_req_root.set('to', recipient)
    bundle_req_root.set('id', _get_request_increment('fetch'))
    pubsub_node = ET.SubElement(bundle_req_root, 'pubsub')
    pubsub_node.set('xmlns', 'http://jabber.org/protocol/pubsub')
    items_node = ET.SubElement(pubsub_node, 'items')
    items_node.set('node', 'urn:xmpp:omemo:0:bundles:{}'.format(device_id))

    return ET.tostring(bundle_req_root, encoding='utf8', method='xml')


def _stanza__get_root_attributes(stanza):
    xml = ET.fromstring(stanza)
    xml_root = xml.getroot()

    return xml_root.attrib

################################################################################
# Sending hooks
################################################################################


def prof_on_message_stanza_send(stanza):
    pass


def prof_on_presence_stanza_send(stanza):
    pass


def prof_on_iq_stanza_send(stanza):
    pass

################################################################################
# Receiving hooks
################################################################################


def prof_on_message_stanza_receive(stanza):
    # prof_incoming_message() and return FALSE
    return True


def prof_on_presence_stanza_receive(stanza):
    # prof_incoming_message() and return FALSE
    return True


def prof_on_iq_stanza_receive(stanza):
    # prof_incoming_message() and return FALSE
    return True

################################################################################
# Plugin Entry Point
################################################################################


def _parse_args(*args):
    """ Parse arguments given in command window

    arg1: start || end
    arg2: muc || jid (optional)

    Starts or ends an encrypted chat session

    """
    pass

################################################################################
# Plugin init
################################################################################


def prof_init(version, status):

    synopsis = [
        "/omemo",
        "/omemo start|end [jid]"
    ]

    description = "Plugin to enable OMEMO encryption"
    args = [
        [ "start|end <jid>", "Start an OMEMO based conversation with <jid> window or current window." ]
    ]
    examples = []

    # ensure the plugin is not registered if python-omemo is not available
    prof.register_command("/omemo", 1, 2, synopsis, description, args, examples, _parse_args)
    prof.register_ac("/omemo", [ "start", "end"])
