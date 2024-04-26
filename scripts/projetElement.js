if (window.screen.width >= 1023)
{
    let index = document.getElementById("index")
    index.setAttribute("open", "open")
}
document.querySelector(".pdfProjet").onclick = function() {window.open("/pdf/Cahier_des_charges.pdf", "_blank");}
