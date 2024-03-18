from flask_wtf import FlaskForm
from wtforms import StringField, FloatField, IntegerField, TextAreaField, HiddenField
from flask_wtf.file import FileField, FileAllowed, FileRequired
from wtforms.validators import DataRequired

from backend.settings import Config
from .models import Categories


class ProductForm(FlaskForm):
    name = StringField(validators=[DataRequired()])
    price = FloatField(validators=[DataRequired()])
    img_upload = FileField(validators=[FileRequired(), FileAllowed(Config.UPLOAD_EXTENSIONS, 'Images only')])
    quantity = IntegerField(validators=[DataRequired()])
    description = TextAreaField()
    hidden_tag_id = HiddenField()

    def validate(self, extra_validators=None):
        initial_validation = super(ProductForm, self).validate(extra_validators)

        if not initial_validation:
            return False
        return True


class SubCategoryForm(FlaskForm):
    name = StringField(validators=[DataRequired()])
    img_upload = FileField(validators=[FileRequired(), FileAllowed(Config.UPLOAD_EXTENSIONS, 'Images only')])
    hidden_tag_id = HiddenField()


class CategoriesForm(FlaskForm):
    name = StringField(validators=[DataRequired()])

    def validate(self, extra_validators=None):
        initial_validation = super(CategoriesForm, self).validate(extra_validators)

        if not initial_validation:
            return False
        category_check = Categories.query.filter_by(name=self.name.data).first()

        # Checking if category exist
        if category_check:
            return False
        return True
