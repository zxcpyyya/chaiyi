//搜索框 
window.addEventListener('scroll', function () {
    const box = document.getElementById('CCCC');
    const box1 = this.document.getElementById('slides-right');
    if (window.scrollY >= 440) {
        box.style.transform = 'scaleY(1)'; // 盒子出现
        box1.style.transform = 'scaleY(1)'; // 盒子出现
    } else {
        box.style.transform = 'scaleY(0)'; // 盒子隐藏
        box1.style.transform = 'scaleY(0)'; // 盒子隐藏
    }
});

//右侧点击显示更多分类
document.getElementById('kinds1').onclick = function(event) {
    event.preventDefault(); // 阻止链接的默认行为
   if(document.getElementById('placekinds1').style.display==="none"){ 
    document.getElementById('placekinds1').style.display = 'block'; // 显示图片
    document.getElementById('rightkinds1').style.height ="120px";
    document.getElementById('rightkinds1').style.display = "block";}
    else{
        document.getElementById('placekinds1').style.display="none";
        document.getElementById('rightkinds1').style.height ="30px";
        document.getElementById('rightkinds1').style.display = "flex";
    }
};

document.getElementById('kinds2').onclick = function(event) {
    event.preventDefault(); // 阻止链接的默认行为
   if(document.getElementById('placekinds2').style.display === "none"){ 
    document.getElementById('placekinds2').style.display = 'block'; // 显示图片
    document.getElementById('rightkinds2').style.height ="150px";
    document.getElementById('rightkinds2').style.display = "block";}
    else{
        document.getElementById('placekinds2').style.display="none";
        document.getElementById('rightkinds2').style.height ="30px";
        document.getElementById('rightkinds2').style.display = "flex";
    }
};



 // 以下是轮播图自动切换效果
// 获取所有的radio按钮
const radios = document.querySelectorAll('input[name="control"]');
let currentIndex = 0;
const totalSlides = radios.length;

// 自动切换到下一张图片
function autoSlide() {
    currentIndex = (currentIndex + 1) % totalSlides; // 计算下一个索引
    radios[currentIndex].checked = true; // 选中下一个radio
}
// 设置定时器
let slideInterval = setInterval(autoSlide, 2000); // 每两秒切换

// 重置定时器，防止用户手动点击时自动切换
function resetTimer() {
    clearInterval(slideInterval); // 清除当前定时器
    slideInterval = setInterval(autoSlide, 2000); // 重新设置定时器
}

// 添加事件监听器到每个radio按钮
radios.forEach(radio => {
    radio.addEventListener('click', resetTimer);
});
document.addEventListener('DOMContentLoaded', () => {
    const items = document.querySelectorAll('.item');
    const content = document.querySelector('.content');
    const leftArrow = document.querySelector('.arrowr.left');
    const rightArrow = document.querySelector('.arrowr.right');

    let currentIndex = 0;
    const totalItems = items.length;

    function updateCarousel() {
        const rotation = currentIndex * -120;
        content.style.transform = `translateZ(-35vw) rotateY(${rotation}deg)`;
    }

    function nextItem() {
        currentIndex = (currentIndex + 1) % totalItems;
        updateCarousel();
    }

    function prevItem() {
        currentIndex = (currentIndex - 1 + totalItems) % totalItems;
        updateCarousel();
    }

    rightArrow.addEventListener('click', nextItem);
    leftArrow.addEventListener('click', prevItem);
    setInterval(nextItem, 3000);
});


// 爱心效果
var aixin = document.getElementsByClassName('icon-a-ziyuan13s')[0]; 
var shoucang = document.getElementsByClassName('icon-shoucang1')[0];
aixin.addEventListener("click", function(){
    if (aixin.style.color === "gray") {
        aixin.style.color = "red";
    } else {
        aixin.style.color = "gray"; 
}
});
shoucang.addEventListener("click", function(){
    if (shoucang.style.color === "gray") {
        shoucang.style.color = "yellow";
    } else {
        shoucang.style.color = "gray"; 
}
});