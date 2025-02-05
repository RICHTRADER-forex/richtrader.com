// dashboard.js

document.addEventListener("DOMContentLoaded", function () {
    const menuButton = document.getElementById("menu-toggle");
    const sidebar = document.getElementById("sidebar");

    // Alternar o menu ao clicar no botão
    menuButton.addEventListener("click", function () {
        sidebar.classList.toggle("active");
    });

    // Fechar o menu ao clicar fora dele
    document.addEventListener("click", function (event) {
        if (!sidebar.contains(event.target) && !menuButton.contains(event.target)) {
            sidebar.classList.remove("active");
        }
    });
});

