import os
import sys
import io
import re
from urllib.request import urlopen, Request
from urllib.parse import urlparse, urljoin
from PIL import Image

# setup outputs folder, avoid crash, artifact location
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "outputs")
os.makedirs(OUTPUT_DIR, exist_ok=True)


def out(name: str) -> str:
    return os.path.join(OUTPUT_DIR, name)


# open file, force RGB, flatten pixels, pack 0xRRGGBB
def load_image(filepath):
    """Load local image file and convert to list-of-lists of 0xRRGGBB ints."""
    try:
        with Image.open(filepath) as img:
            img = img.convert("RGB")
            width, height = img.size
            pixels = list(img.getdata())
            image_data = [
                [(r << 16) | (g << 8) | b for r, g, b in pixels[i * width:
                 (i + 1) * width]]
                for i in range(height)
            ]
            print(f"Successfully loaded '{filepath}' ({width}x{height})")
            return image_data
    except Exception as e:
        print(f"Error loading image: {e}")
        return None


# unpack ints to (r,g,b), write to disk, safe exception handling
def save_image(image_data, filepath):
    """Save list-of-lists of 0xRRGGBB ints to an image file."""
    if not image_data or not image_data[0]:
        print("Error: Image data is empty.")
        return
    h, w = len(image_data), len(image_data[0])
    img = Image.new("RGB", (w, h))
    pixels = []
    for row in image_data:
        for value in row:
            r = (value >> 16) & 0xFF
            g = (value >> 8) & 0xFF
            b = value & 0xFF
            pixels.append((r, g, b))
    img.putdata(pixels)
    try:
        img.save(filepath)
        print(f"Saved: {os.path.abspath(filepath)}")
    except Exception as e:
        print(f"An error occurred while saving: {e}")


