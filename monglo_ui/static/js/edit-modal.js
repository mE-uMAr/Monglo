/**
 * Edit Modal - Monglo Admin
 * Dynamic form-based document editing
 */

class EditModal {
  constructor() {
    this.modal = null;
    this.currentCollection = null;
    this.currentDocumentId = null;
    this.currentDocument = null;
  }

  async open(collection, documentId) {
    this.currentCollection = collection;
    this.currentDocumentId = documentId;

    // Fetch document data
    try {
      const response = await fetch(`/api/admin/${collection}/${documentId}`);
      const result = await response.json();
      this.currentDocument = result.document || result;

      this.createModal();
      this.populateForm();
    } catch (error) {
      alert('Error loading document: ' + error.message);
    }
  }

  createModal() {
    // Remove existing modal if any
    const existing = document.getElementById('edit-modal');
    if (existing) existing.remove();

    const modal = document.createElement('div');
    modal.id = 'edit-modal';
    modal.style.cssText = `
      position: fixed;
      top: 0;
      left: 0;
      right: 0;
      bottom: 0;
      background: rgba(0, 0, 0, 0.6);
      display: flex;
      align-items: center;
      justify-content: center;
      z-index: 9999;
      animation: fadeIn 0.2s ease-out;
    `;

    modal.innerHTML = `
      <div style="
        background: var(--bg-primary);
        border-radius: var(--radius-lg);
        box-shadow: var(--shadow-xl);
        max-width: 600px;
        width: 90%;
        max-height: 80vh;
        overflow: hidden;
        display: flex;
        flex-direction: column;
      ">
        <div style="
          padding: var(--spacing-lg) var(--spacing-xl);
          border-bottom: 1px solid var(--border-color);
          display: flex;
          justify-content: space-between;
          align-items: center;
        ">
          <h2 style="margin: 0; color: var(--text-primary); font-size: var(--font-size-xl);">
            <i class="fas fa-edit"></i> Edit Document
          </h2>
          <button onclick="editModal.close()" class="monglo-btn monglo-btn-secondary monglo-btn-sm">
            <i class="fas fa-times"></i>
          </button>
        </div>
        
        <div id="edit-form-container" style="
          padding: var(--spacing-xl);
          overflow-y: auto;
          flex: 1;
        "></div>
        
        <div style="
          padding: var(--spacing-lg) var(--spacing-xl);
          border-top: 1px solid var(--border-color);
          display: flex;
          gap: var(--spacing-md);
          justify-content: flex-end;
        ">
          <button onclick="editModal.close()" class="monglo-btn monglo-btn-secondary">
            Cancel
          </button>
          <button onclick="editModal.save()" class="monglo-btn monglo-btn-primary">
            <i class="fas fa-save"></i> Save Changes
          </button>
        </div>
      </div>
    `;

    document.body.appendChild(modal);
    this.modal = modal;

    // Close on backdrop click
    modal.addEventListener('click', (e) => {
      if (e.target === modal) this.close();
    });
  }

  populateForm() {
    const container = document.getElementById('edit-form-container');
    if (!container || !this.currentDocument) return;

    let formHtml = '';

    // Generate fields for each property except _id
    for (const [key, value] of Object.entries(this.currentDocument)) {
      if (key === '_id') continue; // Skip _id (read-only)

      const fieldType = this.detectFieldType(value);
      formHtml += this.generateField(key, value, fieldType);
    }

    container.innerHTML = formHtml;
  }

  detectFieldType(value) {
    if (value === null) return 'text';
    if (typeof value === 'boolean') return 'checkbox';
    if (typeof value === 'number') return 'number';
    if (typeof value === 'object') return 'json';
    if (typeof value === 'string' && value.includes('T') && !isNaN(Date.parse(value))) {
      return 'datetime-local';
    }
    return 'text';
  }

  generateField(key, value, type) {
    let displayValue = type === 'json' ? JSON.stringify(value, null, 2) : value;

    // Format datetime for datetime-local input (requires YYYY-MM-DDTHH:mm format)
    if (type === 'datetime-local' && displayValue) {
      // Convert ISO string (2025-12-13T00:19:34.272000) to datetime-local format (2025-12-13T00:19)
      displayValue = displayValue.substring(0, 16);
    }

    const checked = type === 'checkbox' && value ? 'checked' : '';

    return `
      <div style="margin-bottom: var(--spacing-lg);">
        <label style="
          display: block;
          font-weight: 600;
          margin-bottom: var(--spacing-sm);
          color: var(--text-primary);
          font-size: var(--font-size-sm);
        ">
          ${key}
        </label>
        ${type === 'checkbox' ? `
          <input 
            type="checkbox" 
            name="${key}" 
            ${checked}
            style="width: 20px; height: 20px; cursor: pointer;"
          />
        ` : type === 'json' ? `
          <textarea 
            name="${key}" 
            class="monglo-input"
            rows="5"
            style="font-family: var(--font-mono); font-size: var(--font-size-sm);"
          >${displayValue}</textarea>
        ` : `
          <input 
            type="${type}" 
            name="${key}" 
            value="${displayValue || ''}"
            class="monglo-input"
          />
        `}
      </div>
    `;
  }

  async save() {
    const container = document.getElementById('edit-form-container');
    if (!container) return;

    // Collect form data
    const formData = {};
    const inputs = container.querySelectorAll('input, textarea');

    inputs.forEach(input => {
      const key = input.name;
      let value = input.type === 'checkbox' ? input.checked : input.value;

      // Try to parse JSON fields
      if (input.tagName === 'TEXTAREA') {
        try {
          value = JSON.parse(value);
        } catch (e) {
          // Keep as string if not valid JSON
        }
      } else if (input.type === 'number') {
        value = parseFloat(value);
      }

      formData[key] = value;
    });

    // Update document
    try {
      const response = await fetch(`/api/admin/${this.currentCollection}/${this.currentDocumentId}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(formData)
      });

      if (response.ok) {
        this.close();
        window.location.reload(); // Reload to show changes
      } else {
        alert('Error updating document');
      }
    } catch (error) {
      alert('Error: ' + error.message);
    }
  }

  close() {
    if (this.modal) {
      this.modal.remove();
      this.modal = null;
    }
  }
}

// Global instance
window.editModal = new EditModal();

// Global function to open edit modal
window.editDocument = function (id) {
  const collection = window.location.pathname.split('/')[2];
  window.editModal.open(collection, id);
};
