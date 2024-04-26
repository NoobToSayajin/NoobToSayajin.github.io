let pSideBar = document.getElementById("pSideBar")
let burger = document.getElementById("burger")

burger.onclick = stateMenu;

function openMenu(){
    pSideBar.classList.add("active");
    burger.classList.add("active");
}
function closeMenu(){
    pSideBar.classList.remove("active")
    burger.classList.remove("active")
}
function stateMenu(){
    if (pSideBar.classList.contains("active")) {
        closeMenu();
    }
    else
    {
        openMenu();
    }
}