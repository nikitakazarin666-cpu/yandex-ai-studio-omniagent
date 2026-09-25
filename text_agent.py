import openai

from config_loader import load_agent_config


YANDEX_CLOUD_MODEL = "yandexgpt"


class TextAgent:

    def __init__(self, api_key: str, base_url: str, project: str):
        self.previous_id = None

        self.config = load_agent_config()
        self.text_config = self.config.get("text", {})

        self.client = openai.OpenAI(
            api_key=api_key,
            base_url=base_url,
            project=project
        )

        self.model = f"gpt://{project}/{YANDEX_CLOUD_MODEL}"

    def send(self, user_input: str) -> str:

        tools = []

        if self.text_config.get("web_search", False):
            domains = self.text_config.get("allowed_domains", [])

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
            "instructions": self.text_config.get(
                "system_prompt",
                "Ты полезный AI-ассистент."
            ),
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

        response = self.client.responses.create(**params)

        self.previous_id = response.id

        return response.output_text
