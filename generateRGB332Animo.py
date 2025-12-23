import struct

# --- RGB332 -> RGB565 helpers ---
def rgb332_to_rgb888(c: int):
    r3 = (c >> 5) & 0x07
    g3 = (c >> 2) & 0x07
    b2 = c & 0x03
    r8 = (r3 * 255) // 7
    g8 = (g3 * 255) // 7
    b8 = (b2 * 255) // 3
    return r8, g8, b8

def rgb888_to_rgb565(r8: int, g8: int, b8: int) -> int:
    r5 = (r8 * 31) // 255
    g6 = (g8 * 63) // 255
    b5 = (b8 * 31) // 255
    return (r5 << 11) | (g6 << 5) | b5

def rgb332_to_rgb565(c: int) -> int:
    r8, g8, b8 = rgb332_to_rgb888(c)
    return rgb888_to_rgb565(r8, g8, b8)

def enc1250(s: str) -> bytes:
    return s.encode("windows-1250", errors="replace")

def pad_bytes(b: bytes, size: int) -> bytes:
    if len(b) >= size:
        return b[:size]
    return b + (b"\x00" * (size - len(b)))

def write_header(f, frames_count: int, bpp: int, events_count: int,
                 fps: int, flags: int, transparency: int,
                 random_frames_number: int, author: str, description: str):
    # magic: "NVP\0"
    f.write(b"NVP\x00")
    f.write(struct.pack("<HHH", frames_count, bpp, events_count))
    f.write(b"\x00" * 0x0D)
    f.write(struct.pack("<II", fps, flags))
    f.write(struct.pack("<B", transparency))
    f.write(struct.pack("<H", random_frames_number))
    f.write(b"\x00" * 0x0A)

    a = enc1250(author)
    d = enc1250(description)
    f.write(struct.pack("<I", len(a)))
    f.write(a)
    f.write(struct.pack("<I", len(d)))
    f.write(d)

def write_frame(f, pos_x: int, pos_y: int, has_sounds: int,
                transparency: int, name: str, sounds=None):
    if sounds is None:
        sounds = []

    # 4 bytes constant
    f.write(bytes([0x00, 0xA4, 0xCE, 0x57]))
    # skip 4
    f.write(b"\x00" * 4)

    f.write(struct.pack("<hh", pos_x, pos_y))

    # uint32 0xffffffff
    f.write(struct.pack("<I", 0xFFFFFFFF))
    # hasSounds uint32
    f.write(struct.pack("<I", has_sounds))
    # skip 4
    f.write(b"\x00" * 4)

    # transparency byte
    f.write(struct.pack("<B", transparency))
    # skip 5
    f.write(b"\x00" * 5)

    # name (with null terminator) length-prefixed
    name_b = enc1250(name + "\x00")
    f.write(struct.pack("<I", len(name_b)))
    f.write(name_b)

    if has_sounds != 0:
        sfx = ";".join([s.strip() for s in sounds if s.strip()]) + "\x00"
        sfx_b = enc1250(sfx)
        f.write(struct.pack("<I", len(sfx_b)))
        f.write(sfx_b)

def write_event(f, name: str, frames_count: int, loop_after_frame: int,
                transparency: int, frames_image_mapping):
    # 32 bytes name padded (with null)
    name_b = enc1250(name + "\x00")
    f.write(pad_bytes(name_b, 0x20))

    f.write(struct.pack("<H", frames_count))
    f.write(b"\x00" * 0x06)
    # loopAfterFrame modulo framesCount
    f.write(struct.pack("<I", loop_after_frame % frames_count))
    f.write(b"\x00" * 0x0A)
    f.write(struct.pack("<B", transparency))
    f.write(b"\x00" * 0x0C)

    # framesImageMapping (uint16 per frame)
    for idx in frames_image_mapping:
        f.write(struct.pack("<H", idx))

    # frames themselves
    for i in range(frames_count):
        write_frame(
            f,
            pos_x=0,
            pos_y=0,
            has_sounds=0,
            transparency=transparency,
            name=f"C{i:03d}",
            sounds=[]
        )

