# This module contains the OrderTracker class, which encapsulates the core
# business logic for managing orders.
from .errors import StatusError, OrderIDError

class OrderTracker:
    """
    Manages customer orders, providing functionalities to add, update,
    and retrieve order information.
    """
    def __init__(self, storage):
        required_methods = ['save_order', 'get_order', 'get_all_orders']
        for method in required_methods:
            if not hasattr(storage, method) or not callable(getattr(storage, method)):
                raise TypeError(f"Storage object must implement a callable '{method}' method.")
        self.storage = storage

    def add_order(self, order_id: str, item_name: str, quantity: int, customer_id: str, status: str = "pending"):
        if not isinstance(order_id, str) or not order_id.strip():
            raise OrderIDError()
        
        if not isinstance(item_name, str) or not item_name.strip():
            raise ValueError("Item name must be a non-empty string.")

        if not isinstance(quantity, int) or quantity <= 0:
            raise ValueError("Quantity must be a positive integer.")

        if not isinstance(customer_id, str) or not customer_id.strip():
            raise ValueError("Customer ID must be a non-empty string.")

        if status not in ["pending", "shipped", "completed", "cancelled"]:
            raise StatusError()

        if order_id in self.storage.get_all_orders():
            raise ValueError(f"Order with ID '{order_id}' already exists.")

        order_data = {
            'order_id': order_id,
            'item_name': item_name,
            'quantity': quantity,
            'customer_id': customer_id,
            'status': status
        }
        self.storage.save_order(order_id, order_data)

    def get_order_by_id(self, order_id: str):
        if not isinstance(order_id, str) or not order_id.strip():
            raise OrderIDError()

        order = self.storage.get_order(order_id)
        if not order:
            raise ValueError(f"Order with ID '{order_id}' not found.")

        return order

    def update_order_status(self, order_id: str, new_status: str):
        order = self.get_order_by_id(order_id)
        if new_status not in ["pending", "shipped", "completed", "cancelled"]:
            raise StatusError()

        order['status'] = new_status
        self.storage.save_order(order_id, order)

    def list_all_orders(self):
        return self.storage.get_all_orders()

    def list_orders_by_status(self, status: str):
        all_orders = self.storage.get_all_orders()
        return {order_id: order for order_id, order in all_orders.items() if order.get('status') == status}

    def delete_order(self, order_id: str):
        order = self.get_order_by_id(order_id)
        self.storage.delete_order(order_id)
