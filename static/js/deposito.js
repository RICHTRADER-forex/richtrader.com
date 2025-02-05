document.addEventListener("DOMContentLoaded", function () {
    const paymentMethod = document.getElementById("payment-method");
    const bankSection = document.getElementById("bank-section");
    const countrySelect = document.getElementById("country");
    const bankDetails = document.getElementById("bank-details");
    const bankInfo = document.getElementById("bank-info");
    const cryptoSection = document.getElementById("crypto-section");
    const comprovanteInput = document.getElementById("comprovante");
    const amountInput = document.getElementById("amount");
    const ibanInput = document.getElementById("iban");
    const ibanMessage = document.getElementById("iban-name");
    const submitButton = document.getElementById("submit-deposit");

    // 🔹 Dados bancários por país
    const bankData = {
        "pt": "<b>Portugal</b><br>IBAN: <b>PT50 0033 0000 4575 1411 8810 5</b>",
        "ao": "<b>Angola</b><br>IBAN: <b>AO06004000002585337610174</b>",
        "br": "<b>Brasil</b><br>Conta: <b>024886052-5</b><br>Agência: <b>0500</b><br>Banco: <b>Itaú 341</b>"
    };

    // 🔹 Mostrar a seção correta com base no método de pagamento
    paymentMethod.addEventListener("change", function () {
        bankSection.classList.add("hidden");
        cryptoSection.classList.add("hidden");
        bankDetails.classList.add("hidden");

        if (this.value === "bank") {
            bankSection.classList.remove("hidden");
        } else if (this.value === "crypto") {
            cryptoSection.classList.remove("hidden");
        }

        validateForm();
    });

    // 🔹 Exibir os dados bancários ao selecionar um país
    countrySelect.addEventListener("change", function () {
        if (this.value) {
            bankInfo.innerHTML = bankData[this.value];
            bankDetails.classList.remove("hidden");
        } else {
            bankDetails.classList.add("hidden");
        }
        validateForm();
    });

    // 🔹 Validação do IBAN ao digitar
    ibanInput.addEventListener("blur", async function () {
        const iban = ibanInput.value.trim();
        if (iban === "") return;

        try {
            const response = await fetch("/validar_iban", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ iban: iban })
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

        validateForm();
    });

    // 🔹 Validação do comprovante
    comprovanteInput.addEventListener("change", function () {
        const file = this.files[0];
        if (file) {
            const allowedTypes = ["image/jpeg", "image/png", "application/pdf"];
            if (!allowedTypes.includes(file.type)) {
                Swal.fire({
                    icon: "error",
                    title: "Arquivo inválido!",
                    text: "Apenas JPG, PNG e PDF são permitidos.",
                    confirmButtonColor: "#ff4b5c"
                });
                this.value = "";
            }
        }
        validateForm();
    });

    // 🔹 Validação do montante
    amountInput.addEventListener("input", function () {
        if (this.value <= 0) {
            this.value = "";
        }
        validateForm();
    });

    // 🔹 Validação do formulário
    function validateForm() {
        const methodSelected = paymentMethod.value !== "";
        const countrySelected = (paymentMethod.value === "bank" && countrySelect.value !== "") || paymentMethod.value === "crypto";
        const hasComprovante = comprovanteInput.files.length > 0;
        const validAmount = amountInput.value > 0;
        const validIban = ibanInput.value.length >= 6;

        if (methodSelected && countrySelected && hasComprovante && validAmount && validIban) {
            submitButton.classList.add("active");
            submitButton.disabled = false;
        } else {
            submitButton.classList.remove("active");
            submitButton.disabled = true;
        }
    }

    // 🔹 Envio do formulário via AJAX
    submitButton.addEventListener("click", async function (event) {
        event.preventDefault();
    
        const metodo = paymentMethod.value;
        const valor = amountInput.value;
        const comprovante = comprovanteInput.files[0];
        const iban = ibanInput.value;
    
        if (!metodo || !valor || !comprovante || !iban) {
            Swal.fire("Atenção!", "Preencha todos os campos e envie um comprovante!", "warning");
            return;
        }
    
        const formData = new FormData();
        formData.append("metodo", metodo === "bank" ? "Transferência Bancária" : "Criptomoedas");
        formData.append("valor", valor);
        formData.append("comprovante", comprovante);
        formData.append("iban", iban);
    
        try {
            const response = await fetch("/processar_deposito", {
                method: "POST",
                body: formData,
            });
    
            // 🔹 Verifica se a resposta é JSON antes de tentar processá-la
            const contentType = response.headers.get("content-type");
            if (!contentType || !contentType.includes("application/json")) {
                throw new Error("Resposta do servidor não está em JSON");
            }
    
            const data = await response.json();
    
            if (data.success) {
                Swal.fire("Sucesso!", data.message, "success");
            } else {
                Swal.fire("Erro!", data.message, "error");
            }
        } catch (error) {
            Swal.fire("Erro!", "Falha ao enviar depósito. Tente novamente.", "error");
            console.error("Erro ao processar depósito:", error);
        }
    });
    
});