def write_ann_image_header(f, width: int, height: int, pos_x: int, pos_y: int,
                           compression_type: int, image_len: int, alpha_len: int, name: str):
    f.write(struct.pack("<HHhhH", width, height, pos_x, pos_y, compression_type))
    f.write(struct.pack("<I", image_len))

    # misteriousValue = 4 (uint16), then skip 4 bytes, then pad to 12 total
    misterious_value = 4
    f.write(struct.pack("<H", misterious_value))
    f.write(b"\x00" * misterious_value)
    f.write(b"\x00" * (12 - misterious_value))

    f.write(struct.pack("<I", alpha_len))

    # 20 bytes name padded
    name_b = enc1250(name)
    f.write(pad_bytes(name_b, 0x14))

def build_solid_tile_rgb565_le(width: int, height: int, rgb565: int) -> bytes:
    # little-endian 16-bit per pixel
    px = struct.pack("<H", rgb565)
    return px * (width * height)

def build_solid_alpha(width: int, height: int, a: int = 255) -> bytes:
    return bytes([a]) * (width * height)

def generate_rgb332_palette_ann(output_path: str,
                                tile_w: int = 37,
                                tile_h: int = 37,
                                fps: int = 60):
    frames_count = 256
    events_count = 1
    bpp = 16  # RGB565 target in image payload
    flags = 0
    transparency = 255
    random_frames_number = 0

    author = "Patryk"
    description = "RGB332 palette: frame index = color (0..255)"

    # Prepare image payloads
    image_payloads = []
    image_headers = []

    for i in range(256):
        rgb565 = rgb332_to_rgb565(i)
        if rgb565 == 0xF81F: # if it's magenta
            rgb565 ^= 0x0001 # flip a little bit, as magenta... DirectDraw things, colorkey...
        color_bytes = build_solid_tile_rgb565_le(tile_w, tile_h, rgb565)
        alpha_bytes = build_solid_alpha(tile_w, tile_h, 255)

        image_len = len(color_bytes)
        alpha_len = len(alpha_bytes)

        image_payloads.append((color_bytes, alpha_bytes))
        image_headers.append({
            "width": tile_w,
            "height": tile_h,
            "pos_x": 0,
            "pos_y": 0,
            "compression_type": 0,  # NONE
            "image_len": image_len,
            "alpha_len": alpha_len,
            "name": f"C{i:03d}"
        })

    with open(output_path, "wb") as f:
        # Header
        write_header(
            f,
            frames_count=frames_count,
            bpp=bpp,
            events_count=events_count,
            fps=fps,
            flags=flags,
            transparency=transparency,
            random_frames_number=random_frames_number,
            author=author,
            description=description
        )

        # One event: 256 frames mapped 1:1 to 256 images
        frames_image_mapping = list(range(256))
        write_event(
            f,
            name="RGB332",
            frames_count=frames_count,
            loop_after_frame=0,
            transparency=transparency,
            frames_image_mapping=frames_image_mapping
        )

        # Image metadata headers (must come BEFORE image data, per loader)
        for hdr in image_headers:
            write_ann_image_header(
                f,
                width=hdr["width"],
                height=hdr["height"],
                pos_x=hdr["pos_x"],
                pos_y=hdr["pos_y"],
                compression_type=hdr["compression_type"],
                image_len=hdr["image_len"],
                alpha_len=hdr["alpha_len"],
                name=hdr["name"]
            )

        # Image data blocks: color then alpha for each frame
        for color_bytes, alpha_bytes in image_payloads:
            f.write(color_bytes)
            f.write(alpha_bytes)

if __name__ == "__main__":
    generate_rgb332_palette_ann("common/rgb332_palette.ann", tile_w=37, tile_h=37, fps=60)
    print("Wygenerowano rgb332_palette.ann")
