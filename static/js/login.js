// login.js

document.addEventListener("DOMContentLoaded", function () {
    const form = document.getElementById("login-form");

    if (!form) {
        console.error("Elemento #login-form não encontrado!");
        return;
    }

    // Adiciona evento de submit no formulário
    form.addEventListener("submit", async function (event) {
        event.preventDefault(); // Impede o envio padrão

        const email = document.getElementById("email").value.trim();
        const senha = document.getElementById("senha").value.trim();

        if (!email || !senha) {
            Swal.fire({
                icon: "warning",
                title: "Atenção!",
                text: "Preencha todos os campos antes de continuar.",
            });
            return;
        }

        try {
            // Enviar requisição para o backend na URL correta!
            const response = await fetch("/auth/login", {  // 🔥 Alterado de "/login" para "/auth/login"
                method: "POST",
                headers: {
                    "Content-Type": "application/x-www-form-urlencoded",
                },
                body: new URLSearchParams({
                    email: email,
                    senha: senha,
                }),
            });

            const data = await response.json();

            if (response.ok && data.success) {
                Swal.fire({
                    icon: "success",
                    title: "Login bem-sucedido!",
                    text: "Redirecionando para sua conta...",
                    timer: 2000,
                    showConfirmButton: false
                }).then(() => {
                    window.location.href = "/dashboard"; // Redireciona após sucesso
                });
            } else {
                Swal.fire({
                    icon: "error",
                    title: "Erro no login!",
                    text: data.message || "E-mail ou senha incorretos.",
                });
            }
        } catch (error) {
            console.error("Erro na requisição:", error);
            Swal.fire({
                icon: "error",
                title: "Erro no servidor!",
                text: "Não foi possível processar a solicitação. Tente novamente mais tarde.",
            });
        }
    });

    // Função para alternar visibilidade da senha
    document.querySelectorAll(".toggle-password").forEach(button => {
        button.addEventListener("click", function () {
            const targetId = this.getAttribute("data-target");
            const input = document.getElementById(targetId);

            if (input.type === "password") {
                input.type = "text";
                this.textContent = "🙈"; // Ícone de ocultar
            } else {
                input.type = "password";
                this.textContent = "👁️"; // Ícone de mostrar
            }
        });
    });
});

