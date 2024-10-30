// 翻牌效果
const cardContainers = document.querySelectorAll('.card-container');//选择所有名字叫做.card-container的元素，会形成一个元素数组
cardContainers.forEach(cardContainer => //forEach相当于迭代操作，使它可以遍历元素组，cardContainer=>是箭头函数，表示每次迭代时要进行的操作
    cardContainer.addEventListener('click',function(){
             this.classList.toggle('is-flipped');//把原来的元素变成了is-flipped
        }))