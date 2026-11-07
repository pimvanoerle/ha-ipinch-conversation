"""Constants for the iPinch Conversation integration."""

import logging

DOMAIN = "ipinch_conversation"
LOGGER = logging.getLogger(__package__)

CONF_URL = "url"
CONF_TOKEN = "token"
CONF_DEVICE = "device"

DEFAULT_DEVICE = "upstairs-show"
TOKEN_HEADER = "X-Pinch-Token"

# The endpoint answers within 7.5 s (it sends a spoken "ask me again" past that),
# so this only catches a bridge that has gone away.
TIMEOUT_S = 10
UNREACHABLE_REPLY = "Sorry, I can't reach iPinch right now."
