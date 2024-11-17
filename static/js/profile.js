var Informa = document.getElementById('Informa');
var manage = document.getElementById('manage');
var container2 = document.getElementById('container2');
var container = document.getElementById('container');
manage.addEventListener("click",function(){
    container.style.display = "none";
    container2.style.display = "block";
})
Informa.addEventListener("click",function(){
    container2.style.display = "none";
    container.style.display = "block";
})


// 喜欢收藏
var love = document.getElementById('love');
var shoucang = document.getElementById('shoucang');
var lovebox = document.getElementById('lovebox');
var shoucangbox = document.getElementById('shoucangbox');  // 修正拼写错误

// 默认显示喜欢盒子
lovebox.style.display = "block";
shoucangbox.style.display = "none";

love.addEventListener("click", function() {
    shoucangbox.style.display = "none"; // 隐藏收藏
    lovebox.style.display = "block"; // 显示喜欢
});

shoucang.addEventListener("click", function() {
    lovebox.style.display = "none"; // 隐藏喜欢
    shoucangbox.style.display = "block"; // 显示收藏
});
