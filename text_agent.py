import openai

from config_loader import load_agent_config


YANDEX_CLOUD_MODEL = "yandexgpt"
MAX_SESSIONS = 1000


class TextAgent:

    def __init__(self, api_key: str, base_url: str, project: str):
        self.previous_ids = {}

        self.client = openai.OpenAI(
            api_key=api_key,
            base_url=base_url,
            project=project
        )

        self.model = f"gpt://{project}/{YANDEX_CLOUD_MODEL}"

    def send(
        self,
        user_input: str,
        capability_id: str | None = None,
        session_id: str | None = None
    ) -> str:

        config = load_agent_config()
        text_config = config.get("text", {})

        instructions = text_config.get(
            "system_prompt",
            "Ты полезный AI-ассистент."
        )

        if capability_id:
            capability = next(
                (
                    item
                    for item in config.get("capabilities", [])
                    if (
                        item.get("id") == capability_id
                        and item.get("enabled", True)
                    )
                ),
                None
            )

            if capability:
                capability_instructions = capability.get(
                    "instructions",
                    ""
                ).strip()

                if capability_instructions:
                    instructions += (
                        "\n\n"
                        "АКТИВНАЯ БИЗНЕС-ФУНКЦИЯ:\n"
                        + capability_instructions
                    )

        tools = []

        if text_config.get("web_search", False):
            domains = text_config.get(
                "allowed_domains",
                []
            )

            web_search_tool = {
                "type": "web_search"
            }

            if domains:
                web_search_tool["filters"] = {
                    "allowed_domains": domains
                }

            tools.append(web_search_tool)

        params = {
            "model": self.model,
            "instructions": instructions,
            "input": [
                {
                    "role": "user",
                    "content": user_input
                }
            ]
        }

        if tools:
            params["tools"] = tools

        if session_id:
            previous_id = self.previous_ids.get(session_id)

            if previous_id:
                params["previous_response_id"] = previous_id

        response = self.client.responses.create(**params)

        if session_id:
            # Перемещаем активную сессию в конец словаря.
            self.previous_ids.pop(session_id, None)
            self.previous_ids[session_id] = response.id

            # Не держим бесконечно старые сессии в памяти.
            while len(self.previous_ids) > MAX_SESSIONS:
                oldest_session = next(iter(self.previous_ids))
                self.previous_ids.pop(oldest_session, None)

        return response.output_text
