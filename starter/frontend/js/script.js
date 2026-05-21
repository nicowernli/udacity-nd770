document.addEventListener('DOMContentLoaded', () => {
    const messageContainer = document.getElementById('message-container');
    const addOrderForm = document.getElementById('add-order-form');
    const getOrderForm = document.getElementById('get-order-form');
    const singleOrderDetails = document.getElementById('single-order-details');
    const updateStatusForm = document.getElementById('update-status-form');
    const listAllOrdersBtn = document.getElementById('list-all-orders-btn');
    const filterStatusSelect = document.getElementById('filter-status');
    const ordersTableBody = document.getElementById('orders-table-body');

    function showMessage(message, type) {
        messageContainer.textContent = message;
        messageContainer.className = `message-box ${type === 'success' ? 'message-success' : 'message-error'}`;
        messageContainer.classList.remove('hidden');
        setTimeout(() => messageContainer.classList.add('hidden'), 5000);
    }

    function renderOrdersTable(orders) {
        ordersTableBody.innerHTML = '';
        if (orders.length === 0) {
            ordersTableBody.innerHTML = '<tr><td colspan="5" class="text-center py-4">No orders to display.</td></tr>';
            return;
        }
        orders.forEach(order => {
            const row = document.createElement('tr');
            row.innerHTML = `
                <td class="p-2">${order.order_id}</td>
                <td class="p-2">${order.item_name}</td>
                <td class="p-2">${order.quantity}</td>
                <td class="p-2">${order.customer_id}</td>
                <td class="p-2 capitalize">${order.status}</td>
                <td class="p-2 text-red-500">
                    <button class="delete-btn" data-id="${order.order_id}" title="Delete Order">
                    <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="size-6">
                        <path stroke-linecap="round" stroke-linejoin="round" d="m14.74 9-.346 9m-4.788 0L9.26 9m9.968-3.21c.342.052.682.107 1.022.166m-1.022-.165L18.16 19.673a2.25 2.25 0 0 1-2.244 2.077H8.084a2.25 2.25 0 0 1-2.244-2.077L4.772 5.79m14.456 0a48.108 48.108 0 0 0-3.478-.397m-12 .562c.34-.059.68-.114 1.022-.165m0 0a48.11 48.11 0 0 1 3.478-.397m7.5 0v-.916c0-1.18-.91-2.164-2.09-2.201a51.964 51.964 0 0 0-3.32 0c-1.18.037-2.09 1.022-2.09 2.201v.916m7.5 0a48.667 48.667 0 0 0-7.5 0" />
                    </svg>
                    </button>
                </td>
            `;
            ordersTableBody.appendChild(row);

            row.querySelector('.delete-btn').addEventListener('click', async (e) => {
                const button = e.currentTarget.closest('.delete-btn');
                const orderId = button.getAttribute('data-id');
                if (confirm(`Are you sure you want to delete order ${orderId}?`)) {
                    try {
                        const response = await fetch(`/api/orders/${orderId}`, { method: 'DELETE' });
                        if (!response.ok) throw new Error('Failed to delete order');
                        showMessage(`Order ${orderId} deleted.`, 'success');
                        fetchAndRenderOrders();
                    } catch (error) { showMessage(`Error deleting order: ${error.message}`, 'error'); }
                }
            });
        });
    }

    async function fetchAndRenderOrders(status = '') {
        try {
            const url = status ? `/api/orders?status=${status}` : '/api/orders';
            const response = await fetch(url);
            const orders = await response.json();
            if (!response.ok) throw new Error(orders.error || 'Unknown error');
            renderOrdersTable(orders);
        } catch (error) { showMessage(`Failed to load orders: ${error.message}`, 'error'); renderOrdersTable([]); }
    }

    addOrderForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const formData = new FormData(addOrderForm);
        const orderData = Object.fromEntries(formData.entries());
        orderData.quantity = parseInt(orderData.quantity);
        try {
            const response = await fetch('/api/orders', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(orderData) });
            const result = await response.json();
            if (!response.ok) throw new Error(result.error);
            showMessage(`Order ${result.order_id} added!`, 'success');
            addOrderForm.reset();
            fetchAndRenderOrders();
        } catch (error) { showMessage(`Failed to add order: ${error.message}`, 'error'); }
    });

    getOrderForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const orderId = document.getElementById('get-order-id').value.trim();
        singleOrderDetails.classList.add('hidden');
        if (!orderId) { showMessage('Please enter an Order ID.', 'error'); return; }
        try {
            const response = await fetch(`/api/orders/${orderId}`);
            const order = await response.json();
            if (!response.ok) throw new Error(order.error);
            singleOrderDetails.querySelector('pre').textContent = JSON.stringify(order, null, 2);
            singleOrderDetails.classList.remove('hidden');
        } catch (error) { showMessage(`Failed to get order: ${error.message}`, 'error'); }
    });

    updateStatusForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const orderId = document.getElementById('update-order-id').value.trim();
        const newStatus = document.getElementById('update-new-status').value;
        if (!orderId || !newStatus) { showMessage('Please enter an Order ID and select a new status.', 'error'); return; }
        try {
            const response = await fetch(`/api/orders/${orderId}/status`, { method: 'PUT', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ new_status: newStatus }) });
            const result = await response.json();
            if (!response.ok) throw new Error(result.error);
            showMessage(`Order ${orderId} status updated.`, 'success');
            updateStatusForm.reset();
            fetchAndRenderOrders();
        } catch (error) { showMessage(`Failed to update status: ${error.message}`, 'error'); }
    });



    listAllOrdersBtn.addEventListener('click', () => { filterStatusSelect.value = ''; fetchAndRenderOrders(); });
    filterStatusSelect.addEventListener('change', (e) => fetchAndRenderOrders(e.target.value));
    fetchAndRenderOrders();
});
