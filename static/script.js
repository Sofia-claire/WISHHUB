document.addEventListener('DOMContentLoaded', function() {
    updateItemCount();

    if (!editable) {
        document.getElementById('add-manual-btn').disabled = true;
    }

    const manualBtn = document.getElementById('add-manual-btn');
    if (manualBtn) {
        manualBtn.addEventListener('click', function() {
            if (!editable) return;

            const name = document.getElementById('manual-name').value.trim();
            const price = document.getElementById('manual-price').value.trim();
            const image = document.getElementById('manual-image').value.trim();
            const url = document.getElementById('manual-url').value.trim();
            const description = document.getElementById('manual-description').value.trim();

            if (!name || !price) {
                showNotification('Введите название и цену', 'error');
                return;
            }

            // Валидация цены
            if (!/^\d+(\s?\d+)*\s?₽?$/.test(price)) {
                showNotification('Некорректная цена', 'error');
                return;
            }

            // Валидация ссылок
            const urlPattern = /^(https?:\/\/[^\s]+)$/;
            if (image && !urlPattern.test(image)) {
                showNotification('Некорректная ссылка на изображение', 'error');
                return;
            }
            if (url && !urlPattern.test(url)) {
                showNotification('Некорректная ссылка на товар', 'error');
                return;
            }

            const payload = { name, price, image, source_url: url, description };
            const editUrl = window.location.pathname + window.location.search;

            fetch(editUrl, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            })
            .then(res => res.json())
            .then(data => {
                if (data.success) {
                    addItemToTable(data.item);
                    showNotification('Товар добавлен', 'success');
                    document.getElementById('manual-name').value = '';
                    document.getElementById('manual-price').value = '';
                    document.getElementById('manual-image').value = '';
                    document.getElementById('manual-url').value = '';
                    document.getElementById('manual-description').value = '';
                } else {
                    showNotification(data.error || 'Ошибка при добавлении', 'error');
                }
            })
            .catch(() => showNotification('Ошибка при добавлении', 'error'));
        });
    }
});

function deleteItem(id) {
    if (!editable) return;

    // Формируем правильный URL для удаления
    const pathnameParts = window.location.pathname.split('/');
    const wishlistId = pathnameParts[2]; // /wishlist/1/edit => wishlistId = 1
    const key = new URLSearchParams(window.location.search).get('key');
    const deleteUrl = `/wishlist/${wishlistId}/delete/${id}?key=${key}`;

    fetch(deleteUrl, { method: 'DELETE' })
        .then(res => res.json())
        .then(data => {
            if (data.success) {
                const row = document.getElementById(`item-${id}`);
                if (row) row.remove();
                updateItemCount();
                showNotification('Товар удалён', 'success');
            } else showNotification('Ошибка при удалении', 'error');
        })
        .catch(() => showNotification('Ошибка при удалении', 'error'));
}

function addItemToTable(item) {
    const tbody = document.getElementById('table-body');
    document.getElementById('wishlist-table').style.display = '';
    document.getElementById('empty-state').style.display = 'none';

    const tr = document.createElement('tr');
    tr.id = `item-${item.id}`;
    tr.innerHTML = `
        <td>${item.image ? `<img src="${item.image}" alt="${item.name}" class="item-image">`
                           : `<div class="item-image placeholder"><i class="fas fa-gift"></i></div>`}</td>
        <td>
            <div class="item-name">${item.name}</div>
            ${item.description ? `<div class="item-description">${item.description}</div>` : ''}
            ${item.source_url ? `<div class="item-link"><a href="${item.source_url}" target="_blank"><i class="fas fa-external-link-alt"></i> Ссылка на товар</a></div>` : ''}
            <div class="item-status"><span class="status-badge status-manual">Вручную</span></div>
        </td>
        <td>${item.price}</td>
        <td>${item.added_date}</td>
        <td>${editable ? `<div class="item-actions">
                <button class="btn btn-danger" onclick="deleteItem(${item.id})">
                    <i class="fas fa-trash"></i>
                </button></div>` : ''}</td>
    `;
    tbody.appendChild(tr);
    updateItemCount();
}

function clearAll() {
    if (!editable) return;
    document.querySelectorAll('#table-body tr').forEach(row => row.remove());
    updateItemCount();
    showNotification('Список очищен', 'success');
}

function updateItemCount() {
    const count = document.querySelectorAll('#table-body tr').length;
    document.getElementById('item-count').textContent = `(${count} товаров)`;
}

function showNotification(msg, type='success') {
    const n = document.getElementById('notification');
    n.textContent = msg;
    n.className = `notification ${type} show`;
    setTimeout(() => n.classList.remove('show'), 3000);
}
