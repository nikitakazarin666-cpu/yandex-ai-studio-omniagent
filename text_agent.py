import openai

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

    def send(self, user_input: str) -> str:

        params = {
            "model": self.model,
            "instructions": (
                "Ты ассистент по подбору товаров и ответам на вопросы "
                "интернет-магазина Яндекс Маркет. "
                "Твоя задача — помогать пользователям находить товары "
                "и отвечать на их вопросы. "
                "Если требуется поиск в интернете, искать надо только "
                "на сайте market.yandex.ru. "
                "Если найден подходящий товар, предоставь ссылку на сайт. "
                "Отвечай четко и по делу, избегай лишних слов. "
                "Если не знаешь точного ответа, честно скажи об этом."
            ),
            "tools": [
                {
                    "type": "web_search",
                    "filters": {
                        "allowed_domains": [
                            "market.yandex.ru"
                        ]
                    }
                }
            ],
            "input": [
                {
                    "role": "user",
                    "content": user_input
                }
            ]
        }

        if self.previous_id:
            params["previous_response_id"] = self.previous_id

        response = self.client.responses.create(**params)

        self.previous_id = response.id

        return response.output_text
