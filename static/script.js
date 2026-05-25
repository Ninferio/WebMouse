const touchpad = document.getElementById('touchpad');
let lastX = null;
let lastY = null;
let isSending = false;

//Функция отправки координат на ПК
function sendMove(dx, dy) {
    // Защита от спама 
    if (isSending) return;
    isSending = true;

    fetch(`/move_mouse?dx=${dx}&dy=${dy}`)
        .finally(() => { isSending = false; });
}


touchpad.addEventListener('touchstart', (e) => {
    const touch = e.touches[0];
    lastX = touch.clientX;
    lastY = touch.clientY;
}, { passive: true });

//Движение пальца
touchpad.addEventListener('touchmove', (e) => {
    if (lastX === null || lastY === null) return;

    const touch = e.touches[0];
    const dx = touch.clientX - lastX;
    const dy = touch.clientY - lastY;
    if (dx !== 0 || dy !== 0) {
        sendMove(dx, dy);
    }

    lastX = touch.clientX;
    lastY = touch.clientY;
}, { passive: true });

// Сброс
touchpad.addEventListener('touchend', () => {
    lastX = null;
    lastY = null;
});

// ПКМ ЛКМ
document.getElementById('leftBtn').addEventListener('touchstart', (e) => { e.preventDefault(); fetch('/click?b=left'); });
document.getElementById('rightBtn').addEventListener('touchstart', (e) => { e.preventDefault(); fetch('/click?b=right'); });
