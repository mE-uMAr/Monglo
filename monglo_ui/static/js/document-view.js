// Monglo Document View - Interactive document editing

class MongloDocumentView {
    constructor(collectionName, documentId) {
        this.collection = collectionName;
        this.documentId = documentId;
        this.editMode = false;
        this.originalData = null;

        this.init();
    }

    init() {
        this.setupTreeNavigation();
        this.setupCopyButtons();
    }

    setupTreeNavigation() {
        // Make nested objects collapsible
        document.querySelectorAll('.monglo-tree-node').forEach(node => {
            const hasChildren = node.querySelector('.monglo-tree-node');
            if (hasChildren) {
                const toggle = document.createElement('span');
                toggle.textContent = '▼ ';
                toggle.style.cursor = 'pointer';
                toggle.style.color = 'var(--gray-400)';
                toggle.style.marginRight = 'var(--spacing-xs)';

                toggle.addEventListener('click', () => {
                    const children = node.querySelectorAll(':scope > .monglo-tree-node');
                    children.forEach(child => {
                        child.style.display = child.style.display === 'none' ? 'block' : 'none';
                    });
                    toggle.textContent = toggle.textContent === '▼ ' ? '▶ ' : '▼ ';
                });

                node.insertBefore(toggle, node.firstChild);
            }
        });
    }

    setupCopyButtons() {
        // Add copy buttons to values
        document.querySelectorAll('.monglo-tree-value').forEach(value => {
            if (!value.dataset.copyEnabled) {
                value.style.position = 'relative';
                value.addEventListener('mouseenter', () => this.showCopyButton(value));
                value.dataset.copyEnabled = 'true';
            }
        });
    }

    showCopyButton(element) {
        const existing = element.querySelector('.copy-btn');
        if (existing) return;

        const btn = document.createElement('button');
        btn.className = 'copy-btn';
        btn.innerHTML = '📋';
        btn.style.cssText = `
            position: absolute;
            right: -25px;
            top: 50%;
            transform: translateY(-50%);
            background: var(--gray-700);
            color: white;
            border: none;
            border-radius: var(--radius-sm);
            padding: 2px 6px;
            cursor: pointer;
            font-size: 0.75rem;
            opacity: 0.8;
        `;

        btn.addEventListener('click', (e) => {
            e.stopPropagation();
            navigator.clipboard.writeText(element.textContent);
            btn.innerHTML = '✓';
            setTimeout(() => btn.innerHTML = '📋', 1000);
        });

        element.appendChild(btn);

        element.addEventListener('mouseleave', () => {
            setTimeout(() => btn.remove(), 200);
        });
    }

    async enterEditMode() {
        this.editMode = true;
        this.originalData = this.getCurrentData();

        // Convert tree to form
        const docTree = document.querySelector('.monglo-document-tree');
        const form = this.createEditForm(this.originalData);

        docTree.innerHTML = '';
        docTree.appendChild(form);

        // Update header buttons
        this.updateHeaderButtons();
    }

    createEditForm(data, prefix = '') {
        const form = document.createElement('div');
        form.className = 'monglo-edit-form';

        Object.entries(data).forEach(([key, value]) => {
            const fieldPath = prefix ? `${prefix}.${key}` : key;
            const field = this.createField(key, value, fieldPath);
            form.appendChild(field);
        });

        return form;
    }

    createField(key, value, path) {
        const field = document.createElement('div');
        field.style.marginBottom = 'var(--spacing-md)';

        const label = document.createElement('label');
        label.textContent = key;
        label.style.display = 'block';
        label.style.fontWeight = '600';
        label.style.marginBottom = 'var(--spacing-xs)';
        field.appendChild(label);

        let input;

        if (typeof value === 'object' && value !== null) {
            input = document.createElement('textarea');
            input.value = JSON.stringify(value, null, 2);
            input.rows = 5;
        } else if (typeof value === 'boolean') {
            input = document.createElement('input');
            input.type = 'checkbox';
            input.checked = value;
        } else if (typeof value === 'number') {
            input = document.createElement('input');
            input.type = 'number';
            input.value = value;
        } else {
            input = document.createElement('input');
            input.type = 'text';
            input.value = value || '';
        }

        input.className = 'monglo-input';
        input.dataset.path = path;
        field.appendChild(input);

        return field;
    }

    getCurrentData() {
        // Extract data from DOM (simplified)
        return {}; // Would parse from tree structure
    }

    updateHeaderButtons() {
        const actions = document.querySelector('.monglo-actions');
        if (this.editMode) {
            actions.innerHTML = `
                <button class="monglo-btn monglo-btn-primary" onclick="docView.saveChanges()">
                    Save Changes
                </button>
                <button class="monglo-btn monglo-btn-secondary" onclick="docView.cancelEdit()">
                    Cancel
                </button>
            `;
        }
    }

    async saveChanges() {
        // Collect form data
        const formData = {};
        document.querySelectorAll('[data-path]').forEach(input => {
            const path = input.dataset.path;
            let value = input.value;

            if (input.type === 'checkbox') {
                value = input.checked;
            } else if (input.type === 'number') {
                value = parseFloat(value);
            }

            formData[path] = value;
        });

        try {
            const response = await fetch(`${window.MONGLO_PREFIX}/${this.collection}/${this.documentId}`, {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(formData)
            });

            if (response.ok) {
                window.location.reload();
            } else {
                alert('Error saving changes');
            }
        } catch (error) {
            alert('Error saving changes');
            console.error(error);
        }
    }

    cancelEdit() {
        window.location.reload();
    }
}

// Export
window.MongloDocumentView = MongloDocumentView;
