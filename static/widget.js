(function () {

    if (window.__omniagentWidgetLoaded) return;

    window.__omniagentWidgetLoaded = true;

    const currentScript =
        document.currentScript;

    const BASE_URL =
        new URL(currentScript.src).origin;

    const AGENT_URL =
        BASE_URL + '/static/widget-app.html';


    const button = document.createElement('button');

    button.innerHTML = '✦';

    button.setAttribute(
        'aria-label',
        'Открыть AI-ассистента'
    );

    Object.assign(button.style, {
        position: 'fixed',
        right: '22px',
        bottom: '22px',
        width: '60px',
        height: '60px',
        border: 'none',
        borderRadius: '50%',
        background: '#2161f5',
        color: '#fff',
        fontSize: '25px',
        cursor: 'pointer',
        boxShadow: '0 10px 30px rgba(33,97,245,.32)',
        zIndex: '2147483646'
    });


    const panel = document.createElement('div');

    Object.assign(panel.style, {
        position: 'fixed',
        right: '22px',
        bottom: '94px',
        width: '390px',
        height: '590px',
        maxWidth: 'calc(100vw - 24px)',
        maxHeight: 'calc(100vh - 115px)',
        background: '#fff',
        borderRadius: '22px',
        overflow: 'hidden',
        boxShadow: '0 24px 70px rgba(19,35,65,.22)',
        zIndex: '2147483647',
        display: 'none'
    });


    const iframe =
        document.createElement('iframe');

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

    document.body.appendChild(panel);
    document.body.appendChild(button);


    function openWidget() {

        panel.style.display = 'block';

        button.innerHTML = '×';

        button.setAttribute(
            'aria-label',
            'Закрыть AI-ассистента'
        );
    }


    function closeWidget() {

        iframe.contentWindow.postMessage(
            { type: 'omniagent-hide' },
            '*'
        );

        panel.style.display = 'none';

        button.innerHTML = '✦';

        button.setAttribute(
            'aria-label',
            'Открыть AI-ассистента'
        );
    }


    button.addEventListener('click', () => {

        if (panel.style.display === 'block') {
            closeWidget();
        } else {
            openWidget();
        }
    });


    window.addEventListener('message', event => {

        if (
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
                maxHeight: 'none',
                borderRadius: '20px'
            });

            button.style.right = '16px';
            button.style.bottom = '16px';

        } else {

            Object.assign(panel.style, {
                left: 'auto',
                top: 'auto',
                right: '22px',
                bottom: '94px',
                width: '390px',
                height: '590px',
                maxWidth: 'calc(100vw - 24px)',
                maxHeight: 'calc(100vh - 115px)',
                borderRadius: '22px'
            });
        }
    }


    adaptMobile();

    window.addEventListener(
        'resize',
        adaptMobile
    );

})();
