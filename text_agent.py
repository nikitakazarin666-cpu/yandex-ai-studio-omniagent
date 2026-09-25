import openai

from config_loader import load_agent_config


YANDEX_CLOUD_MODEL = "yandexgpt"


class TextAgent:

    def __init__(self, api_key: str, base_url: str, project: str):
        self.previous_id = None

        self.client = openai.OpenAI(
            api_key=api_key,
            base_url=base_url,
            project=project
        )

        self.model = f"gpt://{project}/{YANDEX_CLOUD_MODEL}"

    def send(
        self,
        user_input: str,
        capability_id: str | None = None
    ) -> str:

        # Конфиг перечитывается на каждом запросе.
        # Это позволяет менять настройки клиента без изменения кода.
        config = load_agent_config()
        text_config = config.get("text", {})

        instructions = text_config.get(
            "system_prompt",
            "Ты полезный AI-ассистент."
        )

        # Подключаем инструкции активной бизнес-функции.
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

        if self.previous_id:
            params["previous_response_id"] = self.previous_id

        response = self.client.responses.create(
            **params
        )

        self.previous_id = response.id

        return response.output_text
