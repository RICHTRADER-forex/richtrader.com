document.addEventListener("DOMContentLoaded", function () {
    const form = document.getElementById("register-form");

    if (!form) {
        console.error("Elemento #register-form não encontrado!");
        return;
    }

    form.addEventListener("submit", async function (event) {
        event.preventDefault(); // Impede o recarregamento da página

        // Capturar os valores dos inputs
        const nome = document.getElementById("nome").value.trim();
        const email = document.getElementById("email").value.trim();
        const senha = document.getElementById("senha").value.trim();
        const senhaConfirm = document.getElementById("senha-confirm").value.trim();

        // Verificar se os campos estão preenchidos
        if (!nome || !email || !senha || !senhaConfirm) {
            Swal.fire({
                icon: "warning",
                title: "Atenção!",
                text: "Preencha todos os campos antes de continuar.",
            });
            return;
        }

        // Verificar se as senhas coincidem
        if (senha !== senhaConfirm) {
            Swal.fire({
                icon: "error",
                title: "Erro!",
                text: "As senhas não coincidem. Digite novamente.",
            });
            return;
        }

        try {
            // Enviar os dados para o backend via Fetch API para a rota correta
            const response = await fetch("/auth/register", { // 🔹 Corrigido para `/auth/register`
                method: "POST",
                headers: {
                    "Content-Type": "application/x-www-form-urlencoded",
                },
                body: new URLSearchParams({
                    nome: nome,
                    email: email,
                    senha: senha,
                }),
            });

            let data;
            try {
                data = await response.json();
            } catch (error) {
                throw new Error("Resposta inesperada do servidor. Verifique se a API está retornando JSON válido.");
            }

            if (response.ok && data.success) {
                Swal.fire({
                    icon: "success",
                    title: "Cadastro realizado!",
                    text: `Seu IBAN gerado: ${data.iban}`,
                    confirmButtonText: "Fazer Login",
                }).then(() => {
                    window.location.href = "/auth/login"; // 🔹 Corrigido para redirecionar corretamente
                });
            } else {
                Swal.fire({
                    icon: "error",
                    title: "Erro no cadastro!",
                    text: data.message || "Ocorreu um erro inesperado.",
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

    // 🔹 Senha: Alternar visibilidade
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

    // 🔹 Validação da força da senha
    const senhaInput = document.getElementById("senha");
    const passwordStrengthDiv = document.getElementById("password-strength");

    if (senhaInput && passwordStrengthDiv) {
        senhaInput.addEventListener("input", function () {
            verificarForcaSenha(senhaInput.value);
        });
    }

    function verificarForcaSenha(senha) {
        let forca = 0;
        let criterios = [];

        if (senha.length >= 8) { forca++; criterios.push("Mínimo de 8 caracteres"); }
        if (/[A-Z]/.test(senha)) { forca++; criterios.push("Letra maiúscula"); }
        if (/[a-z]/.test(senha)) { forca++; criterios.push("Letra minúscula"); }
        if (/\d/.test(senha)) { forca++; criterios.push("Número"); }
        if (/[\W_]/.test(senha)) { forca++; criterios.push("Caractere especial"); }

        let forcaTexto = "";
        let forcaCor = "";

        if (forca === 0) {
            forcaTexto = "";
        } else if (forca <= 2) {
            forcaTexto = "Senha fraca ❌";
            forcaCor = "red";
        } else if (forca === 3 || forca === 4) {
            forcaTexto = "Senha média ⚠️";
            forcaCor = "orange";
        } else {
            forcaTexto = "Senha forte ✅";
            forcaCor = "green";
        }

        passwordStrengthDiv.innerHTML = `
            <div style="width: 100%; height: 8px; background: lightgray; border-radius: 4px; margin-top: 5px;">
                <div style="width: ${forca * 20}%; height: 100%; background: ${forcaCor}; transition: 0.3s;"></div>
            </div>
            <p style="color: ${forcaCor}; font-size: 14px; margin-top: 5px;">${forcaTexto}</p>
            <small>${criterios.join(" | ")}</small>
        `;
    }
});

