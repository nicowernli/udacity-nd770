import pytest
from unittest.mock import Mock
from contextlib import nullcontext as does_not_raise
from ..order_tracker import OrderTracker

# --- Fixtures for Unit Tests ---

@pytest.fixture
def mock_storage():
    """
    Provides a mock storage object for tests.
    This mock will be configured to simulate various storage behaviors.
    """
    mock = Mock()
    # By default, mock get_order to return None (no order found)
    mock.get_order.return_value = None
    # By default, mock get_all_orders to return an empty dict
    mock.get_all_orders.return_value = {}
    return mock

@pytest.fixture
def order_tracker(mock_storage):
    """
    Provides an OrderTracker instance initialized with the mock_storage.
    """
    return OrderTracker(mock_storage)

def test_order_tracker_list_all_orders(order_tracker, mock_storage):
    # Arrange
    mock_storage.get_all_orders.return_value = {
        'order1': {'id': 'order1', 'status': 'pending'},
        'order2': {'id': 'order2', 'status': 'completed'}
    }

    # Act
    orders = order_tracker.list_all_orders()

    # Assert
    assert len(orders) == 2
    assert orders['order1']['status'] == 'pending'
    assert orders['order2']['status'] == 'completed'

def test_order_tracker_list_all_orders_empty(order_tracker, mock_storage):
    # Arrange
    mock_storage.get_all_orders.return_value = {}

    # Act
    orders = order_tracker.list_all_orders()

    # Assert
    assert isinstance(orders, dict)
    assert len(orders) == 0

def test_order_tracker_list_all_orders_storage_error(order_tracker, mock_storage):
    # Arrange
    mock_storage.get_all_orders.side_effect = Exception("Storage error")

    # Act & Assert
    with pytest.raises(Exception) as exc_info:
        order_tracker.list_all_orders()
    assert str(exc_info.value) == "Storage error"

@pytest.mark.parametrize("status, expected_count", [
    ('pending', 2),
    ('completed', 1),
    ('cancelled', 0)
])
def test_order_tracker_list_all_orders_by_status(order_tracker, mock_storage, status, expected_count):
    # Arrange
    mock_storage.get_all_orders.return_value = {
        'order1': {'id': 'order1', 'status': 'pending'},
        'order2': {'id': 'order2', 'status': 'completed'},
        'order3': {'id': 'order3', 'status': 'pending'}
    }

    # Act
    orders = order_tracker.list_orders_by_status(status)

    # Assert
    assert len(orders) == expected_count
    assert all(order['status'] == status for order in orders.values())

def test_order_tracker_list_all_orders_by_status_no_orders(order_tracker, mock_storage):
    # Arrange
    mock_storage.get_all_orders.return_value = {}

    # Act
    orders = order_tracker.list_orders_by_status('pending')

    # Assert
    assert isinstance(orders, dict)
    assert len(orders) == 0

def test_order_tracker_add_order(order_tracker, mock_storage):
    # Arrange
    order_id = 'order1'
    item_name = 'Widget'
    quantity = 3
    customer_id = 'customer1'
    status = 'pending'

    # Act
    order_tracker.add_order(order_id, item_name, quantity, customer_id, status)

    # Assert
    mock_storage.save_order.assert_called_once_with(order_id, {
        'order_id': order_id,
        'item_name': item_name,
        'quantity': quantity,
        'customer_id': customer_id,
        'status': status
    })

    assert order_tracker.list_all_orders() == mock_storage.get_all_orders.return_value

@pytest.mark.parametrize("item_name, status, quantity, expectation", [
    ('', 'pending', 5, pytest.raises(ValueError, match="Item name must be a non-empty string.")),
    ('Widget', 'pending', -1, pytest.raises(ValueError, match="Quantity must be a positive integer.")),
    ('Widget', 'invalid', 5, pytest.raises(ValueError, match="Status must be one of: 'pending', 'shipped', 'completed', 'cancelled'."))
])
def test_order_tracker_add_order_value_error(order_tracker, mock_storage, item_name, status, quantity, expectation):
    # Arrange
    order_id = 'order1'
    item_name = item_name
    quantity = quantity
    customer_id = 'customer1'
    status = status

    # Act & Assert
    with expectation as exc_info: 
        order_tracker.add_order(order_id, item_name, quantity, customer_id, status)

    assert str(exc_info.value) in [
        "Item name must be a non-empty string.",
        "Quantity must be a positive integer.",
        "Status must be one of: 'pending', 'shipped', 'completed', 'cancelled'."
    ]

    assert mock_storage.save_order.call_count == 0
        
