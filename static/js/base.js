window.addEventListener("load", function() {
  function showHamburgerNavLinks() {
    let hamburgerLinks = document.getElementById("hamburgerNavBar");
    if (hamburgerLinks.style.display === "block") {
      hamburgerLinks.style.display = "none";
    } else {
      hamburgerLinks.style.display = "block";
    }
  }

  let hamburgerButton = document.getElementById("hamburger");
  hamburgerButton.onclick = showHamburgerNavLinks;
})