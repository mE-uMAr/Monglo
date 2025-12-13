// Monglo Table View - Interactive table functionality

class MongloTableView {
    constructor(collectionName) {
        this.collection = collectionName;
        this.currentPage = 1;
        this.perPage = 20;
        this.search = '';
        this.sort = '';
        this.selectedRows = new Set();

        this.init();
    }

    init() {
        this.setupEventListeners();
        this.setupKeyboardShortcuts();
    }

    setupEventListeners() {
        // Search input with debounce
        const searchInput = document.getElementById('search-input');
        if (searchInput) {
            let debounceTimer;
            searchInput.addEventListener('input', (e) => {
                clearTimeout(debounceTimer);
                debounceTimer = setTimeout(() => {
                    this.search = e.target.value;
                    this.reload();
                }, 300);
            });
        }

        // Row clicks
        document.querySelectorAll('.monglo-table tbody tr').forEach(row => {
            row.addEventListener('click', (e) => {
                if (!e.target.matches('input[type="checkbox"]') &&
                    !e.target.matches('button')) {
                    const id = row.dataset.id;
                    window.location.href = `${window.MONGLO_PREFIX}/${this.collection}/document/${id}`;
                }
            });
        });

        // Checkbox selection
        document.querySelectorAll('.row-checkbox').forEach(checkbox => {
            checkbox.addEventListener('change', (e) => {
                if (e.target.checked) {
                    this.selectedRows.add(e.target.value);
                } else {
                    this.selectedRows.delete(e.target.value);
                }
                this.updateBulkActions();
            });
        });
    }

    setupKeyboardShortcuts() {
        document.addEventListener('keydown', (e) => {
            // Ctrl+F or Cmd+F for search
            if ((e.ctrlKey || e.metaKey) && e.key === 'f') {
                e.preventDefault();
                document.getElementById('search-input')?.focus();
            }

            // Arrow keys for pagination
            if (e.key === 'ArrowLeft' && e.altKey) {
                this.previousPage();
            }
            if (e.key === 'ArrowRight' && e.altKey) {
                this.nextPage();
            }
        });
    }

    updateBulkActions() {
        const bulkBar = document.getElementById('bulk-actions-bar');
        if (this.selectedRows.size > 0) {
            if (!bulkBar) {
                this.showBulkActionsBar();
            }
        } else {
            bulkBar?.remove();
        }
    }

    showBulkActionsBar() {
        const bar = document.createElement('div');
        bar.id = 'bulk-actions-bar';
        bar.style.cssText = `
            position: fixed;
            bottom: 20px;
            left: 50%;
            transform: translateX(-50%);
            background: var(--gray-900);
            color: white;
            padding: var(--spacing-md) var(--spacing-xl);
            border-radius: var(--radius-lg);
            box-shadow: var(--shadow-xl);
            display: flex;
            gap: var(--spacing-md);
            align-items: center;
            z-index: 1000;
            animation: slideUp 0.3s ease-out;
        `;

        bar.innerHTML = `
            <span>${this.selectedRows.size} selected</span>
            <button class="monglo-btn monglo-btn-danger" onclick="tableView.bulkDelete()">
                Delete All
            </button>
            <button class="monglo-btn monglo-btn-secondary" onclick="tableView.clearSelection()">
                Clear
            </button>
        `;

        document.body.appendChild(bar);
    }

    async bulkDelete() {
        if (!confirm(`Delete ${this.selectedRows.size} documents?`)) return;

        try {
            const promises = Array.from(this.selectedRows).map(id =>
                fetch(`${window.MONGLO_PREFIX}/${this.collection}/${id}`, { method: 'DELETE' })
            );

            await Promise.all(promises);
            this.reload();
            this.clearSelection();
        } catch (error) {
            alert('Error deleting documents');
            console.error(error);
        }
    }

    clearSelection() {
        this.selectedRows.clear();
        document.querySelectorAll('.row-checkbox').forEach(cb => cb.checked = false);
        document.getElementById('bulk-actions-bar')?.remove();
    }

    reload() {
        const params = new URLSearchParams({
            page: this.currentPage,
            per_page: this.perPage,
            search: this.search,
            sort: this.sort
        });

        window.location.href = `?${params.toString()}`;
    }

    nextPage() {
        this.currentPage++;
        this.reload();
    }

    previousPage() {
        if (this.currentPage > 1) {
            this.currentPage--;
            this.reload();
        }
    }
}

// Add slide-up animation
const style = document.createElement('style');
style.textContent = `
    @keyframes slideUp {
        from {
            opacity: 0;
            transform: translate(-50%, 20px);
        }
        to {
            opacity: 1;
            transform: translate(-50%, 0);
        }
    }
`;
document.head.appendChild(style);

// Export for use in templates
window.MongloTableView = MongloTableView;

// Global delete function
window.deleteDocument = async function (collection, id) {
    if (!confirm('Are you sure you want to delete this document?')) return;

    try {
        const response = await fetch(`${window.MONGLO_PREFIX}/${collection}/${id}`, {
            method: 'DELETE'
        });

        if (response.ok) {
            window.location.reload();
        } else {
            const error = await response.text();
            alert('Error deleting document: ' + error);
        }
    } catch (error) {
        console.error('Delete error:', error);
        alert('Error: ' + error.message);
    }
};