# nearest neighbor scaling, chunky pixels, integer factor
def scale_image(image_data, factor):
    """Nearest neighbor integer scaling."""
    if not image_data or not image_data[0] or factor <= 0:
        return []
    if factor == 1:
        return [row[:] for row in image_data]
    new_h = len(image_data) * factor
    new_w = len(image_data[0]) * factor
    new_image = [[0] * new_w for _ in range(new_h)]
    for y in range(new_h):
        for x in range(new_w):
            new_image[y][x] = image_data[y // factor][x // factor]
    return new_image


# check if source is a URL
def is_url(source: str) -> bool:
    return urlparse(source).scheme in ("http", "https")


# fetch URL, handle redirects, return bytes and content type
def fetch_url(url: str, timeout: int = 15):
    req = Request(
        url,
        headers={
            "User-Agent": "Mozilla/5.0",
            "Accept": "image/*,*/*;q=0.8",
            "Referer": url,
        },
    )
    with urlopen(req, timeout=timeout) as r:
        data = r.read()
        content_type = (r.headers.get("Content-Type")
                        or "").split(";")[0].strip().lower()
        final_url = r.geturl()  # după eventuale redirecturi
    return data, content_type, final_url


# check if URL looks like an image link
def _looks_like_image_url(u: str) -> bool:
    return u.lower().split("?")[0].endswith((".png", ".jpg", ".jpeg", ".webp",
                                             ".bmp"))


def _image_bytes_to_data(data: bytes, source="URL"):
    with Image.open(io.BytesIO(data)) as img:
        img = img.convert("RGB")
        w, h = img.size
        pixels = list(img.getdata())
    image_data = [
        [(r << 16) | (g << 8) | b for r, g, b in pixels[i * w:(i + 1) * w]]
        for i in range(h)
    ]
    print(f"Successfully loaded {source} ({w}x{h})")
    return image_data


def load_image_from_url(url: str):
    try:
        data, ctype, final_url = fetch_url(url)

        if ctype.startswith("image/") or _looks_like_image_url(final_url):
            return _image_bytes_to_data(data, source=final_url)

        html = data.decode("utf-8", "ignore")
        m = re.search(
            r'property=["\']og:image["\'][^>]*content=["\']([^"\']+)["\']',
            html, re.I)
        if not m:
            m = re.search(
                (
                    r'name=["\']twitter:image["\'][^>]*content=["\']'
                    r'([^"\']+)["\']'
                ),
                html,
                re.I,
            )

        if m:
            img_url = urljoin(final_url, m.group(1))
            data2, ctype2, final_img_url = fetch_url(img_url)
            if (
               not ctype2.startswith("image/")
                and not _looks_like_image_url(final_img_url)
               ):
                print("Found meta image,"
                      "but it doesn't look like a direct image URL."
                      )
                return None
            return _image_bytes_to_data(data2, source=final_img_url)

        print("The URL is a webpage (HTML), not a direct image."
              "Provide a .jpg/.png link.")
        return None

    except Exception as e:
        print(f"Error loading URL: {e}")
        return None


def load_image_any(source: str):
    """Route to URL or local loader based on source."""
    return load_image_from_url(source) if is_url(
        source) else load_image(source)


# Pixel manipulation helpers

def get_red(px): return (px >> 16) & 0xFF
def get_green(px): return (px >> 8) & 0xFF
def get_blue(px): return px & 0xFF


def create_pixel(r, g, b):
    return ((r & 0xFF) << 16) | ((g & 0xFF) << 8) | (b & 0xFF)


# ----------Image processing functions------------

def to_grayscale(image_data):
    h, w = len(image_data), len(image_data[0])
    out = [[0] * w for _ in range(h)]
    for y in range(h):
        for x in range(w):
            px = image_data[y][x]
            gray = (get_red(px) + get_green(px) + get_blue(px)) // 3
            out[y][x] = create_pixel(gray, gray, gray)
    return out


def invert_colors(image_data):
    h, w = len(image_data), len(image_data[0])
    out = [[0] * w for _ in range(h)]
    for y in range(h):
        for x in range(w):
            out[y][x] = image_data[y][x] ^ 0xFFFFFF
    return out


def remove_green(image_data):
    h, w = len(image_data), len(image_data[0])
    out = [[0] * w for _ in range(h)]
    for y in range(h):
        for x in range(w):
            out[y][x] = image_data[y][x] & 0xFF00FF  # keep RR and BB
    return out


def swap_red_blue(image_data):
    h, w = len(image_data), len(image_data[0])
    out = [[0] * w for _ in range(h)]
    for y in range(h):
        for x in range(w):
            px = image_data[y][x]
            red_to_blue = (px & 0xFF0000) >> 16
            green_stay = px & 0x00FF00
            blue_to_red = (px & 0x0000FF) << 16
            out[y][x] = blue_to_red | green_stay | red_to_blue
    return out


def posterize_keep_bits(image_data, keep_bits=2):
    keep_bits = max(1, min(8, int(keep_bits)))
    mask = 0xFF & (~((1 << (8 - keep_bits)) - 1))  # e.g., 2 bits -> 11000000
    h, w = len(image_data), len(image_data[0])
    out = [[0] * w for _ in range(h)]
    for y in range(h):
        for x in range(w):
            px = image_data[y][x]
            r = get_red(px) & mask
            g = get_green(px) & mask
            b = get_blue(px) & mask
            out[y][x] = create_pixel(r, g, b)
    return out


def threshold_bw(image_data, t=128):
    t = max(0, min(255, int(t)))
    h, w = len(image_data), len(image_data[0])
    out = [[0] * w for _ in range(h)]
    for y in range(h):
        for x in range(w):
            px = image_data[y][x]
            gray = (get_red(px) + get_green(px) + get_blue(px)) // 3
            val = 255 if gray >= t else 0
            out[y][x] = create_pixel(val, val, val)
    return out


# ---------- Main entry ----------

def build_smiley():
    BLACK, YELLOW, BLUE = 0x000000, 0xFFFF00, 0x0000FF
    return [
        [BLACK, BLACK, BLACK, BLACK, BLACK, BLACK, BLACK, BLACK],
        [BLACK, YELLOW, YELLOW, YELLOW, YELLOW, YELLOW, YELLOW, BLACK],
        [BLACK, YELLOW, BLUE,   YELLOW, YELLOW, BLUE,   YELLOW, BLACK],
        [BLACK, YELLOW, YELLOW, YELLOW, YELLOW, YELLOW, YELLOW, BLACK],
        [BLACK, YELLOW, BLUE,   YELLOW, YELLOW, BLUE,   YELLOW, BLACK],
        [BLACK, YELLOW, YELLOW, BLUE,   BLUE,   YELLOW, YELLOW, BLACK],
        [BLACK, YELLOW, YELLOW, YELLOW, YELLOW, YELLOW, YELLOW, BLACK],
        [BLACK, BLACK, BLACK, BLACK, BLACK, BLACK, BLACK, BLACK],
    ]


if __name__ == "__main__":
    source = sys.argv[1].strip() if len(sys.argv) > 1 else input(
        "Enter local file path or URL, or 's' for smiley: "
    ).strip()

    if not source:
        print("No source provided.")
        sys.exit(1)

    if source.lower() in ("s", "smiley"):
        img = scale_image(build_smiley(), 20)
    else:
        img = load_image_any(source)

    if not img:
        print(
            "Could not load image. For web, use a DIRECT image link "
            "ends with .jpg/.png.")
        sys.exit(1)

    save_image(img,                          out("original.png"))
    save_image(invert_colors(img),           out("invert.png"))
    save_image(to_grayscale(img),            out("grayscale.png"))
    save_image(remove_green(img),            out("no_green.png"))
    save_image(swap_red_blue(img),           out("swap_rb.png"))
    save_image(posterize_keep_bits(img, 2),  out("posterize_2bits.png"))
    save_image(threshold_bw(img, 128),       out("threshold_128.png"))
    print(f"All outputs saved to: {OUTPUT_DIR}")


# Photo link
"""
https://upload.wikimedia.org/wikipedia/commons/3/3f/Fronalpstock_big.jpg
"""
