from flask import render_template, redirect, url_for

from backend.extensions import db


class Categories(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    sub_category = db.relationship('Subcategory', backref='categories', lazy=True)


class Subcategory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'))
    img_url = db.Column(db.String(200), nullable=False)

    products = db.relationship('Products', backref='subcategory', cascade='all, delete', lazy=True)


class Products(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Float, nullable=False)
    img_url = db.Column(db.String(200), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    description = db.Column(db.Text)
    subcategory_id = db.Column(db.Integer, db.ForeignKey('subcategory.id'))

    def update_from_json(self, data: dict):
        """Update table from json"""
        if 'card-name' in data:
            self.name = data['card-name']
        if 'card-price' in data:
            self.price = data['card-price']
        if 'card-quantity' in data:
            self.quantity = data['card-quantity']
        if 'card-description' in data:
            self.description = data['card-description']

        db.session.commit()

    @staticmethod
    def set_quantity_from_order_status(self, order):
        raise NotImplementedError

    def __str__(self):
        return self.name

    def __repr__(self):
        return f"Product('{self.name}', '{self.price}', '{self.quantity}')"


class ValidateProduct:
    def __init__(self, product_name):
        self.product = self.set_product_by_name(product_name)

    def set_product_by_name(self, product_name):
        return Products.query.filter_by(name=product_name).first()

    def get_product_page(self):
        if self.product:
            return redirect(url_for('product.show_product', product_id=self.product.id,
                                    subcategory_id=self.product.subcategory.id,
                                    category_id=self.product.subcategory.categories.id))
        else:
            return render_template('product.html')





