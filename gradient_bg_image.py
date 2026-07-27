from PIL import Image

# Màu gradient
COLOR1 = (255, 138, 0)    # #ff8a00
COLOR2 = (255, 79, 163)   # #ff4fa3
COLOR3 = (139, 92, 246)   # #8b5cf6


def lerp(a, b, t):
    return int(a + (b - a) * t)


def blend(c1, c2, t):
    return (
        lerp(c1[0], c2[0], t),
        lerp(c1[1], c2[1], t),
        lerp(c1[2], c2[2], t),
    )


def create_gradient(width, height, filename):
    img = Image.new("RGB", (width, height))
    pixels = img.load()

    # CSS 135deg:
    # Gradient chạy từ góc trên trái -> góc dưới phải
    max_proj = (width - 1) + (height - 1)

    for y in range(height):
        for x in range(width):
            t = (x + y) / max_proj

            if t < 0.5:
                color = blend(COLOR1, COLOR2, t / 0.5)
            else:
                color = blend(COLOR2, COLOR3, (t - 0.5) / 0.5)

            pixels[x, y] = color

    img.save(filename)
    print(f"Saved: {filename}")


if __name__ == "__main__":
    create_gradient(1920, 1080, "gradient_1920x1080.png")
    create_gradient(1080, 1920, "gradient_1080x1920.png")