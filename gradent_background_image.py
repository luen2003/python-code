from PIL import Image
import numpy as np

color1 = np.array([253, 141, 50])  
color2 = np.array([163, 7, 186])  

def create_gradient_image(width, height, filename):
    # Tạo mảng tọa độ
    x = np.linspace(0, 1, width)
    y = np.linspace(1, 0, height) 

    X, Y = np.meshgrid(x, y)

    T = (X + Y) / 2.0
    T = np.expand_dims(T, axis=2)

    image_data = (1 - T) * color1 + T * color2
    image_data = image_data.astype(np.uint8)

    image = Image.fromarray(image_data)
    image.save(filename)
    print(f"Đã tạo thành công ảnh '{filename}' (Kích thước: {width}x{height})!")

create_gradient_image(1920, 1080, "gradient_background_1920x1080.png")
create_gradient_image(1080, 1920, "gradient_background_1080x1920.png")