document.addEventListener("DOMContentLoaded", function () {
    const ibanInput = document.getElementById("iban");
    const ibanMessage = document.getElementById("iban-name");
    const submitButton = document.getElementById("submit-withdraw");

    if (!ibanInput || !ibanMessage || !submitButton) {
        console.error("Erro: Elementos HTML não encontrados.");
        return;
    }

    // 🔹 Verifica IBAN ao digitar
    ibanInput.addEventListener("blur", async function () {
        const iban = ibanInput.value.trim();
        if (iban === "") return;

        try {
            const response = await fetch("/validar_iban_retirada", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ iban: iban }),
            });

            const data = await response.json();

            if (data.success) {
                ibanMessage.textContent = `IBAN Válido: ${data.message}`;
                ibanMessage.style.color = "green";
                ibanMessage.classList.remove("hidden");
                submitButton.disabled = false;
            } else {
                ibanMessage.textContent = "IBAN inválido!";
                ibanMessage.style.color = "red";
                ibanMessage.classList.remove("hidden");
                submitButton.disabled = true;
            }
        } catch (error) {
            console.error("Erro na validação do IBAN:", error);
        }
    });

    // 🔹 Processar a retirada
    submitButton.addEventListener("click", async function (event) {
        event.preventDefault();

        const valor = document.getElementById("amount").value;

        if (!valor) {
            Swal.fire("Atenção!", "Preencha todos os campos!", "warning");
            return;
        }

        const formData = new FormData();
        formData.append("valor", valor);
        formData.append("iban", ibanInput.value);

        try {
            const response = await fetch("/processar_retirada", {
                method: "POST",
                body: formData,
            });

            const data = await response.json();

            if (data.success) {
                Swal.fire("Sucesso!", data.message, "success");
            } else {
                Swal.fire("Erro!", data.message, "error");
            }
        } catch (error) {
            Swal.fire("Erro!", "Falha ao processar retirada. Tente novamente.", "error");
            console.error("Erro ao processar retirada:", error);
        }
    });
});
