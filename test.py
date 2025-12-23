canvasW = 800
canvasH = 600
gridW = 16
gridH = 16
tileSize = 37
gap = 0

gridPixelW = gridW * tileSize + (gridW - 1) * gap
gridPixelH = gridH * tileSize + (gridH - 1) * gap

originX = (canvasW - gridPixelW) / 2
originY = (canvasH - gridPixelH) / 2

for tile in range(gridW*gridH):
    x = tile % gridW
    y = tile // gridW

    pixelX = originX + x * (tileSize + gap)
    pixelY = originY + y * (tileSize + gap)

    print(f"Tile {tile}: Grid({x}, {y}) -> Grid Pixel({gridPixelW}, {gridPixelH}) -> Origin({originX}, {originY}) -> Pixel({pixelX}, {pixelY})")