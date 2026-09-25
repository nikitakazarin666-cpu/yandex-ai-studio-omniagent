# OmniAgent — Yandex AI Studio Website Agent

Текстовый и голосовой AI-ассистент для сайтов на базе Yandex AI Studio.

Проект основан на:
https://github.com/yandex-ai-studio/ai-academy-cb-omniagent

Оригинальный README Яндекса сохранён в `README.yandex.md`.

## Возможности

- текстовый AI-ассистент;
- Web Search;
- голосовой Realtime API;
- WebSocket;
- встраиваемый `widget.js`;
- HTTPS / WSS;
- Nginx;
- systemd;
- автоматическое развёртывание на Ubuntu.

## Быстрое развёртывание

```bash
git clone https://github.com/nikitakazarin666-cpu/yandex-ai-studio-omniagent.git /opt/omniagent
cd /opt/omniagent

chmod +x deploy/install.sh
chmod +x deploy/setup.sh

./deploy/install.sh
./deploy/setup.sh
