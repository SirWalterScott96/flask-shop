from flask import Blueprint, render_template, jsonify, request, g
from .models import Categories, Subcategory, Products, ValidateProduct
from backend.orders.models import Orders

product = Blueprint('product', __name__, template_folder='../templates/product', static_folder='./templates/static')


@product.route('/category')
@product.route('/category-<category_id>')
def category(category_id=None):
    if category_id:
        g.category_active = Categories.query.filter_by(id=category_id).first()
        g.category_id = int(category_id)

    return render_template('category.html')


@product.route('/category-<category_id>/subcategory-<subcategory_id>')
def subcategory(category_id, subcategory_id):
    subcategory_active = Subcategory.query.filter_by(id=subcategory_id).first()
    return render_template('subcategories.html',
                           subcategory_active=subcategory_active,
                           category_id=int(category_id))


@product.route('/category-<category_id>/subcategory-<subcategory_id>/product-<product_id>')
def show_product(category_id, subcategory_id, product_id):
    product = Products.query.filter_by(id=product_id).first()
    categories = Categories.query.all()

    return render_template('product.html', product=product,
                           categories=categories,
                           category_id=int(category_id),
                           subcategory_id=int(subcategory_id))


@product.route('/show-product', methods=['POST'])
def search_product():
    if request.method == 'POST':
        product_name = request.form.get('product_name')
        product = ValidateProduct(product_name)
        return product.get_product_page()


@product.route('/get-all-products', methods=['GET'])
def get_all_products():
    all_products_list = Products.query.all()
    products_dict = {product.name: product.id for product in all_products_list}
    return jsonify(products_dict)


# TODO realize show product correctly
@product.route('/test')
def test():
    """Reference"""
    test_product = Products.query.get(1)
    print(test_product.name)

    test_subcategory = test_product.subcategory.name
    print(test_subcategory)

    test_category = test_product.subcategory.categories.name
    print(test_category)

    return 'Hello World'
