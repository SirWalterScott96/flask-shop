import uuid
from werkzeug.utils import secure_filename
from backend.settings import Config


class Image:

    def __init__(self, image_data, directory):
        self.directory = directory
        self.image_data = image_data
        self.name = self.secure_name(self.image_data)
        self.path = self.img_path()

    def secure_name(self, img_data):
        return str(uuid.uuid4()) + '_' + secure_filename(img_data.filename)

    def img_path(self):
        return self.directory / self.name

    def save_img(self):
        self.image_data.save(self.path)

    def img_url(self):
        return f'{self.path.name}/{self.name}'


class ImageProduct(Image):
    def __init__(self, image_data):
        super().__init__(image_data, Config.UPLOAD_FOLDER_PRODUCT_IMGS)


class ImageSubcategory(Image):
    def __init__(self, image_data):
        super().__init__(image_data, Config.UPLOAD_FOLDER_SUBCATEGORY_IMGS)
