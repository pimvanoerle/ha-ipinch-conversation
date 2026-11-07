# iPinch Conversation

A small Home Assistant conversation agent that hands each voice turn to [iPinch](https://github.com/pimvanoerle/clawlexa)'s voice bridge over HTTP and speaks the reply. Use it as the conversation agent of an Assist pipeline, for example on a second wake word.

## The bridge's side

```
POST <turn URL>
X-Pinch-Token: <token>
{"text": "turn the lights down a bit", "conversation_id": "...", "device": "upstairs-show"}

200 {"reply": "Done, they're at 30 percent.", "conversation_id": "...", "end": false}
```

`conversation_id` stays the same for the turns of one conversation, so the bridge can keep its session warm. While `end` is false, Home Assistant keeps listening for an answer without the wake word. An empty `text` should get a 200 with an empty reply: setup uses that to check the URL and token.

## Install

1. HACS → Custom repositories → add this repository as an Integration, then download it and restart Home Assistant.
2. Settings → Devices & services → Add integration → iPinch Conversation. Enter the turn URL, the token and a device name.
3. Settings → Voice assistants → add an assistant with iPinch as its conversation agent.

The bridge should answer within about 8 seconds, since Assist gives up after that. If it can't be reached, the agent says so out loud instead of failing silently.
