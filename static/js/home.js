document.addEventListener("DOMContentLoaded", function () {

    // 🔹 Efeito de Fade-in para Seções ao Rolar a Página
    const sections = document.querySelectorAll("section");

    function revealSections() {
        sections.forEach(section => {
            const sectionTop = section.getBoundingClientRect().top;
            const windowHeight = window.innerHeight;
            
            if (sectionTop < windowHeight - 100) {
                section.classList.add("visible");
            }
        });
    }

    window.addEventListener("scroll", revealSections);
    revealSections(); // Chamar ao carregar a página

    // 🔹 Slider Automático para Depoimentos (Evita Erros se o Elemento Não Existir)
    const testimonials = document.querySelector(".testimonial-slider");
    if (testimonials) {
        let testimonialsList = [
            { text: "Conquistei minha independência financeira com a Rich Trader!", name: "João Silva" },
            { text: "Nunca imaginei que fosse tão fácil começar a investir!", name: "Mariana Costa" },
            { text: "A plataforma me ajudou a lucrar de verdade!", name: "Carlos Mendes" }
        ];

        let currentIndex = 0;

        function updateTestimonial() {
            testimonials.innerHTML = `
                <p>"${testimonialsList[currentIndex].text}"</p>
                <p><strong>${testimonialsList[currentIndex].name}</strong></p>
            `;
            currentIndex = (currentIndex + 1) % testimonialsList.length;
        }

        setInterval(updateTestimonial, 5000);
        updateTestimonial();
    }

    // 🔹 Efeito de Hover nos Cards de Benefícios (Melhorando a Performance)
    const benefitCards = document.querySelectorAll(".benefits .col-md-3");
    benefitCards.forEach(card => {
        card.addEventListener("mouseenter", () => card.classList.add("hover-effect"));
        card.addEventListener("mouseleave", () => card.classList.remove("hover-effect"));
    });

    // 🔹 Efeito Hover nos Logos de Parceiros (Melhorando Performance)
    const partnerLogos = document.querySelectorAll(".partners img");
    partnerLogos.forEach(logo => {
        logo.addEventListener("mouseenter", () => logo.classList.add("logo-hover"));
        logo.addEventListener("mouseleave", () => logo.classList.remove("logo-hover"));
    });

    // 🔹 Alerta no Clique no Botão CTA (Corrigindo Redirecionamento)
    const ctaButton = document.querySelector(".hero .btn");
    if (ctaButton) {
        ctaButton.addEventListener("click", function (event) {
            event.preventDefault();
            Swal.fire({
                title: "Bem-vindo à Rich Trader!",
                text: "Crie sua conta e comece a investir com segurança.",
                icon: "info",
                showCancelButton: true,
                confirmButtonText: "Cadastre-se Agora",
                cancelButtonText: "Voltar"
            }).then((result) => {
                if (result.isConfirmed) {
                    window.location.href = "register.html"; // ✅ Corrigido para GitHub Pages
                }
            });
        });
    }

    // 🔹 Script para abrir e fechar o menu lateral (Removendo Código Duplicado)
    const menuToggle = document.getElementById("menu-toggle");
    const sidebar = document.getElementById("sidebar");

    if (menuToggle && sidebar) {
        menuToggle.addEventListener("click", function () {
            sidebar.classList.toggle("active");
        });
    }

});

