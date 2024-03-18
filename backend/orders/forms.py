from flask import abort
import re
from urllib.parse import parse_qs


class OrderForm:

    @staticmethod
    def validate_data(request_data):

        if not request_data or not isinstance(request_data, dict):
            abort(400)

        required_fields = ['formData', 'productsData']
        if not all(field in request_data for field in required_fields):
            abort(400)

        email = parse_qs(request_data['formData']).get('email')[0]

        if not email or not re.match(r'^[\w\.-]+@[\w\.-]+\.\w+$', email):
            abort(400)

        return True
