const button = document.getElementById('submit');

button.addEventListener('mousedown', () => {
    button.style.transform = 'scale(0.95)'; // 按下时缩小
});

button.addEventListener('mouseup', () => {
    button.style.transform = 'scale(1)'; // 松开时恢复大小
});

button.addEventListener('mouseleave', () => {
    button.style.transform = 'scale(1)'; // 离开时恢复大小
});