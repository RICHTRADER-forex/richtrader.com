document.addEventListener("DOMContentLoaded", function () {
    carregarHistoricoOrdens();
});

/**
 * 🔥 Função para carregar as ordens fechadas e atualizar a tabela de histórico
 */
async function carregarHistoricoOrdens() {
    try {
        const tabela = document.getElementById("tabela-historico");

        // 🔥 Se a tabela não existir, evita erro
        if (!tabela) {
            console.error("❌ Erro: Elemento #tabela-historico não encontrado!");
            return;
        }

        const resposta = await fetch('/api/historico_ordens');
        if (!resposta.ok) throw new Error(`Erro HTTP: ${resposta.status}`);

        const historico = await resposta.json();
        tabela.innerHTML = ""; // 🔥 Limpa antes de inserir os dados

        if (historico.length === 0) {
            tabela.innerHTML = `<tr><td colspan="7">Nenhuma ordem fechada ainda.</td></tr>`;
            return;
        }

        historico.forEach(ordem => {
            const tr = document.createElement("tr");

            // 🔥 Verifica se os valores existem antes de chamar `.toFixed()`
            const precoEntrada = ordem.preco_entrada ? ordem.preco_entrada.toFixed(2) : "0.00";
            const quantidade = ordem.quantidade ? ordem.quantidade : 0;
            const lucroPrejuizo = ordem.lucro_prejuizo ? ordem.lucro_prejuizo.toFixed(2) : "0.00";
            const comissao = ordem.comissao ? ordem.comissao.toFixed(2) : "0.00";

            tr.innerHTML = `
                <td>${ordem.id}</td>
                <td>${ordem.ativo}</td>
                <td>${precoEntrada}</td>
                <td>${quantidade}</td>
                <td class="${lucroPrejuizo >= 0 ? 'text-success' : 'text-danger'}">
                    ${lucroPrejuizo} €
                </td>
                <td class="text-danger">-${comissao} €</td>
                <td>${new Date(ordem.timestamp).toLocaleString()}</td>
            `;

            tabela.appendChild(tr);
        });

    } catch (erro) {
        console.error("❌ Erro ao carregar histórico:", erro);
    }
}

/**
 * 🔄 Atualiza o histórico a cada 10 segundos (caso feche ordens em tempo real)
 */
setInterval(carregarHistoricoOrdens, 10000);
document.addEventListener("DOMContentLoaded", function () {
    const menuToggle = document.getElementById("menu-toggle");
    const sidebar = document.getElementById("sidebar");

    if (menuToggle && sidebar) {
        menuToggle.addEventListener("click", function () {
            sidebar.classList.toggle("active");
        });
    }
});
