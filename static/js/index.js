console.log('running');


// placeholder navbar
navbarelement = document.querySelector('.navbar');
var placeholdernavbar = document.getElementById('placeholder_navbar');

function updateplaceholdernavbar() {
    navbarheight = navbarelement.offsetHeight;
    if (navbarheight != 50) {
        placeholdernavbar.style.height = navbarheight.toString() + "px";
    }
    else {
        placeholdernavbar.style.height = "50px";
    }
}
// first site load
updateplaceholdernavbar();
// updating when window is rezised 
window.addEventListener('resize', updateplaceholdernavbar);



// textarea counter homepage
const textarea = document.getElementById('text');
const counter = document.getElementById('counter');

textarea.addEventListener('input', function() {
    const maxlength = parseInt(textarea.getAttribute('maxlength'));
    const currentlength = textarea.value.length;
    const remaininglength = maxlength - currentlength;

    counter.textContent = remaininglength;

});


// FAQ Dropdowns contact
const faqQuestions = document.querySelectorAll('.faq-question');
const dropups = document.getElementsByClassName('drop-up');

for (var i = 0; i < dropups.length; i += 1) {
    dropups[i].style.display = 'none';
}

faqQuestions.forEach((question) => {
    var dropdown = question.parentElement;
    dropdown = dropdown.querySelector('.drop-down');
    var dropup = question.parentElement;
    dropup = dropup.querySelector('.drop-up');
    var answer = question.parentElement;
    var answer = answer.nextElementSibling;
    
    question.addEventListener('click', () => {
        question.classList.toggle('active');
        answer.style.display = answer.style.display === 'block' ? 'none' : 'block';
        dropdown.style.display = dropdown.style.display === 'none' ? 'block' : 'none';
        dropup.style.display = dropup.style.display === 'none' ? 'block' : 'none';
});
});
