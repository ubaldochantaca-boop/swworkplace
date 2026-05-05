class TaskManager {
    constructor() {
        this.tasks = this.loadTasks();
        this.currentFilter = 'all';
        this.init();
    }

    init() {
        this.setupEventListeners();
        this.updateDate();
        this.render();
        this.updateStats();
    }

    setupEventListeners() {
        // Formulario de agregar tarea,
        document.getElementById('taskForm').addEventListener('submit', (e) => {
            e.preventDefault();
            this.addTask();
        });

        // Filtros
        document.querySelectorAll('.filter-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                this.setFilter(e.target.dataset.filter);
            });
        });

        // Botones de acción.
        document.getElementById('clearCompleted').addEventListener('click', () => {
            this.clearCompletedTasks();
        });

        document.getElementById('clearAll').addEventListener('click', () => {
            this.clearAllTasks();
        });

        // Delegación de eventos para evitar recrear listeners en cada render
        document.getElementById('taskList').addEventListener('click', (e) => {
            const checkbox = e.target.closest('.task-checkbox');
            if (checkbox) {
                this.toggleTask(checkbox.dataset.id);
                return;
            }

            const deleteBtn = e.target.closest('.task-delete');
            if (deleteBtn) {
                this.deleteTask(deleteBtn.dataset.id);
            }
        });
    }

    updateDate() {
        const dateElement = document.getElementById('currentDate');
        const options = {
            weekday: 'long',
            year: 'numeric',
            month: 'long',
            day: 'numeric'
        };
        const today = new Date();
        dateElement.textContent = today.toLocaleDateString('es-ES', options);
    }

    generateId() {
        if (window.crypto?.randomUUID) {
            return window.crypto.randomUUID();
        }

        return Date.now().toString(36) + Math.random().toString(36).slice(2);
    }

    addTask() {
        const input = document.getElementById('taskInput');
        const taskText = input.value.trim();

        if (taskText === '') return;

        const newTask = {
            id: this.generateId(),
            text: taskText,
            completed: false,
            createdAt: new Date().toISOString()
        };

        this.tasks.unshift(newTask);
        this.saveTasks();
        this.render();
        this.updateStats();

        input.value = '';
        input.focus();
    }

    toggleTask(id) {
        const task = this.tasks.find(t => t.id === id);
        if (task) {
            task.completed = !task.completed;
            this.saveTasks();
            this.render();
            this.updateStats();
        }
    }

    deleteTask(id) {
        this.tasks = this.tasks.filter(t => t.id !== id);
        this.saveTasks();
        this.render();
        this.updateStats();
    }

    setFilter(filter) {
        this.currentFilter = filter;

        // Actualizar botones activos
        document.querySelectorAll('.filter-btn').forEach(btn => {
            btn.classList.toggle('active', btn.dataset.filter === filter);
        });

        this.render();
    }

    getFilteredTasks() {
        switch (this.currentFilter) {
            case 'completed':
                return this.tasks.filter(t => t.completed);
            case 'pending':
                return this.tasks.filter(t => !t.completed);
            default:
                return this.tasks;
        }
    }

    formatTime(dateString) {
        const date = new Date(dateString);
        const now = new Date();
        const diffMs = now - date;
        const diffMins = Math.floor(diffMs / 60000);
        const diffHours = Math.floor(diffMs / 3600000);
        const diffDays = Math.floor(diffMs / 86400000);

        if (diffMins < 1) return 'Ahora';
        if (diffMins < 60) return `Hace ${diffMins} min`;
        if (diffHours < 24) return `Hace ${diffHours} h`;
        if (diffDays < 7) return `Hace ${diffDays} d`;

        return date.toLocaleDateString('es-ES', {
            day: 'numeric',
            month: 'short'
        });
    }

    render() {
        const taskList = document.getElementById('taskList');
        const emptyState = document.getElementById('emptyState');
        const filteredTasks = this.getFilteredTasks();

        if (filteredTasks.length === 0) {
            taskList.innerHTML = '';
            emptyState.style.display = 'block';

            // Mensaje personalizado según el filtro
            let message = '📝 No hay tareas aún. ¡Agrega tu primera tarea!';
            if (this.currentFilter === 'completed') {
                message = '✅ No hay tareas completadas aún';
            } else if (this.currentFilter === 'pending') {
                message = '⏳ No hay tareas pendientes';
            }
            emptyState.querySelector('p').textContent = message;
        } else {
            emptyState.style.display = 'none';
            taskList.innerHTML = filteredTasks.map(task => this.createTaskHTML(task)).join('');
        }
    }

    createTaskHTML(task) {
        return `
            <li class="task-item ${task.completed ? 'completed' : ''}">
                <div class="task-checkbox ${task.completed ? 'checked' : ''}" data-id="${task.id}"></div>
                <span class="task-text">${this.escapeHtml(task.text)}</span>
                <span class="task-time">${this.formatTime(task.createdAt)}</span>
                <button class="task-delete" data-id="${task.id}">Eliminar</button>
            </li>
        `;
    }

    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    updateStats() {
        const total = this.tasks.length;
        const completed = this.tasks.filter(t => t.completed).length;
        const pending = total - completed;

        document.getElementById('totalTasks').textContent = total;
        document.getElementById('completedTasks').textContent = completed;
        document.getElementById('pendingTasks').textContent = pending;
    }

    clearCompletedTasks() {
        if (this.tasks.filter(t => t.completed).length === 0) {
            this.showMessage('No hay tareas completadas para eliminar');
            return;
        }

        if (confirm('¿Estás seguro de que quieres eliminar todas las tareas completadas?')) {
            this.tasks = this.tasks.filter(t => !t.completed);
            this.saveTasks();
            this.render();
            this.updateStats();
            this.showMessage('Tareas completadas eliminadas');
        }
    }

    clearAllTasks() {
        if (this.tasks.length === 0) {
            this.showMessage('No hay tareas para eliminar');
            return;
        }

        if (confirm('¿Estás seguro de que quieres eliminar todas las tareas? Esta acción no se puede deshacer.')) {
            this.tasks = [];
            this.saveTasks();
            this.render();
            this.updateStats();
            this.showMessage('Todas las tareas han sido eliminadas');
        }
    }

    showMessage(message) {
        // Crear un toast temporal
        const toast = document.createElement('div');
        toast.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 15px 20px;
            border-radius: 10px;
            box-shadow: 0 5px 15px rgba(0,0,0,0.2);
            z-index: 1000;
            animation: slideIn 0.3s ease;
            max-width: 300px;
        `;
        toast.textContent = message;
        document.body.appendChild(toast);

        setTimeout(() => {
            toast.style.animation = 'slideOut 0.3s ease';
            setTimeout(() => {
                document.body.removeChild(toast);
            }, 300);
        }, 3000);
    }

    saveTasks() {
        localStorage.setItem('dailyTasks', JSON.stringify(this.tasks));
    }

    loadTasks() {
        const saved = localStorage.getItem('dailyTasks');
        if (!saved) return [];

        try {
            const parsedTasks = JSON.parse(saved);
            return Array.isArray(parsedTasks) ? parsedTasks : [];
        } catch {
            return [];
        }
    }
}

// Agregar animaciones CSS dinámicamente
const style = document.createElement('style');
style.textContent = `
    @keyframes slideOut {
        to {
            opacity: 0;
            transform: translateX(100%);
        }
    }
`;
document.head.appendChild(style);

// Inicializar la aplicación cuando el DOM esté listo
document.addEventListener('DOMContentLoaded', () => {
    window.taskManager = new TaskManager();
});

// Guardar tareas antes de cerrar la pestaña
window.addEventListener('beforeunload', () => {
    if (window.taskManager?.tasks.length > 0) {
        window.taskManager.saveTasks();
    }
});
