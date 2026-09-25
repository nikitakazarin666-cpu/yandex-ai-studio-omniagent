(function () {

    if (window.__omniagentWidgetLoaded) return;
    window.__omniagentWidgetLoaded = true;

    const currentScript = document.currentScript;
    const BASE_URL = new URL(currentScript.src).origin;
    const AGENT_URL = BASE_URL + '/static/widget-app.html';

    const defaults = {
        primary_color: '#2161f5',
        launcher: {
            icon: '✦',
            label: 'Задать вопрос AI',
            show_label: true,
            position: 'right',
            size: 60
        }
    };

    async function getConfig() {
        try {
            const response = await fetch(
                BASE_URL + '/widget-config',
                { cache: 'no-store' }
            );

            if (!response.ok) throw new Error();

            return await response.json();

        } catch (e) {
            return defaults;
        }
    }

    function init(config) {

        const launcher = {
            ...defaults.launcher,
            ...(config.launcher || {})
        };

        const primary =
            config.primary_color ||
            defaults.primary_color;

        const side =
            launcher.position === 'left'
                ? 'left'
                : 'right';

        const opposite =
            side === 'right'
                ? 'left'
                : 'right';

        const wrapper = document.createElement('div');

        Object.assign(wrapper.style, {
            position: 'fixed',
            bottom: '22px',
            zIndex: '2147483646',
            display: 'flex',
            alignItems: 'center',
            gap: '10px'
        });

        wrapper.style[side] = '22px';

        if (side === 'left') {
            wrapper.style.flexDirection = 'row';
        } else {
            wrapper.style.flexDirection = 'row-reverse';
        }


        const button = document.createElement('button');

        button.textContent = launcher.icon;

        button.setAttribute(
            'aria-label',
            launcher.label
        );

        Object.assign(button.style, {
            width: `${launcher.size}px`,
            height: `${launcher.size}px`,
            flex: `0 0 ${launcher.size}px`,
            border: 'none',
            borderRadius: '50%',
            background: primary,
            color: '#fff',
            fontSize: '25px',
            cursor: 'pointer',
            boxShadow:
                '0 10px 30px rgba(30,70,150,.28)'
        });


        const label = document.createElement('div');

        label.textContent = launcher.label;

        Object.assign(label.style, {
            display:
                launcher.show_label
                    ? 'block'
                    : 'none',
            padding: '10px 14px',
            background: '#fff',
            color: '#172033',
            borderRadius: '14px',
            fontFamily:
                'Inter, Arial, sans-serif',
            fontSize: '14px',
            fontWeight: '600',
            whiteSpace: 'nowrap',
            boxShadow:
                '0 8px 28px rgba(20,35,70,.16)'
        });


        const panel = document.createElement('div');

        Object.assign(panel.style, {
            position: 'fixed',
            bottom: '94px',
            width: '390px',
            height: '590px',
            maxWidth: 'calc(100vw - 24px)',
            maxHeight: 'calc(100vh - 115px)',
            background: '#fff',
            borderRadius: '22px',
            overflow: 'hidden',
            boxShadow:
                '0 24px 70px rgba(19,35,65,.22)',
            zIndex: '2147483647',
            display: 'none'
        });

        panel.style[side] = '22px';
        panel.style[opposite] = 'auto';


        const iframe = document.createElement('iframe');

        iframe.src = AGENT_URL;
        iframe.allow = 'microphone';
        iframe.title = 'AI-ассистент';

        Object.assign(iframe.style, {
            width: '100%',
            height: '100%',
            border: '0',
            display: 'block'
        });

        panel.appendChild(iframe);

        wrapper.appendChild(button);
        wrapper.appendChild(label);

        document.body.appendChild(panel);
        document.body.appendChild(wrapper);


        function openWidget() {
            panel.style.display = 'block';
            button.textContent = '×';
            label.style.display = 'none';
        }


        function closeWidget() {
            iframe.contentWindow.postMessage(
                { type: 'omniagent-hide' },
                BASE_URL
            );

            panel.style.display = 'none';
            button.textContent = launcher.icon;

            if (launcher.show_label) {
                label.style.display = 'block';
            }
        }


        button.addEventListener('click', () => {
            if (panel.style.display === 'block') {
                closeWidget();
            } else {
                openWidget();
            }
        });


        label.addEventListener('click', openWidget);
        label.style.cursor = 'pointer';


        window.addEventListener('message', event => {

            if (
                event.origin === BASE_URL &&
                event.data &&
                event.data.type === 'omniagent-close'
            ) {
                closeWidget();
            }
        });


        function adaptMobile() {

            if (window.innerWidth <= 600) {

                Object.assign(panel.style, {
                    left: '8px',
                    right: '8px',
                    top: '8px',
                    bottom: '82px',
                    width: 'auto',
                    height: 'auto',
                    maxWidth: 'none',
                    maxHeight: 'none'
                });

                label.style.display = 'none';

            } else {

                panel.style.left =
                    side === 'left'
                        ? '22px'
                        : 'auto';

                panel.style.right =
                    side === 'right'
                        ? '22px'
                        : 'auto';

                panel.style.top = 'auto';
                panel.style.bottom = '94px';
                panel.style.width = '390px';
                panel.style.height = '590px';

                if (
                    panel.style.display !== 'block' &&
                    launcher.show_label
                ) {
                    label.style.display = 'block';
                }
            }
        }

        adaptMobile();

        window.addEventListener(
            'resize',
            adaptMobile
        );
    }

    getConfig().then(init);

})();
