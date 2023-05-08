const el = document.getElementById("hamburgerToggle");
el.addEventListener('click', toggleHamburgerMenu);
const hamburgerMenu = document.querySelector('.hamburgerMenu');
const openMenuIcon = document.getElementById('openIcon');
const closeMenuIcon = document.getElementById('closeIcon');
function toggleHamburgerMenu() {
    console.log('hamburger toggles');
    console.log(hamburgerMenu.classList);
    if (hamburgerMenu.classList.contains('showHamburgerMenu')) {
        hamburgerMenu.classList.toggle("showHamburgerMenu");
        // hamburgerMenu.classList.remove("showHamburgerMenu");
        closeMenuIcon.style.display = "none";
        openMenuIcon.style.display = "block";
    }
    else {
        hamburgerMenu.classList.toggle("showHamburgerMenu");
        closeMenuIcon.style.display = "block";
        openMenuIcon.style.display = "none";
    }
}
