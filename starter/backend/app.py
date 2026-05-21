from flask import Flask, request, jsonify, send_from_directory
from backend.order_tracker import OrderTracker
from backend.in_memory_storage import InMemoryStorage

app = Flask(__name__, static_folder='../frontend')
in_memory_storage = InMemoryStorage()
order_tracker = OrderTracker(in_memory_storage)

@app.route('/')
def serve_index():
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/<path:filename>')
def serve_static(filename):
    return send_from_directory(app.static_folder, filename)

@app.route('/api/orders', methods=['POST'])
def add_order_api():
    data = request.get_json()
    
    try:        
        order_tracker.add_order(
            order_id=data['order_id'],
            item_name=data['item_name'],
            quantity=data['quantity'],
            customer_id=data['customer_id'],
            status=data.get('status', 'pending')
        )
        return jsonify({"message": "Order added successfully", "order_id": data['order_id']}), 201
    except ValueError as ve:
        return jsonify({"error": str(ve)}), 400
    except Exception as e:
        print(e)
        return jsonify({"error": "An unexpected error occurred"}), 500

@app.route('/api/orders/<string:order_id>', methods=['GET'])
def get_order_api(order_id):
    try:
        order = order_tracker.get_order_by_id(order_id)
        return jsonify(order), 200
    except ValueError as ve:
        return jsonify({"error": str(ve)}), 404
    except Exception as e:
        print(e)
        return jsonify({"error": "An unexpected error occurred"}), 500

@app.route('/api/orders/<string:order_id>/status', methods=['PUT'])
def update_order_status_api(order_id):
    data = request.get_json()
    new_status = data.get('new_status')
    try:
        order_tracker.update_order_status(order_id, new_status)
        updated_order = order_tracker.get_order_by_id(order_id)
        return jsonify({"message": "Order status updated successfully", "order_id": order_id, "status": updated_order['status']}), 200
    except ValueError as ve:
        return jsonify({"error": str(ve)}), 400
    except Exception as e:
        return jsonify({"error": "An unexpected error occurred"}), 500

@app.route('/api/orders', methods=['GET'])
def list_orders_api():
    order_tracker.list_all_orders()
    status_filter = request.args.get('status')
    try:
        if status_filter:
            orders = order_tracker.list_orders_by_status(status_filter)
        else:
            orders = order_tracker.list_all_orders()

        return jsonify(list(orders.values())), 200
    except ValueError as ve:
        return jsonify({"error": str(ve)}), 400
    except Exception as e:
        return jsonify({"error": "An unexpected error occurred"}), 500

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=3002, debug=True)
