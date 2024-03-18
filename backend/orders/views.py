from flask import Blueprint, render_template, session, request, jsonify, abort

from backend.product.models import Products
from .models import CreateOrder
from .forms import OrderForm

orders = Blueprint('orders', __name__, template_folder='../templates/orders')


@orders.route('/')
def cart():
    cart: dict = {Products.query.filter_by(id=int(data['product_id'])).first(): data['quantity']
                  for name, data in session['cart'].items()}

    return render_template('orders.html', cart=cart)


@orders.route('/add-to-cart', methods=['POST'])
def add_to_cart():
    if 'cart' not in session:
        session['cart']: dict = {}
    data = request.get_json()
    session_cart_dict = session.get('cart', {})

    if data['product_name'] in session_cart_dict:
        session_cart_dict[data['product_name']]['quantity'] += 1
    else:
        session_cart_dict[data['product_name']] = {'product_id': data['product_id'],
                                                   'quantity': 1 if 'quantity' not in data else data['quantity']}
    session['cart'] = session_cart_dict

    return jsonify(quantity_in_card=len(session['cart']))


# TODO add datatime when create order
@orders.route('/submit-order', methods=['POST'])
def submit_order():
    if request.method == 'POST' and OrderForm.validate_data(request.json):
        request_data = request.json

        new_order = CreateOrder(request_data)
        new_order.set_form_data_to_orders()
        new_order.save()

    return 'success'


@orders.route('/success')
def success_order():
    return 'Hello World'