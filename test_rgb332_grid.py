from PIL import Image, ImageDraw

CANVAS_W, CANVAS_H = 800, 600
GRID_W, GRID_H = 16, 16
TILE = 37
GAP = 0  # ustaw np. 1 jeśli chcesz przerwy między kaflami

def rgb332_to_rgb888(c: int):
    r3 = (c >> 5) & 0x07
    g3 = (c >> 2) & 0x07
    b2 = c & 0x03
    r8 = (r3 * 255) // 7
    g8 = (g3 * 255) // 7
    b8 = (b2 * 255) // 3
    return r8, g8, b8

def main():
    grid_px_w = GRID_W * TILE + (GRID_W - 1) * GAP
    grid_px_h = GRID_H * TILE + (GRID_H - 1) * GAP
    origin_x = (CANVAS_W - grid_px_w) // 2
    origin_y = (CANVAS_H - grid_px_h) // 2

    img = Image.new("RGB", (CANVAS_W, CANVAS_H), (16, 16, 16))  # tło
    draw = ImageDraw.Draw(img)

    for idx in range(256):
        x = idx % GRID_W
        y = idx // GRID_W

        px = origin_x + x * (TILE + GAP)
        py = origin_y + y * (TILE + GAP)

        r, g, b = rgb332_to_rgb888(idx)
        draw.rectangle([px, py, px + TILE - 1, py + TILE - 1], fill=(r, g, b))

    img.save("rgb332_grid_800x600.png")
    print("Zapisano: rgb332_grid_800x600.png")
    print(f"origin=({origin_x},{origin_y}), grid={grid_px_w}x{grid_px_h}")

if __name__ == "__main__":
    main()
