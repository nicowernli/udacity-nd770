class StatusError(ValueError):
    """Custom exception for invalid order status."""
    def __init__(self, message="Status must be one of: 'pending', 'shipped', 'completed', 'cancelled'.", status_code=400, response=None):
        super().__init__(message)
        self.response = response

class OrderIDError(ValueError):
    """Custom exception for invalid order ID."""
    def __init__(self, message="Order ID must be a non-empty string.", status_code=400, response=None):
        super().__init__(message)
        self.response = response