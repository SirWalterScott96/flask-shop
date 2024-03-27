from backend.main import create_app

app = create_app()

# def resize_img(image_path):
#     height = 230
#     with Image.open(image_path) as img:
#         aspect_ratio = img.width / img.height
#         width = int(height / aspect_ratio)
#         img.thumbnail((width, height))
#         img.save(image_path)


if __name__ == '__main__':
    app.run(debug=True)