def test_order_tracker_add_order_duplicate_id(order_tracker, mock_storage):
    # Arrange
    order_id = 'order1'
    item_name = 'Widget'
    quantity = 3
    customer_id = 'customer1'
    status = 'pending'

    mock_storage.get_all_orders.return_value = {
        order_id: {'id': order_id, 'status': status}
    }

    # Act & Assert
    with pytest.raises(ValueError) as exc_info:
        order_tracker.add_order(order_id, item_name, quantity, customer_id, status)

    assert str(exc_info.value) == f"Order with ID '{order_id}' already exists."
    assert mock_storage.save_order.call_count == 0

def test_order_tracker_get_order_by_id(order_tracker, mock_storage):
    # Arrange
    order_id = 'order1'
    expected_order = {'id': order_id, 'status': 'pending'}
    mock_storage.get_order.return_value = expected_order

    # Act
    order = order_tracker.get_order_by_id(order_id)

    # Assert
    assert order == expected_order

@pytest.mark.parametrize("order_id, expectation", [
    ('', pytest.raises(ValueError, match="Order ID must be a non-empty string.")),
    ('   ', pytest.raises(ValueError, match="Order ID must be a non-empty string.")),
    ('nonexistent_order', pytest.raises(ValueError, match="Order with ID 'nonexistent_order' not found."))
])
def test_order_tracker_get_order_by_id_not_found(order_tracker, mock_storage, order_id, expectation):
    # Arrange
    order_id = order_id
    mock_storage.get_order.return_value = None

    # Act
    with expectation as exc_info:
        order = order_tracker.get_order_by_id(order_id)

    # Assert
    assert str(exc_info.value) in [
        "Order ID must be a non-empty string.",
        f"Order with ID '{order_id}' not found."
    ]

def test_order_tracker_update_order_status(order_tracker, mock_storage):
    # Arrange
    order_id = 'order1'
    new_status = 'completed'
    existing_order = {'id': order_id, 'status': 'pending'}
    mock_storage.get_order.return_value = existing_order

    # Act
    order_tracker.update_order_status(order_id, new_status)

    # Assert
    mock_storage.get_order.assert_called_once_with(order_id)
    updated_order = existing_order.copy()
    updated_order['status'] = new_status
    mock_storage.save_order.assert_called_once_with(order_id, updated_order)

@pytest.mark.parametrize("order_id, new_status, expectation", [
    ('order1', 'invalid', pytest.raises(ValueError, match="Status must be one of: 'pending', 'shipped', 'completed', 'cancelled'.")),
    ('invalid', 'completed', pytest.raises(ValueError, match="Order with ID 'invalid' not found.")),
])
def test_order_tracker_update_order_status_invalid_status(order_tracker, mock_storage, order_id, new_status, expectation):
    # Arrange
    existing_order = {'id': 'order1', 'status': 'pending'}
    if order_id == 'invalid':
        mock_storage.get_order.return_value = None
    else:
        mock_storage.get_order.return_value = existing_order

    # Act & Assert
    with expectation as exc_info:
        order_tracker.update_order_status(order_id, new_status)

    assert str(exc_info.value) in [
        "Status must be one of: 'pending', 'shipped', 'completed', 'cancelled'.",
        f"Order with ID '{order_id}' not found."
    ]
    assert mock_storage.save_order.call_count == 0

def test_order_tracker_delete_order(order_tracker, mock_storage):
    # Arrange
    order_id = 'order1'
    existing_order = {'id': order_id, 'status': 'pending'}
    mock_storage.get_order.return_value = existing_order

    # Act
    order_tracker.delete_order(order_id)

    # Assert
    mock_storage.get_order.assert_called_once_with(order_id)
    mock_storage.delete_order.assert_called_once_with(order_id)

def test_order_tracker_delete_order_not_found(order_tracker, mock_storage):
    # Arrange
    order_id = 'nonexistent_order'
    mock_storage.get_order.return_value = None

    # Act
    with pytest.raises(ValueError) as exc_info:
        order_tracker.delete_order(order_id)

    # Assert
    assert str(exc_info.value) == f"Order with ID '{order_id}' not found."