document.addEventListener("DOMContentLoaded", function () {
    carregarOrderBook();
});

/**
 * 🔥 Função para carregar as ordens do Order Book
 */
async function carregarOrderBook() {
    try {
        const resposta = await fetch('/api/order_book');
        if (!resposta.ok) throw new Error(`Erro HTTP: ${resposta.status}`);

        const ordens = await resposta.json();
        const tabelaCompra = document.getElementById("ordens-compra");
        const tabelaVenda = document.getElementById("ordens-venda");

        tabelaCompra.innerHTML = "";
        tabelaVenda.innerHTML = "";

        ordens.forEach(ordem => {
            const tr = document.createElement("tr");

            tr.innerHTML = `
                <td>${ordem.trader}</td>
                <td>${ordem.quantidade}</td>
                <td>${ordem.preco.toFixed(2)} €</td>
                <td>${new Date(ordem.data_hora).toLocaleString()}</td>
            `;

            if (ordem.tipo === "buy") {
                tabelaCompra.appendChild(tr);  // Adiciona na tabela de compras
            } else {
                tabelaVenda.appendChild(tr);   // Adiciona na tabela de vendas
            }
        });

    } catch (erro) {
        console.error("❌ Erro ao carregar Order Book:", erro);
    }
}

/**
 * 🔄 Atualiza o Order Book a cada 5 segundos
 */
setInterval(carregarOrderBook, 5000);
