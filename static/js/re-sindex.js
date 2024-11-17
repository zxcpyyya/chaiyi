document.addEventListener("DOMContentLoaded", function () {
  const commentInput = document.getElementById("Comments");
  const submitBtn = document.getElementById("submitBtn");
  const submitBtn1 = document.getElementById("submitBtn1");
  const maxLength = 300; // 限制评论长度

  // 限制评论长度
  commentInput.addEventListener("input", function () {
    const currentLength = commentInput.value.length;
    if (currentLength > maxLength) {
      commentInput.value = commentInput.value.substring(0, maxLength); // 限制字数
    }
    // 更新按钮禁用状态
    submitBtn.disabled = commentInput.value.trim().length === 0;
  });

  // 提交评论函数
  function submitComment() {
    const comment = commentInput.value.trim();
    if (comment) {
      // 执行评论提交的逻辑
      commentInput.value = ''; // 清空输入框
      submitBtn.disabled = true; // 禁用按钮
    }
  }

  // 点击提交按钮时提交评论
  submitBtn.addEventListener("click", function () {
    submitComment();
  });

  // 支持按回车键提交评论
  commentInput.addEventListener("keypress", function (event) {
    if (event.key === "Enter" && !event.shiftKey) { // 当按下回车键且不按Shift时
      event.preventDefault(); // 阻止换行
      submitComment(); // 提交评论
    }
  });

  // 页面加载时检查按钮的状态
  submitBtn.disabled = commentInput.value.trim().length === 0;

  // 显示textarea和submitBtn的功能
  submitBtn1.addEventListener('click', function() {
    console.log("submitBtn1 clicked");  // 调试输出
    submitBtn1.style.display = "none";  // 隐藏 submitBtn1
    commentInput.style.display = "block";  // 显示 textarea
    submitBtn.style.display = "block";  // 显示 submitBtn
    submitBtn.disabled = false;  // 使评论按钮可用
  });
});
