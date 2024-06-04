from collections import defaultdict
from urllib.parse import parse_qs
from datetime import datetime
from flask_login import current_user

from backend.extensions import db
from backend.product.models import Products

orders_products = db.Table('orders_products',
                           db.Column('order_id', db.Integer, db.ForeignKey('orders.id'), primary_key=True),
                           db.Column('product_id', db.Integer, db.ForeignKey('products.id'), primary_key=True),
                           db.Column('quantity', db.Integer, nullable=False)
                           )


class Orders(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    phone_number = db.Column(db.String(100), nullable=False)
    street = db.Column(db.String(255), nullable=False)
    house_number = db.Column(db.String(100), nullable=False)
    entrance_number = db.Column(db.String(100), nullable=False)
    comment = db.Column(db.String(255), nullable=False)
    total_price = db.Column(db.Float, nullable=False)
    order_time = db.Column(db.DateTime, nullable=False, default=datetime.utcnow())
    products = db.relationship('Products', secondary=orders_products, backref='orders', lazy=True)
    status = db.Column(db.String(100), nullable=True, default='in_process')

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)

    @staticmethod
    def get_all_user_orders(user):
        pass

    @staticmethod
    def get_all_orders():
        return Orders.query.order_by(Orders.order_time.desc()).all()

    @staticmethod
    def get_quantity_dict(user) -> dict:
        order_quantities_dict = defaultdict(list)
        for order in user.orders:
            for product in order.products:
                quantity = db.session.query(orders_products.c.quantity).filter_by(order_id=order.id,
                                                                                  product_id=product.id).scalar()
                order_quantities_dict[order.id].append(quantity)
        return order_quantities_dict

    @staticmethod
    def get_all_orders_products_data():
        order_quantities_dict = defaultdict(list)
        for order in Orders.get_all_orders():
            for product in order.products:
                quantity = db.session.query(orders_products.c.quantity).filter_by(order_id=order.id,
                                                                                  product_id=product.id).scalar()
                order_quantities_dict[order.id].append(quantity)
        return order_quantities_dict

    @staticmethod
    def set_new_status(order_id, status):
        order = Orders.query.filter_by(id=order_id).first()
        if order:
            order.status = status
            db.session.commit()
            return 'success'
        else:
            return 'fail'

    def __repr__(self):
        return f"Orders('{self.name}', '{self.email}', '{self.phone_number}', '{self.street}', '{self.house_number}'," \
               f" '{self.entrance_number}', '{self.comment}', '{self.total_price}')"


class CreateOrder(Orders):

    def __init__(self, request_data):
        super().__init__()
        self.request_data = request_data
        self.product_dict = None
        self.new_order = None

    def set_form_data_to_orders(self):
        form_data = self.get_form_from_data()
        self.name = form_data.get('name')[0]
        self.email = form_data.get('email')[0]
        self.phone_number = form_data.get('phone_number')[0]
        self.street = form_data.get('street')[0]
        self.house_number = form_data.get('house_number')[0]
        self.entrance_number = form_data.get('entrance_number')[0]
        self.comment = form_data.get('comment')[0] if 'comment' in form_data else ''
        self.product_dict = self.get_products_list()
        self.total_price = self.total_price_product()

    def get_form_from_data(self):
        return parse_qs(self.request_data['formData'])

    def get_products_from_data(self):
        return self.request_data['productsData']

    def get_products_list(self):
        products_form = self.get_products_from_data()
        products_list: dict = {Products.query.get(product_id): quantity for product_id, quantity
                               in
                               products_form.items()}
        return products_list

    def total_price_product(self):
        total_price_products: float = 0

        for product, quantity in self.product_dict.items():
            price_local: float = product.price * int(quantity)
            total_price_products += price_local

        return total_price_products

    def save(self):
        self.new_order = Orders(
            name=self.name,
            email=self.email,
            phone_number=self.phone_number,
            street=self.street,
            house_number=self.house_number,
            entrance_number=self.entrance_number,
            comment=self.comment,
            total_price=self.total_price,
            user_id=current_user.id if current_user.is_active else None,
        )

        db.session.add(self.new_order)
        db.session.commit()

        self.add_products_and_quantity_to_order()

    def add_products_and_quantity_to_order(self):
        for product, quantity in self.product_dict.items():
            order_products = orders_products.insert().values(order_id=self.new_order.id,
                                                             product_id=product.id,
                                                             quantity=quantity)
            db.session.execute(order_products)

        db.session.commit()
