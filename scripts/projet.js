function redirect()
{
    window.location = "/index.html";
}
// selecting all sections with class of section
const cards = document.querySelectorAll(".card");

// Foreach card when clicked
cards.forEach((card) => {
    card.addEventListener("mouseover", () => {
    
    // remove active class from all another card and
    // add it to the selected card
    cards.forEach((card) => {
        card.classList.remove("active");
    });
        card.classList.add("active");
    });
    document.querySelector(".one").onclick = function() {document.location.href = '/pdf/DataOne.pdf';}
    document.querySelector(".two").onclick = function() {document.location.href = '/pdf/Mairie.pdf';}
    document.querySelector(".three").onclick = function() {document.location.href = '/Nav/Projet/main.html';}
    document.querySelector(".four").onclick = function() {document.location.href = '/Nav/synthese.html';}
});