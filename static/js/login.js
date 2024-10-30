
document.querySelector('.img__btn').addEventListener('click', function() {
    document.querySelector('.dowebok').classList.toggle('s--signup')
})

document.querySelector('.sign-in .submit').addEventListener('click', function(event) {
    event.preventDefault(); // 防止表单默认提交
    const username = document.querySelector('.sign-in input[name="username"]').value;
    const password = document.querySelector('.sign-in input[name="passwd"]').value;

    fetch('你的登录接口', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ username, password })
    })
    .then(response => response.json())
    .then(data => {
        console.log(data);
        // 处理登录响应
    })
    .catch(error => console.error('Error:', error));
});

// 注册处理
document.querySelector('.sign-up .submit').addEventListener('click', function(event) {
    event.preventDefault(); // 防止表单默认提交
    const username = document.querySelector('.sign-up input[name="username"]').value;
    const email = document.querySelector('.sign-up input[name="email"]').value;
    const password = document.querySelector('.sign-up input[name="passwd"]').value;

    fetch('你的注册接口', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ username, email, password })
    })
    .then(response => response.json())
    .then(data => {
        console.log(data);
        // 处理注册响应
    })
    .catch(error => console.error('Error:', error));
});

