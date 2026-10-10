// Welcome message
console.log("Spice Garden website loaded!");

// Mobile menu
function toggleMenu() {
    const menu = document.getElementById("navMenu");

    if (menu.style.display === "flex") {
        menu.style.display = "none";
    } else {
        menu.style.display = "flex";
    }
}

// Reservation message
function showMessage() {
    alert("Thank you! Your reservation request has been received.");
}