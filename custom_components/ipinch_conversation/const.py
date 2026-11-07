"""Constants for the iPinch Conversation integration."""

import logging
import re

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

# A short "thanks, that's all" from the person ends the conversation, whatever the reply says:
# the bridge only marks the end when iPinch herself says goodbye.
_CLOSER = (
    r"(?:thank(?:s|\s?you)(?:\s(?:so|very)\s?much)?|ta|cheers|many thanks"
    r"|that'?s (?:all|it|everything|great|perfect)|nothing(?: else)?|no(?:,)? (?:thanks|thank you|that'?s (?:all|it))"
    r"|(?:good)?bye|bye[\s-]?bye|good ?night|night(?:[\s-]night)?|see (?:you|ya)(?: later)?|later)"
)
CLOSING = re.compile(
    r"^(?:(?:ok(?:ay)?|great|perfect|lovely|cool|nice|brilliant|awesome|amazing|super|right|and)[\s,.!]+)*"
    + _CLOSER
    + r"(?:[\s,.!]+(?:" + _CLOSER + r"|pinchy|ipinch|i pinch|crab|buddy|mate|again|a lot))*[\s,.!]*$",
    re.IGNORECASE,
)


def is_closing(text: str) -> bool:
    """Whether the person is wrapping up rather than asking something."""
    return bool(CLOSING.match(text.strip()))
