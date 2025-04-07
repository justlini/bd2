import base64
from io import BytesIO
from tkinter import Image
from PIL import Image

imagem = "Sample_JPG.jpg";
def converterImg (imagem):
    with open(imagem, "rb") as image_file:
        image_bytes = image_file.read()
    print(base64.b64encode(image_bytes).decode('utf-8'))

    # Create a BytesIO object to handle the image data
    image_stream = BytesIO(image_bytes)

    # Open the image using Pillow (PIL)
    img = Image.open(image_stream)
    img.show()

    def converterImg(imagem):
        with open(imagem, "rb") as image_file:
            image_bytes = image_file.read()
        print(base64.b64encode(image_bytes).decode('utf-8'))

        # Create a BytesIO object to handle the image data
        image_stream = BytesIO(image_bytes)

        # Open the image using Pillow (PIL)
        img = Image.open(image_stream)
        img.show()
converterImg(imagem)
