from flask import Blueprint, render_template
from .models import Categories, Subcategory

product = Blueprint('product', __name__, template_folder='../templates/product', static_folder='./templates/static')


@product.route('/category-<category_id>')
def category(category_id):
    categories = Categories.query.all()
    category_active = Categories.query.filter_by(id=category_id).first()
    return render_template('category.html',
                           categories=categories,
                           category_id=int(category_id),
                           category_active=category_active)


@product.route('/category-<category_id>/subcategory-<subcategory_id>')
def subcategory(category_id, subcategory_id):

    categories = Categories.query.all()
    subcategory_active = Subcategory.query.filter_by(id=subcategory_id).first()
    return render_template('subcategories.html', categories=categories,
                           subcategory_active=subcategory_active,
                           category_id=int(category_id))



