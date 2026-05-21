# Udatracker Starter Code

This directory contains the starter code for the Udatracker project. The initial structure of directories and files is described below.

```
.
├── backend
│   ├── __init__.py
│   ├── app.py
│   ├── in_memory_storage.py
│   ├── order_tracker.py
│   ├── requirements.txt
│   └── tests
│       ├── __init__.py
│       ├── test_api.py
│       └── test_order_tracker.py
├── frontend
│   ├── css
│   │   └── style.css
│   ├── index.html
│   └── js
│       └── script.js
├── pytest.ini
└── README.md
```

# Design decision

I decided to store orders as dictionary and return them as list. The idea behind it faster access to stored orders using the `order_id` and then
returning a standar list when requesting a list of orders.

Also decided to created custom errors to avoid duplicating some validation errors around the app.

# Testing insight

I made the decition of storing orders as `dict` but listing as `list` after finding a test looking for an order by index on the request response.

Validations also were triggered by tests passing while asserting for a raise Error context.

The idea of having custom error (specially the `StatusError`) came after adding the `shipped` status as a valid status and having some tests failing
to asser the validation error message.

# Next-step

I would probably improve validation and api responses. Right now the `try/catch` is repeated over the handlers and that could be done a bit
better.
