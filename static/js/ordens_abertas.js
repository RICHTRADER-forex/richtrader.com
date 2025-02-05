document.addEventListener("DOMContentLoaded", function () {
    carregarOrdensAbertas();
});

/**
 * 🔥 Função para carregar as ordens abertas e atualizar a tabela
 */
async function carregarOrdensAbertas() {
    try {
        const resposta = await fetch('/api/ordens_abertas');
        if (!resposta.ok) throw new Error(`Erro HTTP: ${resposta.status}`);

        const ordens = await resposta.json();
        const tabela = document.getElementById("tabela-ordens");
        tabela.innerHTML = ""; // Limpa tabela antes de recarregar

        if (ordens.length === 0) {
            tabela.innerHTML = `<tr><td colspan="7">Nenhuma ordem aberta</td></tr>`;
            return;
        }

        ordens.forEach(ordem => {
            let row = tabela.insertRow();

            row.insertCell(0).textContent = ordem.id;  
            row.insertCell(1).textContent = ordem.ativo;  
            row.insertCell(2).textContent = ordem.preco_entrada.toFixed(2);  
            row.insertCell(3).textContent = ordem.quantidade;  

            // 🔥 Lucro/Prejuízo atualizado em tempo real
            let cellLucro = row.insertCell(4);
            cellLucro.textContent = "Calculando...";
            atualizarLucroPrejuizo(ordem, cellLucro);

            // 🔥 Tipo de Ordem (Buy ou Sell)
            let cellAcao = row.insertCell(5);
            cellAcao.textContent = ordem.tipo;  

            // 🔥 Botão de Fechar Ordem
            let cellFechar = row.insertCell(6);
            let btnFechar = document.createElement("button");
            btnFechar.classList.add("btn", "btn-danger", "btn-sm", "fechar-ordem");
            btnFechar.setAttribute("data-id", ordem.id);
            btnFechar.textContent = "Fechar";
            cellFechar.appendChild(btnFechar);
        });

    } catch (erro) {
        console.error("❌ Erro ao carregar ordens abertas:", erro);
        Swal.fire("Erro", "Não foi possível carregar as ordens.", "error");
    }
}

/**
 * 🔥 Função para calcular e atualizar o lucro/prejuízo de cada ordem
 */
async function atualizarLucroPrejuizo(ordem, cellLucro) {
    try {
        let precoAtual = await obterPrecoAtual(ordem.ativo);
        if (precoAtual !== 0) {
            let lucroPrejuizo = ((precoAtual - ordem.preco_entrada) * ordem.quantidade).toFixed(2);
            cellLucro.textContent = lucroPrejuizo > 0 ? `+${lucroPrejuizo} €` : `${lucroPrejuizo} €`;
            cellLucro.classList.add(lucroPrejuizo >= 0 ? "text-success" : "text-danger");
        } else {
            cellLucro.textContent = "Erro no cálculo";
        }
    } catch (erro) {
        console.error("❌ Erro ao calcular lucro/prejuízo:", erro);
    }
}

/**
 * 🔥 Obtém o preço atual do ativo via API do gráfico
 */
async function obterPrecoAtual(ativo) {
    try {
        let response = await fetch(`/api/grafico/ultima-vela`);
        if (!response.ok) throw new Error("Erro ao obter preço do gráfico");

        let dados = await response.json();
        return dados.close;
    } catch (erro) {
        console.error("❌ Erro ao obter preço do gráfico:", erro);
        return 0;  // Retorna 0 em caso de erro
    }
}

/**
 * 🔥 Conexão WebSocket para atualizar ordens em tempo real
 */
const socket = io();
socket.on("nova_ordem", () => {
    console.log("📈 Nova ordem recebida!");
    carregarOrdensAbertas();
});

/**
 * 🔄 Atualiza as ordens abertas a cada 5 segundos
 */
setInterval(carregarOrdensAbertas, 5000);

/**
 * 🔥 Função para fechar uma ordem com confirmação
 */
async function fecharOrdem(id) {
    const confirmacao = await Swal.fire({
        title: "Tem certeza?",
        text: "Essa ação fechará a ordem e aplicará uma taxa de 10%.",
        icon: "warning",
        showCancelButton: true,
        confirmButtonColor: "#d33",
        cancelButtonColor: "#3085d6",
        confirmButtonText: "Sim, fechar",
        cancelButtonText: "Cancelar"
    });

    if (!confirmacao.isConfirmed) return;

    try {
        const resposta = await fetch(`/api/fechar_ordem/${id}`, {
            method: "POST",
            headers: { "Content-Type": "application/json" }
        });

        const resultado = await resposta.json();
        if (!resposta.ok) throw new Error(resultado.message || "Erro ao fechar ordem");

        Swal.fire("Sucesso!", "Ordem fechada com sucesso.", "success");

        // 🔥 Atualiza **somente as ordens abertas** após fechar
        carregarOrdensAbertas();

    } catch (erro) {
        console.error("❌ Erro ao fechar ordem:", erro);
        Swal.fire("Erro", "Não foi possível fechar a ordem.", "error");
    }
}

/**
 * 🔥 Captura clique no botão "Fechar"
 */
document.addEventListener("click", function (event) {
    if (event.target.classList.contains("fechar-ordem")) {
        const ordemId = event.target.getAttribute("data-id");
        fecharOrdem(ordemId);
    }
});
document.addEventListener("DOMContentLoaded", function () {
    const menuToggle = document.getElementById("menu-toggle");
    const sidebar = document.getElementById("sidebar");

    if (menuToggle && sidebar) {
        menuToggle.addEventListener("click", function () {
            sidebar.classList.toggle("active");
        });
    }
});
