from PIL import Image
import numpy as np

width = 1920
height = 1080

color1 = np.array([253, 141, 50])  
color2 = np.array([163, 7, 186])  

x = np.linspace(0, 1, width)
y = np.linspace(1, 0, height) 

X, Y = np.meshgrid(x, y)

T = (X + Y) / 2.0

T = np.expand_dims(T, axis=2)

image_data = (1 - T) * color1 + T * color2

image_data = image_data.astype(np.uint8)

image = Image.fromarray(image_data)
image.save("gradient_background_image.png")

print("Đã tạo thành công ảnh 'gradient_background_image.png'!")