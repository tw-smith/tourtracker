const el = document.getElementById("hamburgerToggle");
el.addEventListener('click', toggleHamburgerMenu);
const hamburgerMenu = document.querySelector('.hamburgerMenu');
const openMenuIcon = document.getElementById('openIcon');
const closeMenuIcon = document.getElementById('closeIcon');
const bodyElement = document.getElementsByTagName("body")[0];
function toggleHamburgerMenu() {
    if (hamburgerMenu.classList.contains('showHamburgerMenu')) {
        hamburgerMenu.classList.toggle("showHamburgerMenu");
        closeMenuIcon.style.display = "none";
        openMenuIcon.style.display = "block";
        bodyElement.classList.toggle('preventScroll');
    }
    else {
        hamburgerMenu.classList.toggle("showHamburgerMenu");
        closeMenuIcon.style.display = "block";
        openMenuIcon.style.display = "none";
        bodyElement.classList.toggle('preventScroll');
    }
}
