// Dashboard GLPI - JavaScript
class DashboardManager {
    constructor() {
        this.charts = {};
        this.currentFilters = {};
        this.init();
    }

    init() {
        console.log('Inicializando Dashboard GLPI...');
        this.setupEventListeners();
        this.loadInitialData();
    }

    setupEventListeners() {
        // Botão aplicar filtros
        document.getElementById('apply-filters').addEventListener('click', () => {
            this.applyFilters();
        });

        // Botão limpar filtros
        document.getElementById('clear-filters').addEventListener('click', () => {
            this.clearFilters();
        });

        // Enter no campo de requisitante
        document.getElementById('requisitante-filter').addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                this.applyFilters();
            }
        });

        // Auto-aplicar filtros quando selects mudarem
        const selects = document.querySelectorAll('.filter-select');
        selects.forEach(select => {
            select.addEventListener('change', () => {
                // Aguarda um pouco antes de aplicar para evitar muitas requisições
                setTimeout(() => this.applyFilters(), 500);
            });
        });
    }

    showLoading(show = true) {
        const overlay = document.getElementById('loading-overlay');
        overlay.style.display = show ? 'flex' : 'none';
    }

    async loadInitialData() {
        this.showLoading(true);
        try {
            await Promise.all([
                this.loadMetrics(),
                this.loadChartData()
            ]);
        } catch (error) {
            console.error('Erro ao carregar dados iniciais:', error);
            this.showError('Erro ao carregar dados do dashboard');
        } finally {
            this.showLoading(false);
        }
    }

    async loadMetrics(filters = {}) {
        try {
            const params = new URLSearchParams(filters);
            const response = await fetch(`/api/metrics?${params}`);
            const metrics = await response.json();
            
            this.updateMetricsDisplay(metrics);
        } catch (error) {
            console.error('Erro ao carregar métricas:', error);
        }
    }

    updateMetricsDisplay(metrics) {
        document.getElementById('total-chamados').textContent = metrics.total_chamados || 0;
        document.getElementById('total-pendente').textContent = metrics.total_pendente || 0;
        document.getElementById('total-atribuido').textContent = metrics.total_atribuido || 0;
        document.getElementById('total-fechado').textContent = metrics.total_fechado || 0;
        document.getElementById('chamados-novos').textContent = metrics.chamados_novos || 0;
    }

    async loadChartData(filters = {}) {
        const chartTypes = ['requisitante', 'categoria', 'localizacao', 'tipos'];
        
        for (const chartType of chartTypes) {
            try {
                const params = new URLSearchParams(filters);
                const response = await fetch(`/api/chart-data/${chartType}?${params}`);
                const data = await response.json();
                
                this.updateChart(chartType, data);
            } catch (error) {
                console.error(`Erro ao carregar dados do gráfico ${chartType}:`, error);
            }
        }
    }

    updateChart(chartType, data) {
        const canvasId = `chart-${chartType === 'tipos' ? 'tipos' : chartType}`;
        const canvas = document.getElementById(canvasId);
        
        if (!canvas) {
            console.error(`Canvas não encontrado: ${canvasId}`);
            return;
        }

        // Destruir gráfico existente se houver
        if (this.charts[chartType]) {
            this.charts[chartType].destroy();
        }

        const ctx = canvas.getContext('2d');
        
        let chartConfig = {};

        switch (chartType) {
            case 'requisitante':
                chartConfig = this.getBarChartConfig(data, 'Chamados por Requisitante');
                break;
            case 'categoria':
                chartConfig = this.getHorizontalBarChartConfig(data, 'Chamados por Categoria');
                break;
            case 'localizacao':
                chartConfig = this.getBarChartConfig(data, 'Chamados por Localização');
                break;
            case 'tipos':
                chartConfig = this.getPieChartConfig(data, 'Distribuição por Tipo');
                break;
        }

        this.charts[chartType] = new Chart(ctx, chartConfig);
    }

    getBarChartConfig(data, title) {
        return {
            type: 'bar',
            data: {
                labels: data.labels,
                datasets: [{
                    label: 'Quantidade',
                    data: data.data,
                    backgroundColor: data.backgroundColor,
                    borderColor: data.backgroundColor,
                    borderWidth: 1,
                    borderRadius: 4,
                    borderSkipped: false
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: false
                    },
                    tooltip: {
                        backgroundColor: 'rgba(0,0,0,0.8)',
                        titleColor: 'white',
                        bodyColor: 'white',
                        cornerRadius: 6
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        grid: {
                            color: 'rgba(0,0,0,0.1)'
                        },
                        ticks: {
                            font: {
                                size: 12
                            }
                        }
                    },
                    x: {
                        grid: {
                            display: false
                        },
                        ticks: {
                            font: {
                                size: 12
                            },
                            maxRotation: 45
                        }
                    }
                }
            }
        };
    }

    getHorizontalBarChartConfig(data, title) {
        return {
            type: 'bar',
            data: {
                labels: data.labels,
                datasets: [{
                    label: 'Quantidade',
                    data: data.data,
                    backgroundColor: data.backgroundColor,
                    borderColor: data.backgroundColor,
                    borderWidth: 1,
                    borderRadius: 4,
                    borderSkipped: false
                }]
            },
            options: {
                indexAxis: 'y',
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: false
                    },
                    tooltip: {
                        backgroundColor: 'rgba(0,0,0,0.8)',
                        titleColor: 'white',
                        bodyColor: 'white',
                        cornerRadius: 6
                    }
                },
                scales: {
                    x: {
                        beginAtZero: true,
                        grid: {
                            color: 'rgba(0,0,0,0.1)'
                        },
                        ticks: {
                            font: {
                                size: 12
                            }
                        }
                    },
                    y: {
                        grid: {
                            display: false
                        },
                        ticks: {
                            font: {
                                size: 12
                            }
                        }
                    }
                }
            }
        };
    }

    getPieChartConfig(data, title) {
        return {
            type: 'doughnut',
            data: {
                labels: data.labels,
                datasets: [{
                    data: data.data,
                    backgroundColor: data.backgroundColor,
                    borderWidth: 2,
                    borderColor: '#ffffff'
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                cutout: '40%',
                plugins: {
                    legend: {
                        display: false // Usamos legenda customizada no HTML
                    },
                    tooltip: {
                        backgroundColor: 'rgba(0,0,0,0.8)',
                        titleColor: 'white',
                        bodyColor: 'white',
                        cornerRadius: 6,
                        callbacks: {
                            label: function(context) {
                                const total = context.dataset.data.reduce((a, b) => a + b, 0);
                                const percentage = ((context.parsed * 100) / total).toFixed(1);
                                return `${context.label}: ${context.parsed} (${percentage}%)`;
                            }
                        }
                    }
                }
            }
        };
    }

    getCurrentFilters() {
        return {
            categoria: document.getElementById('categoria-filter').value,
            status: document.getElementById('status-filter').value,
            periodo: document.getElementById('periodo-filter').value,
            requisitante: document.getElementById('requisitante-filter').value
        };
    }

    async applyFilters() {
        this.currentFilters = this.getCurrentFilters();
        
        // Remove filtros vazios
        Object.keys(this.currentFilters).forEach(key => {
            if (!this.currentFilters[key]) {
                delete this.currentFilters[key];
            }
        });

        console.log('Aplicando filtros:', this.currentFilters);
        
        this.showLoading(true);
        try {
            await Promise.all([
                this.loadMetrics(this.currentFilters),
                this.loadChartData(this.currentFilters)
            ]);
            
            this.showFilterStatus();
        } catch (error) {
            console.error('Erro ao aplicar filtros:', error);
            this.showError('Erro ao aplicar filtros');
        } finally {
            this.showLoading(false);
        }
    }

    clearFilters() {
        document.getElementById('categoria-filter').value = '';
        document.getElementById('status-filter').value = '';
        document.getElementById('periodo-filter').value = '30';
        document.getElementById('requisitante-filter').value = '';
        
        this.currentFilters = {};
        this.applyFilters();
    }

    showFilterStatus() {
        const activeFilters = Object.keys(this.currentFilters).length;
        if (activeFilters > 0) {
            console.log(`${activeFilters} filtro(s) ativo(s)`);
            // Você pode adicionar uma indicação visual aqui
        }
    }

    showError(message) {
        // Implementar notificação de erro
        console.error(message);
        alert(message); // Temporário - substitua por uma notificação melhor
    }

    // Método para exportar dados (para uso futuro)
    async exportData(format = 'csv') {
        try {
            const params = new URLSearchParams(this.currentFilters);
            const response = await fetch(`/api/export/${format}?${params}`);
            const result = await response.json();
            
            console.log('Dados exportados:', result);
            // Implementar download do arquivo
        } catch (error) {
            console.error('Erro ao exportar dados:', error);
            this.showError('Erro ao exportar dados');
        }
    }

    // Método para atualizar dados em tempo real (para uso futuro)
    startRealTimeUpdates(interval = 30000) {
        setInterval(() => {
            console.log('Atualizando dados em tempo real...');
            this.loadInitialData();
        }, interval);
    }
}

// Inicializar o dashboard quando a página carregar
document.addEventListener('DOMContentLoaded', () => {
    window.dashboard = new DashboardManager();
    
    // Configurações globais do Chart.js
    Chart.defaults.font.family = "'Segoe UI', Tahoma, Geneva, Verdana, sans-serif";
    Chart.defaults.font.size = 12;
    Chart.defaults.color = '#666';
    
    console.log('Dashboard GLPI carregado com sucesso!');
});

// Expor funções globais se necessário
window.DashboardUtils = {
    refreshData: () => {
        if (window.dashboard) {
            window.dashboard.loadInitialData();
        }
    },
    
    exportData: (format) => {
        if (window.dashboard) {
            window.dashboard.exportData(format);
        }
    },
    
    setAutoRefresh: (enabled, interval = 30000) => {
        if (window.dashboard && enabled) {
            window.dashboard.startRealTimeUpdates(interval);
        }
    }
};