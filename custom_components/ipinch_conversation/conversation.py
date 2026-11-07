"""The conversation agent: each turn goes to the bridge, and its reply is spoken."""

from typing import Literal

import aiohttp

from homeassistant.components import conversation
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import MATCH_ALL
from homeassistant.core import HomeAssistant
from homeassistant.helpers import intent
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.device_registry import DeviceEntryType, DeviceInfo
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from .const import (
    CONF_DEVICE,
    CONF_TOKEN,
    CONF_URL,
    DOMAIN,
    LOGGER,
    TIMEOUT_S,
    TOKEN_HEADER,
    UNREACHABLE_REPLY,
    is_closing,
)


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddConfigEntryEntitiesCallback
) -> None:
    async_add_entities([IPinchConversationEntity(entry)])


class IPinchConversationEntity(conversation.ConversationEntity):
    _attr_has_entity_name = True
    _attr_name = None

    def __init__(self, entry: ConfigEntry) -> None:
        self._entry = entry
        self._attr_unique_id = entry.entry_id
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry.entry_id)},
            name=entry.title,
            manufacturer="iPinch",
            entry_type=DeviceEntryType.SERVICE,
        )

    @property
    def supported_languages(self) -> list[str] | Literal["*"]:
        return MATCH_ALL

    async def _async_handle_message(
        self, user_input: conversation.ConversationInput, chat_log: conversation.ChatLog
    ) -> conversation.ConversationResult:
        data = self._entry.data
        reply, end = UNREACHABLE_REPLY, True
        try:
            async with async_get_clientsession(self.hass).post(
                data[CONF_URL],
                json={
                    "text": user_input.text,
                    "conversation_id": chat_log.conversation_id,
                    "device": data[CONF_DEVICE],
                },
                headers={TOKEN_HEADER: data[CONF_TOKEN]},
                timeout=aiohttp.ClientTimeout(total=TIMEOUT_S),
            ) as resp:
                resp.raise_for_status()
                body = await resp.json()
            reply = str(body.get("reply") or "")
            end = bool(body.get("end"))
        except (aiohttp.ClientError, TimeoutError, ValueError) as err:
            LOGGER.warning("iPinch didn't answer: %s", err)

        chat_log.async_add_assistant_content_without_tools(
            conversation.AssistantContent(agent_id=user_input.agent_id, content=reply)
        )
        response = intent.IntentResponse(language=user_input.language)
        response.async_set_speech(reply)
        # Keep listening for an answer, the way Clawlexa keeps its window open, unless
        # iPinch said goodbye or the person was wrapping up ("thanks pinchy").
        return conversation.ConversationResult(
            response=response,
            conversation_id=chat_log.conversation_id,
            continue_conversation=bool(reply) and not end and not is_closing(user_input.text),
        )
