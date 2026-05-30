const touchpad = document.getElementById('touchpad');
const statusText = document.getElementById('status-text');

let lastX = null, lastY = null;
let lastScrollY = null;

let isMoving = false;
let lastTapTime = 0;
let longTouchTimer = null;

// Троттлинг: запрещаем отправку запросов чаще, чем раз в 16 мс (60 раз в секунду)
let lastRequestTime = 0;
const MIN_REQUEST_INTERVAL = 16;

function sendRequest(url, force = false) {
    const now = Date.now();
    if (!force && (now - lastRequestTime < MIN_REQUEST_INTERVAL)) {
        return; // Скипаем запрос, если он отправлен слишком быстро
    }
    lastRequestTime = now;
    fetch(url).catch(err => console.error("Сбой сети:", err));
}

// Начало касания
touchpad.addEventListener('touchstart', (e) => {
    isMoving = false;
    const touches = e.touches;

    if (touches.length === 1) {
        lastX = touches[0].clientX;
        lastY = touches[0].clientY;

        // Жест: Долгое удержание для ПКМ (0.5 секунды)
        longTouchTimer = setTimeout(() => {
            if (!isMoving) {
                sendRequest('/click?b=right', true);
                if (navigator.vibrate) navigator.vibrate(50); // Легкая вибрация, если поддерживается
            }
        }, 500);

    } else if (touches.length === 2) {
        // Если коснулись вторым пальцем — отменяем таймер удержания ПКМ
        clearTimeout(longTouchTimer);
        lastScrollY = (touches[0].clientY + touches[1].clientY) / 2;
    }
}, { passive: true });

// Движение пальцев
touchpad.addEventListener('touchmove', (e) => {
    const touches = e.touches;

    // Если палец сдвинулся больше чем на 3 пикселя, считаем это перемещением
    isMoving = true;
    clearTimeout(longTouchTimer); // Сбрасываем удержание ПКМ, так как началось движение

    if (touches.length === 1 && lastX !== null && lastY !== null) {
        // 1 ПАЛЕЦ: Плавное перемещение мыши
        const dx = touches[0].clientX - lastX;
        const dy = touches[0].clientY - lastY;

        if (dx !== 0 || dy !== 0) {
            sendRequest(`/move_mouse?dx=${dx}&dy=${dy}`);
        }
        lastX = touches[0].clientX;
        lastY = touches[0].clientY;

    } else if (touches.length === 2 && lastScrollY !== null) {
        // 2 ПАЛЬЦА: Ограниченный по скорости скролл (колесико)
        const currentScrollY = (touches[0].clientY + touches[1].clientY) / 2;
        const diffY = currentScrollY - lastScrollY;

        if (Math.abs(diffY) > 4) {
            const scrollDirection = diffY > 0 ? -1 : 1;
            sendRequest(`/scroll?clicks=${scrollDirection}`);
            lastScrollY = currentScrollY;
        }
    }
}, { passive: true });

// Конец касания
touchpad.addEventListener('touchend', (e) => {
    clearTimeout(longTouchTimer); // Защита от ложных срабатываний ПКМ

    // Если палец убрали БЕЗ движения — это клик (тап)
    if (!isMoving && e.touches.length === 0) {
        const now = Date.now();
        const TIMESPAN = now - lastTapTime;

        if (TIMESPAN < 250) {
            // ЖЕСТ: Двойной быстрый клик (Дабл-клик ЛКМ)
            sendRequest('/click?b=left', true);
            setTimeout(() => sendRequest('/click?b=left', true), 50);
        } else {
            // ЖЕСТ: Одиночный клик (ЛКМ)
            sendRequest('/click?b=left', true);
        }
        lastTapTime = now;
    }

    // Сброс координат
    lastX = null;
    lastY = null;
    lastScrollY = null;
});
