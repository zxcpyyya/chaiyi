

    var error2 = document.getElementById('error2'); 
    var error3 = document.getElementById('error3'); 


document.querySelector('.img__btn').addEventListener('click', function() { 
     document.querySelector('.dowebok').classList.toggle('s--signup')
    if (error2.innerHTML.trim()) {
    error2.innerHTML = ''; 
     }
    if (error3.innerHTML.trim()) {
    error3.innerHTML = ''; 
     }
    });
    