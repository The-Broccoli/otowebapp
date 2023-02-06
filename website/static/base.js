function mobileOpenNav() {
    let button = document.getElementById('burgerMenu');
    let nav = document.getElementById('nav');
    let navbar = document.getElementById('navBar');

    navbar.classList.add('fixed');
    nav.classList.remove('mobile');
    button.innerHTML = '<svg onclick="mobileCloseNav()" xmlns="http://www.w3.org/2000/svg" height="48" width="48"><path d="m12.45 37.65-2.1-2.1L21.9 24 10.35 12.45l2.1-2.1L24 21.9l11.55-11.55 2.1 2.1L26.1 24l11.55 11.55-2.1 2.1L24 26.1Z"/></svg>';
}

function mobileCloseNav() {
    let button = document.getElementById('burgerMenu');
    let nav = document.getElementById('nav');
    let navbar = document.getElementById('navBar');

    navbar.classList.remove('fixed');
    nav.classList.add('mobile');
    button.innerHTML = '<svg onclick="mobileOpenNav()" xmlns="http://www.w3.org/2000/svg" height="48" width="48"><path d="M6 36v-3h36v3Zm0-10.5v-3h36v3ZM6 15v-3h36v3Z"/></svg>';
}