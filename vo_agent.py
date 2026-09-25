import json
import asyncio
import aiohttp

from config_loader import load_agent_config


VOICE = "dasha"
MODEL_NAME = "speech-realtime-260528"

API_ENDPOINT = "wss://ai.api.cloud.yandex.net/v1/realtime/openai"

IN_RATE = 44100
OUT_RATE = 44100
SILENCE_THRESHOLD_MS = 500


class RealTimeAgent:

    def __init__(self, api_key, folder_id):
        self.api_key = api_key
        self.folder_id = folder_id

        self.config = load_agent_config()
        self.voice_config = self.config.get("voice", {})

        self.running = True
        self.ws = None
        self.session = None

        self.realtime_api_url = (
            f"{API_ENDPOINT}"
            f"?model=gpt://{self.folder_id}/{MODEL_NAME}"
        )

        self.authorization_header = {
            "Authorization": f"Api-Key {self.api_key}"
        }

    async def initialize_yandex_connection(self):
        print(f"Connecting to Yandex Realtime API, folder={self.folder_id}")

        self.session = aiohttp.ClientSession()

        self.ws = await self.session.ws_connect(
            self.realtime_api_url,
            headers=self.authorization_header,
            heartbeat=20.0
        )

        print("✅ Connected to Yandex Realtime API")

        await self.ws.send_json({
            "type": "session.update",
            "session": {
                "type": "realtime",

                "instructions": self.voice_config.get(
                    "system_prompt",
                    "Ты полезный голосовой AI-ассистент."
                ),

                "output_modalities": [
                    "audio"
                ],

                "audio": {
                    "input": {
                        "format": {
                            "type": "audio/pcm",
                            "rate": IN_RATE
                        },

                        "languages": [
                            "ru-RU"
                        ],

                        "turn_detection": {
                            "type": "server_vad",
                            "threshold": 0.5,
                            "silence_duration_ms": SILENCE_THRESHOLD_MS
                        }
                    },

                    "output": {
                        "format": {
                            "type": "audio/pcm",
                            "rate": OUT_RATE
                        },

                        "voice": self.voice_config.get("voice", "dasha")
                    }
                }
            }
        })

        print("✅ Realtime session.update sent")

    async def send_audio_to_yandex(self, base64_audio_data):

        if (
            not self.running
            or self.ws is None
            or self.ws.closed
        ):
            return

        await self.ws.send_json({
            "type": "input_audio_buffer.append",
            "audio": base64_audio_data
        })

    async def handle_yandex_messages(self, client_ws):

        if self.ws is None:
            print("❌ Yandex WebSocket not initialized")
            return

        async for msg in self.ws:

            if msg.type == aiohttp.WSMsgType.ERROR:
                print("❌ Yandex WebSocket error:", self.ws.exception())
                break

            if msg.type != aiohttp.WSMsgType.TEXT:
                continue

            try:
                message = json.loads(msg.data)
            except Exception:
                print("Unknown message:", msg.data)
                continue

            msg_type = message.get("type")

            print("YANDEX EVENT:", msg_type)

            if msg_type == "session.created":
                session_id = (message.get("session") or {}).get("id")
                print("🪪 Session:", session_id)
                continue

            if msg_type == "session.updated":
                print("✅ Realtime session configured")
                continue

            if msg_type == "conversation.item.input_audio_transcription.completed":
                transcript = message.get("transcript", "")

                print("USER:", transcript)

                try:
                    await client_ws.send_json({
                        "type": "transcript",
                        "text": transcript
                    })
                except Exception:
                    pass

                continue

            if msg_type == "input_audio_buffer.speech_started":

                print("🎤 Speech started")

                try:
                    await client_ws.send_json({
                        "type": "user_speech_started"
                    })
                except Exception:
                    pass

                continue

            if msg_type == "response.created":
                print("🤖 Response started")
                continue

            if msg_type == "response.output_audio.delta":

                audio_base64 = message.get("delta")

                if audio_base64:
                    try:
                        await client_ws.send_json({
                            "type": "audio",
                            "data": audio_base64
                        })
                    except Exception as e:
                        print("Browser audio send error:", e)

                continue

            if msg_type == "response.output_text.delta":

                text = message.get("delta", "")

                if text:
                    print("BOT:", text, end="", flush=True)

                continue

            if msg_type == "response.done":
                print("\n✅ Response completed")
                continue

            if msg_type == "error":
                print(
                    "❌ YANDEX REALTIME ERROR:",
                    json.dumps(
                        message,
                        ensure_ascii=False,
                        indent=2
                    )
                )
                continue

        print("Yandex Realtime WebSocket closed")

    async def stop(self):
        self.running = False

        if self.ws is not None and not self.ws.closed:
            await self.ws.close()

        if self.session is not None:
            await self.session.close()

        self.ws = None
        self.session = None

    def is_connected(self):
        return self.ws is not None and not self.ws.closed

    async def reconnect(self):
        await self.stop()

        self.running = True

        await self.initialize_yandex_connection()

    def set_running(self, state: bool):
        self.running = state

    def get_status(self):
        return {
            "running": self.running,
            "connected": self.is_connected(),
            "folder_id": self.folder_id
        }
