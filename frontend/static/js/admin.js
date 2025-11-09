/**
 * MyBella Admin Dashboard Management
 * Handles analytics, persona management, and system monitoring
 */

class AdminDashboard {
    constructor() {
        this.currentTab = 'analytics';
        this.charts = {};
        this.refreshInterval = null;
        this.init();
    }

    init() {
        this.setupEventListeners();
        this.loadInitialData();
        this.startAutoRefresh();
    }

    setupEventListeners() {
        // Tab switching
        document.querySelectorAll('.tab-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                this.switchTab(e.target.dataset.tab);
            });
        });

        // Analytics filters
        document.getElementById('userTimeFilter')?.addEventListener('change', () => {
            this.loadUserAnalytics();
        });

        document.getElementById('revenueTimeFilter')?.addEventListener('change', () => {
            this.loadRevenueAnalytics();
        });

        // Persona management
        document.getElementById('createPersonaBtn')?.addEventListener('click', () => {
            this.openCreatePersonaModal();
        });

        document.getElementById('createPersonaForm')?.addEventListener('submit', (e) => {
            e.preventDefault();
            this.createPersona();
        });

        document.getElementById('editPersonaForm')?.addEventListener('submit', (e) => {
            e.preventDefault();
            this.updatePersona();
        });

        document.getElementById('deletePersonaBtn')?.addEventListener('click', () => {
            this.deletePersona();
        });

        // System controls
        document.getElementById('reloadMetrics')?.addEventListener('click', () => {
            this.reloadSystemMetrics();
        });

        document.getElementById('refreshLogs')?.addEventListener('click', () => {
            this.loadSystemLogs();
        });

        // Modal controls
        document.querySelectorAll('.modal-close').forEach(btn => {
            btn.addEventListener('click', (e) => {
                this.closeModal(e.target.closest('.modal').id);
            });
        });

        // Close modals on outside click
        document.querySelectorAll('.modal').forEach(modal => {
            modal.addEventListener('click', (e) => {
                if (e.target === modal) {
                    this.closeModal(modal.id);
                }
            });
        });
    }

    switchTab(tabName) {
        // Update tab buttons
        document.querySelectorAll('.tab-btn').forEach(btn => {
            btn.classList.remove('active');
        });
        document.querySelector(`[data-tab="${tabName}"]`).classList.add('active');

        // Update tab content
        document.querySelectorAll('.tab-content').forEach(content => {
            content.classList.remove('active');
        });
        document.getElementById(`${tabName}-tab`).classList.add('active');

        this.currentTab = tabName;

        // Load tab-specific data
        switch (tabName) {
            case 'analytics':
                this.loadAnalytics();
                break;
            case 'personas':
                this.loadPersonas();
                break;
            case 'system':
                this.loadSystemData();
                break;
        }
    }

    async loadInitialData() {
        await this.loadDashboardSummary();
        if (this.currentTab === 'analytics') {
            await this.loadAnalytics();
        }
    }

    async loadDashboardSummary() {
        try {
            const response = await fetch('/admin/api/dashboard-summary');
            const data = await response.json();

            document.getElementById('totalUsers').textContent = data.totalUsers || '0';
            document.getElementById('monthlyRevenue').textContent = `$${(data.monthlyRevenue || 0).toLocaleString()}`;
            document.getElementById('totalPersonas').textContent = data.totalPersonas || '0';
            document.getElementById('apiUsage').textContent = (data.apiUsage || 0).toLocaleString();
        } catch (error) {
            console.error('Error loading dashboard summary:', error);
            this.showError('Failed to load dashboard summary');
        }
    }

    async loadAnalytics() {
        await Promise.all([
            this.loadUserAnalytics(),
            this.loadRevenueAnalytics(),
            this.loadApiAnalytics(),
            this.loadPerformanceMetrics()
        ]);
    }

    async loadUserAnalytics() {
        try {
            const timeFilter = document.getElementById('userTimeFilter').value;
            const response = await fetch(`/admin/api/user-analytics?period=${timeFilter}`);
            const data = await response.json();

            // Update stats
            document.getElementById('activeUsers').textContent = data.activeUsers || '0';
            document.getElementById('inactiveUsers').textContent = data.inactiveUsers || '0';
            document.getElementById('newRegistrations').textContent = data.newRegistrations || '0';
            document.getElementById('churnRate').textContent = `${data.churnRate || 0}%`;

            // Update chart
            this.updateUserChart(data.chartData || []);
        } catch (error) {
            console.error('Error loading user analytics:', error);
        }
    }

    async loadRevenueAnalytics() {
        try {
            const timeFilter = document.getElementById('revenueTimeFilter').value;
            const response = await fetch(`/admin/api/revenue-analytics?period=${timeFilter}`);
            const data = await response.json();

            // Update stats
            document.getElementById('totalRevenue').textContent = `$${(data.totalRevenue || 0).toLocaleString()}`;
            document.getElementById('avgRevenue').textContent = `$${(data.avgRevenue || 0).toFixed(2)}`;
            document.getElementById('growthRate').textContent = `${data.growthRate || 0}%`;
            document.getElementById('subscriptionRevenue').textContent = `$${(data.subscriptionRevenue || 0).toLocaleString()}`;

            // Update chart
            this.updateRevenueChart(data.chartData || []);
        } catch (error) {
            console.error('Error loading revenue analytics:', error);
        }
    }

    async loadApiAnalytics() {
        try {
            const response = await fetch('/admin/api/api-analytics');
            const data = await response.json();

            // Update stats
            document.getElementById('chatApiCalls').textContent = (data.chatApiCalls || 0).toLocaleString();
            document.getElementById('voiceApiCalls').textContent = (data.voiceApiCalls || 0).toLocaleString();
            document.getElementById('elevenLabsUsage').textContent = (data.elevenLabsUsage || 0).toLocaleString();
            document.getElementById('firebaseCalls').textContent = (data.firebaseCalls || 0).toLocaleString();
            document.getElementById('avgResponseTime').textContent = `${data.avgResponseTime || 0}ms`;

            // Update chart
            this.updateApiChart(data.chartData || []);
        } catch (error) {
            console.error('Error loading API analytics:', error);
        }
    }

    async loadPerformanceMetrics() {
        try {
            const response = await fetch('/admin/api/performance-metrics');
            const data = await response.json();

            // Update stats
            document.getElementById('serverUptime').textContent = data.serverUptime || '0h 0m';
            document.getElementById('dbLoad').textContent = `${data.dbLoad || 0}%`;
            document.getElementById('memoryUsage').textContent = `${data.memoryUsage || 0}%`;
            document.getElementById('activeConnections').textContent = data.activeConnections || '0';

            // Update last reload time
            document.getElementById('lastReload').textContent = `Last updated: ${new Date().toLocaleTimeString()}`;
        } catch (error) {
            console.error('Error loading performance metrics:', error);
        }
    }

    async loadPersonas() {
        try {
            const response = await fetch('/admin/api/personas');
            const personas = await response.json();

            const grid = document.getElementById('personasGrid');
            grid.innerHTML = '';

            personas.forEach(persona => {
                const personaCard = this.createPersonaCard(persona);
                grid.appendChild(personaCard);
            });
        } catch (error) {
            console.error('Error loading personas:', error);
            this.showError('Failed to load personas');
        }
    }

    createPersonaCard(persona) {
        const card = document.createElement('div');
        card.className = 'persona-card';
        card.innerHTML = `
            <div class="persona-header">
                <div class="persona-avatar">
                    ${persona.avatar ? `<img src="${persona.avatar}" alt="${persona.name}">` : persona.name.charAt(0)}
                </div>
                <div class="persona-info">
                    <h4>${persona.name}</h4>
                    <span class="persona-status ${persona.active ? 'active' : 'inactive'}">
                        ${persona.active ? 'Active' : 'Inactive'}
                    </span>
                </div>
            </div>
            <div class="persona-description">
                ${persona.description}
            </div>
            <div class="persona-actions">
                <button class="btn btn-primary btn-sm" onclick="adminDashboard.editPersona(${persona.id})">
                    ✏️ Edit
                </button>
                <button class="btn btn-secondary btn-sm" onclick="adminDashboard.togglePersonaStatus(${persona.id}, ${!persona.active})">
                    ${persona.active ? '⏸️ Deactivate' : '▶️ Activate'}
                </button>
            </div>
        `;
        return card;
    }

    async loadSystemData() {
        await this.loadSystemLogs();
    }

    async loadSystemLogs() {
        try {
            const logLevel = document.getElementById('logLevel').value;
            const response = await fetch(`/admin/api/system-logs?level=${logLevel}`);
            const logs = await response.json();

            const logContent = document.getElementById('logContent');
            logContent.innerHTML = '';

            logs.forEach(log => {
                const logEntry = document.createElement('div');
                logEntry.className = 'log-entry';
                logEntry.innerHTML = `
                    <span class="log-time">${log.timestamp}</span>
                    <span class="log-level ${log.level}">${log.level.toUpperCase()}</span>
                    <span class="log-message">${log.message}</span>
                `;
                logContent.appendChild(logEntry);
            });
        } catch (error) {
            console.error('Error loading system logs:', error);
        }
    }

    // Chart update methods
    updateUserChart(data) {
        const ctx = document.getElementById('userChart').getContext('2d');
        
        if (this.charts.userChart) {
            this.charts.userChart.destroy();
        }

        this.charts.userChart = new Chart(ctx, {
            type: 'line',
            data: {
                labels: data.labels || [],
                datasets: [{
                    label: 'Active Users',
                    data: data.activeUsers || [],
                    borderColor: 'rgb(99, 102, 241)',
                    backgroundColor: 'rgba(99, 102, 241, 0.1)',
                    tension: 0.4
                }, {
                    label: 'New Registrations',
                    data: data.newUsers || [],
                    borderColor: 'rgb(34, 197, 94)',
                    backgroundColor: 'rgba(34, 197, 94, 0.1)',
                    tension: 0.4
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: {
                        beginAtZero: true
                    }
                }
            }
        });
    }

    updateRevenueChart(data) {
        const ctx = document.getElementById('revenueChart').getContext('2d');
        
        if (this.charts.revenueChart) {
            this.charts.revenueChart.destroy();
        }

        this.charts.revenueChart = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: data.labels || [],
                datasets: [{
                    label: 'Revenue',
                    data: data.revenue || [],
                    backgroundColor: 'rgba(99, 102, 241, 0.8)',
                    borderColor: 'rgb(99, 102, 241)',
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: {
                        beginAtZero: true,
                        ticks: {
                            callback: function(value) {
                                return '$' + value.toLocaleString();
                            }
                        }
                    }
                }
            }
        });
    }

    updateApiChart(data) {
        const ctx = document.getElementById('apiChart').getContext('2d');
        
        if (this.charts.apiChart) {
            this.charts.apiChart.destroy();
        }

        this.charts.apiChart = new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: ['Chat API', 'Voice API', '11Labs', 'Firebase'],
                datasets: [{
                    data: [
                        data.chatApi || 0,
                        data.voiceApi || 0,
                        data.elevenLabs || 0,
                        data.firebase || 0
                    ],
                    backgroundColor: [
                        'rgb(99, 102, 241)',
                        'rgb(34, 197, 94)',
                        'rgb(251, 191, 36)',
                        'rgb(239, 68, 68)'
                    ]
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false
            }
        });
    }

    // Persona management methods
    openCreatePersonaModal() {
        this.showModal('createPersonaModal');
    }

    async createPersona() {
        try {
            const formData = new FormData(document.getElementById('createPersonaForm'));
            const personaData = Object.fromEntries(formData.entries());
            personaData.active = document.getElementById('personaActive').checked;

            const response = await fetch('/admin/api/personas', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(personaData)
            });

            if (response.ok) {
                this.closeModal('createPersonaModal');
                this.loadPersonas();
                this.showSuccess('Persona created successfully');
                document.getElementById('createPersonaForm').reset();
            } else {
                const error = await response.json();
                this.showError(error.message || 'Failed to create persona');
            }
        } catch (error) {
            console.error('Error creating persona:', error);
            this.showError('Failed to create persona');
        }
    }

    async editPersona(personaId) {
        try {
            const response = await fetch(`/admin/api/personas/${personaId}`);
            const persona = await response.json();

            // Populate edit form
            document.getElementById('editPersonaId').value = persona.id;
            document.getElementById('editPersonaName').value = persona.name;
            document.getElementById('editPersonaDescription').value = persona.description;
            document.getElementById('editPersonaAvatar').value = persona.avatar || '';
            document.getElementById('editPersonaPersonality').value = persona.personality || '';
            document.getElementById('editPersonaVoice').value = persona.voice || 'default';
            document.getElementById('editPersonaActive').checked = persona.active;

            this.showModal('editPersonaModal');
        } catch (error) {
            console.error('Error loading persona for edit:', error);
            this.showError('Failed to load persona details');
        }
    }

    async updatePersona() {
        try {
            const personaId = document.getElementById('editPersonaId').value;
            const formData = new FormData(document.getElementById('editPersonaForm'));
            const personaData = Object.fromEntries(formData.entries());
            personaData.active = document.getElementById('editPersonaActive').checked;

            const response = await fetch(`/admin/api/personas/${personaId}`, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(personaData)
            });

            if (response.ok) {
                this.closeModal('editPersonaModal');
                this.loadPersonas();
                this.showSuccess('Persona updated successfully');
            } else {
                const error = await response.json();
                this.showError(error.message || 'Failed to update persona');
            }
        } catch (error) {
            console.error('Error updating persona:', error);
            this.showError('Failed to update persona');
        }
    }

    async deletePersona() {
        const personaId = document.getElementById('editPersonaId').value;
        
        if (!confirm('Are you sure you want to delete this persona? This action cannot be undone.')) {
            return;
        }

        try {
            const response = await fetch(`/admin/api/personas/${personaId}`, {
                method: 'DELETE'
            });

            if (response.ok) {
                this.closeModal('editPersonaModal');
                this.loadPersonas();
                this.showSuccess('Persona deleted successfully');
            } else {
                const error = await response.json();
                this.showError(error.message || 'Failed to delete persona');
            }
        } catch (error) {
            console.error('Error deleting persona:', error);
            this.showError('Failed to delete persona');
        }
    }

    async togglePersonaStatus(personaId, active) {
        try {
            const response = await fetch(`/admin/api/personas/${personaId}/status`, {
                method: 'PATCH',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ active })
            });

            if (response.ok) {
                this.loadPersonas();
                this.showSuccess(`Persona ${active ? 'activated' : 'deactivated'} successfully`);
            } else {
                const error = await response.json();
                this.showError(error.message || 'Failed to update persona status');
            }
        } catch (error) {
            console.error('Error updating persona status:', error);
            this.showError('Failed to update persona status');
        }
    }

    async reloadSystemMetrics() {
        const btn = document.getElementById('reloadMetrics');
        const originalText = btn.textContent;
        btn.textContent = '🔄 Reloading...';
        btn.disabled = true;

        try {
            await this.loadPerformanceMetrics();
            this.showSuccess('Metrics reloaded successfully');
        } catch (error) {
            this.showError('Failed to reload metrics');
        } finally {
            btn.textContent = originalText;
            btn.disabled = false;
        }
    }

    // Utility methods
    showModal(modalId) {
        document.getElementById(modalId).classList.add('show');
    }

    closeModal(modalId) {
        document.getElementById(modalId).classList.remove('show');
    }

    startAutoRefresh() {
        // Refresh dashboard summary every 30 seconds
        this.refreshInterval = setInterval(() => {
            this.loadDashboardSummary();
            if (this.currentTab === 'analytics') {
                this.loadPerformanceMetrics();
            }
        }, 30000);
    }

    showSuccess(message) {
        // Implement your success notification system
        console.log('Success:', message);
    }

    showError(message) {
        // Implement your error notification system
        console.error('Error:', message);
    }

    destroy() {
        if (this.refreshInterval) {
            clearInterval(this.refreshInterval);
        }
        
        // Destroy charts
        Object.values(this.charts).forEach(chart => {
            if (chart) chart.destroy();
        });
    }
}

// Initialize admin dashboard when DOM is loaded
let adminDashboard;
document.addEventListener('DOMContentLoaded', () => {
    adminDashboard = new AdminDashboard();
});

// Global functions for HTML onclick handlers
window.closeModal = function(modalId) {
    adminDashboard.closeModal(modalId);
};

// Export for module usage
if (typeof module !== 'undefined' && module.exports) {
    module.exports = AdminDashboard;
}