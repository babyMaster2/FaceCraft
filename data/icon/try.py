from PIL import Image


def get_image_size(image_path):
    with Image.open(image_path) as img:
        width, height = img.size
    return width, height


if __name__ == '__main__':
    path = '../img/555472.jpg'
    width, height = get_image_size(path)
    print(width, height)
