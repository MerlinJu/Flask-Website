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

if (textarea && counter) {
    textarea.addEventListener('input', function() {
        const maxlength = parseInt(textarea.getAttribute('maxlength'));
        const currentlength = textarea.value.length;
        const remaininglength = maxlength - currentlength;

        counter.textContent = remaininglength;

    });
}


// FAQ Dropdowns contact
const faqQuestions = document.querySelectorAll('.faq-question');
const dropups = document.getElementsByClassName('drop-up');
const question_boxes = document.querySelectorAll('.faq-element');


for (var i = 0; i < dropups.length; i += 1) {
    dropups[i].style.display = 'none';
}

question_boxes.forEach((question) => {
    console.log(question);

    // var dropdown = question.nextSibling;
    var dropdown = question.querySelector('.drop-down');
    console.log(dropdown);

    // var dropup = question.parentElement;
    var dropup = question.querySelector('.drop-up');
    console.log(dropup);

    var answer = question.querySelector('.faq-answer');
    // console.log(answer);
    
    question.addEventListener('click', () => {
        question.classList.toggle('active');
        answer.style.display = answer.style.display === 'block' ? 'none' : 'block';
        dropdown.style.display = dropdown.style.display === 'none' ? 'block' : 'none';
        dropup.style.display = dropup.style.display === 'none' ? 'block' : 'none';
    });
});


// Settings page informations
const settingstabs = document.querySelectorAll('.settings_tab');
const infos = document.querySelectorAll('.tab_information');

settingstabs.forEach((tab, index) => {
    if (index < settingstabs.length - 1 ) {
        infos[index].style.display = 'none';
        infos[0].style.display = 'block';
        settingstabs[0].classList.add('active');


        tab.addEventListener('click', () => {   
            infos.forEach((info) => {
                info.style.display = 'none';
            });
            console.log(tab);

            settingstabs.forEach((othertab) => {
                othertab.classList.remove('active');
            });
            
            infos[index].style.display = 'block';
            tab.classList.add('active');

        });
    }
});


// cancel personal info submit
const settings_cancel_personal_info = document.getElementById("settings_cancel_personal_info");

if (settings_cancel_personal_info) {
    settings_cancel_personal_info.onclick = function() 
    {cancelsubmit()};

    function cancelsubmit() {
        window.location = "/"
    };
};

// settings change password popup form
document.getElementById('popup_change_pw').style.display = 'none';

function change_password() {
    document.getElementById('popup_change_pw').style.display = 'flex';
}
function close_change_password() {
    document.getElementById('popup_change_pw').style.display = 'none';
}