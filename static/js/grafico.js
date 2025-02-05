document.addEventListener("DOMContentLoaded", function () {
    const menuButton = document.getElementById("menu-toggle");
    const sidebar = document.getElementById("sidebar");
    const buyButton = document.getElementById("buy-btn");
    const sellButton = document.getElementById("sell-btn");
    const chartContainer = document.getElementById("chart-container");

    // 🔹 Ajustar tamanho do gráfico corretamente
    chartContainer.style.width = "100%";
    chartContainer.style.height = "500px";

    // 🔹 Criar Gráfico TradingView (Lightweight Charts)
    const chart = LightweightCharts.createChart(chartContainer, {
        width: window.innerWidth,
        height: window.innerHeight,
        layout: { backgroundColor: '#1a1a1a', textColor: 'white' },
        grid: { vertLines: { color: 'rgba(255, 255, 255, 0.1)' }, horzLines: { color: 'rgba(255, 255, 255, 0.1)' } },
        timeScale: { timeVisible: true, secondsVisible: false },
        rightPriceScale: { borderColor: 'rgba(255, 255, 255, 0.1)' },
    });

    window.addEventListener("resize", () => {
        chart.applyOptions({ width: window.innerWidth, height: window.innerHeight });
    });

    const candleSeries = chart.addCandlestickSeries({
        upColor: '#26a69a', downColor: '#ef5350', borderUpColor: '#26a69a', borderDownColor: '#ef5350',
        wickUpColor: '#26a69a', wickDownColor: '#ef5350'
    });

    // 🔹 Carregar gráfico ao iniciar
    async function carregarGrafico() {
        try {
            const resposta = await fetch('/api/grafico');
            const dados = await resposta.json();

            console.log("📊 Dados antes da filtragem:", dados);

            if (!Array.isArray(dados) || dados.length === 0) {
                console.warn("❌ Nenhum dado de gráfico disponível!");
                return;
            }

            // 🔹 Remover velas inválidas
            const dadosFiltrados = dados.filter(vela => {
                return !(vela.open === vela.high && vela.high === vela.low && vela.low === vela.close && vela.volume === 0);
            });

            if (dadosFiltrados.length === 0) {
                console.error("❌ Nenhuma vela válida disponível.");
                return;
            }

            console.log("✅ Dados filtrados:", dadosFiltrados);
            candleSeries.setData(dadosFiltrados);
        } catch (erro) {
            console.error("❌ Erro ao carregar gráfico:", erro);
        }
    }

    carregarGrafico();

    // 🔹 Atualizar gráfico a cada 5 minutos
    setInterval(async () => {
        try {
            const response = await fetch('/api/grafico/atualizar');
            if (!response.ok) throw new Error(`Erro HTTP: ${response.status}`);
            
            console.log("✅ Nova vela solicitada ao servidor...");
            carregarGrafico();
        } catch (error) {
            console.error("❌ Erro ao atualizar gráfico automaticamente:", error);
        }
    }, 300000); // 5 minutos

    // 🔥 Conectar ao WebSocket do Flask-SocketIO
    const socket = io("http://127.0.0.1:1970");

    // 🔹 WebSocket para novas velas em tempo real
    socket.on("nova_vela", (novaVela) => {
        console.log("🔥 Nova vela recebida:", novaVela);
    
        let timestamp = Date.parse(novaVela.time) / 1000;
    
        // Se o volume for muito alto, destacar como um "Stop Hunt"
        if (novaVela.volume > 50000) {
            console.warn("🚨 Stop Hunt detectado!");
        }
    
        candleSeries.update({
            time: timestamp,
            open: novaVela.open,
            high: novaVela.high,
            low: novaVela.low,
            close: novaVela.close
        });
    });

    // 🔹 Função para processar compra e venda
    async function processarOrdem(tipo) {
        const { value: quantidade } = await Swal.fire({
            title: tipo === "buy" ? "Comprar" : "Vender",
            input: "number",
            inputAttributes: { min: 1, step: 1 },
            showCancelButton: true,
            confirmButtonText: "Confirmar",
            preConfirm: (value) => {
                if (!value || value <= 0) {
                    Swal.showValidationMessage("Insira um valor válido!");
                }
                return value;
            }
        });

        if (!quantidade) return;

        try {
            const resposta = await fetch("/api/grafico/ordem", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ tipo, quantidade })
            });

            if (!resposta.ok) throw new Error(`Erro HTTP: ${resposta.status}`);

            const dados = await resposta.json();
            console.log("✅ Ordem processada com sucesso!", dados);

            Swal.fire({
                icon: "success",
                title: "Ordem processada!",
                text: `Sua ordem de ${tipo.toUpperCase()} foi executada.`,
            });

            carregarGrafico();  // 🔥 Atualizar o gráfico imediatamente após uma nova ordem
        } catch (erro) {
            console.error("❌ Erro ao processar ordem:", erro);
            Swal.fire({
                icon: "error",
                title: "Erro ao processar ordem",
                text: erro.message || "Ocorreu um erro desconhecido.",
            });
        }
    }

    // 🔹 Event Listeners para Compra e Venda
    if (buyButton) {
        buyButton.addEventListener("click", () => processarOrdem("buy"));
    }

    if (sellButton) {
        sellButton.addEventListener("click", () => processarOrdem("sell"));
    }

    // 🔥 ✅ Correção do Menu Hambúrguer ✅
    if (menuButton && sidebar) {
        menuButton.addEventListener("click", function () {
            sidebar.classList.toggle("active");
        });

        document.addEventListener("click", function (event) {
            if (!sidebar.contains(event.target) && !menuButton.contains(event.target)) {
                sidebar.classList.remove("active");
            }
        });
    }
});
