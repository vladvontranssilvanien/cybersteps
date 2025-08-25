import os
import sys
import io
import re
from urllib.request import urlopen, Request
from urllib.parse import urlparse, urljoin
from PIL import Image

# -----------------------------------------------------------------------------
# Output folder
# -----------------------------------------------------------------------------
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "outputs")
os.makedirs(OUTPUT_DIR, exist_ok=True)


def out(name: str) -> str:
    return os.path.join(OUTPUT_DIR, name)


# -----------------------------------------------------------------------------
# Local I/O
# -----------------------------------------------------------------------------
def load_image(filepath):
    """Load local image file and convert to list-of-lists of 0xRRGGBB ints."""
    try:
        with Image.open(filepath) as img:
            img = img.convert("RGB")
            width, height = img.size
            pixels = list(img.getdata())
        image_data = [
            [(r << 16) | (g << 8) | b for r, g, b in pixels[i * width:(i + 1)
                                                            * width]]
            for i in range(height)
        ]
        print(f"Successfully loaded '{filepath}' ({width}x{height})")
        return image_data
    except Exception as e:
        print(f"Error loading image: {e}")
        return None


def save_image(image_data, filepath):
    """Save list-of-lists of 0xRRGGBB ints to an image file."""
    if not image_data or not image_data[0]:
        print("Error: Image data is empty.")
        return
    h, w = len(image_data), len(image_data[0])
    img = Image.new("RGB", (w, h))
    buf = []
    for row in image_data:
        for px in row:
            buf.append(((px >> 16) & 0xFF, (px >> 8) & 0xFF, px & 0xFF))
    img.putdata(buf)
    try:
        img.save(filepath)
        print(f"Saved: {os.path.abspath(filepath)}")
    except Exception as e:
        print(f"An error occurred while saving: {e}")


def display_image(image_data):
    """(Optional) Show image with OS viewer."""
    if not image_data or not image_data[0]:
        print("Error: Image data is empty.")
        return
    h, w = len(image_data), len(image_data[0])
    img = Image.new("RGB", (w, h))
    buf = []
    for row in image_data:
        for px in row:
            buf.append(((px >> 16) & 0xFF, (px >> 8) & 0xFF, px & 0xFF))
    img.putdata(buf)
    img.show()


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


# -----------------------------------------------------------------------------
# URL I/O (std lib only)
# -----------------------------------------------------------------------------

def is_url(source: str) -> bool:
    p = urlparse(source)
    return p.scheme in ("http", "https") and bool(p.netloc)


def fetch_url(url: str, timeout: int = 15):
    """Return (bytes, content_type, final_url).
    Adds UA + Referer to reduce 403."""
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
        content_type = (r.headers.get("Content-Type") or
                        "").split(";")[0].strip().lower()
        final_url = r.geturl()  # after redirects
    return data, content_type, final_url


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
    """Load from direct image URL; fallback:
    parse HTML og:image/twitter:image."""
    try:
        data, ctype, final_url = fetch_url(url)

        # Direct image response or URL looks like image
        if ctype.startswith("image/") or _looks_like_image_url(final_url):
            return _image_bytes_to_data(data, source=final_url)

        # Likely HTML: try to extract meta image
        html = data.decode("utf-8", "ignore")
        m = re.search(
            r'property=["\']og:image["\'][^>]*content=["\']([^"\']+)["\']',
            html, re.I)
        if not m:
            m = re.search(
                (r'name=["\']twitter:image["\'][^>]*'
                 r'content=["\']([^"\']+)["\']'),
                html, re.I)
        if m:
            img_url = urljoin(final_url, m.group(1))
            data2, ctype2, final_img_url = fetch_url(img_url)
            if (not ctype2.startswith("image/")) and (
                    not _looks_like_image_url(final_img_url)):
                print("Found meta image, "
                      "but it doesn't look like a direct image URL.")
                return None
            return _image_bytes_to_data(data2, source=final_img_url)

        print("The URL is a webpage (HTML), not a direct image. "
              "Provide a .jpg/.png link.")
        return None

    except Exception as e:
        print(f"Error loading URL: {e}")
        return None


def load_image_any(source: str):
    """Smart router: URL -> load_image_from_url, Local -> load_image
    (with existence check)."""
    if is_url(source):
        return load_image_from_url(source)
    if not os.path.isfile(source):
        print(f"Local path not found: {source}")
        return None
    return load_image(source)


# -----------------------------------------------------------------------------
# Pixel toolkit (bitwise)
# -----------------------------------------------------------------------------

def get_red(px):
    return (px >> 16) & 0xFF


def get_green(px):
    return (px >> 8) & 0xFF


def get_blue(px):
    return px & 0xFF


def create_pixel(r, g, b):
    return ((r & 0xFF) << 16) | ((g & 0xFF) << 8) | (b & 0xFF)


def clamp8(x):
    return 0 if x < 0 else 255 if x > 255 else int(x)


# -----------------------------------------------------------------------------
# Core filters (spec-required)
# -----------------------------------------------------------------------------

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
            out[y][x] = (
                (px & 0x0000FF) << 16) | (px & 0x00FF00) | (
                    (px & 0xFF0000) >> 16)
    return out


def posterize_keep_bits(image_data, keep_bits=2):
    keep_bits = max(1, min(8, int(keep_bits)))
    mask = 0xFF & (~((1 << (8 - keep_bits)) - 1))
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


# -----------------------------------------------------------------------------
# Advanced filters (still spec-compliant)
# -----------------------------------------------------------------------------

def gamma_correction(image_data, gamma=2.2):
    gamma = max(0.1, float(gamma))
    lut = [clamp8(255 * ((i / 255.0) ** (1.0 / gamma))) for i in range(256)]
    h, w = len(image_data), len(image_data[0])
    out = [[0]*w for _ in range(h)]
    for y in range(h):
        for x in range(w):
            px = image_data[y][x]
            r = lut[get_red(px)]
            g = lut[get_green(px)]
            b = lut[get_blue(px)]
            out[y][x] = create_pixel(r, g, b)
    return out


def sepia(image_data):
    h, w = len(image_data), len(image_data[0])
    out = [[0]*w for _ in range(h)]
    for y in range(h):
        for x in range(w):
            px = image_data[y][x]
            r, g, b = get_red(px), get_green(px), get_blue(px)
            tr = clamp8(0.393*r + 0.769*g + 0.189*b)
            tg = clamp8(0.349*r + 0.686*g + 0.168*b)
            tb = clamp8(0.272*r + 0.534*g + 0.131*b)
            out[y][x] = create_pixel(tr, tg, tb)
    return out


def apply_kernel(image_data, kernel, divisor=None, offset=0):
    """3x3 convolution; kernel = 9 ints in row order."""
    if divisor is None:
        s = sum(kernel)
        divisor = s if s != 0 else 1
    h, w = len(image_data), len(image_data[0])
    out = [[0]*w for _ in range(h)]
    for y in range(h):
        for x in range(w):
            if y == 0 or x == 0 or y == h-1 or x == w-1:
                out[y][x] = image_data[y][x]
                continue
            acc_r = acc_g = acc_b = 0
            k = 0
            for dy in (-1, 0, 1):
                for dx in (-1, 0, 1):
                    p = image_data[y+dy][x+dx]
                    acc_r += get_red(p) * kernel[k]
                    acc_g += get_green(p) * kernel[k]
                    acc_b += get_blue(p) * kernel[k]
                    k += 1
            r = clamp8(round(acc_r / divisor) + offset)
            g = clamp8(round(acc_g / divisor) + offset)
            b = clamp8(round(acc_b / divisor) + offset)
            out[y][x] = create_pixel(r, g, b)
    return out


# Presets
K_BLUR_BOX = [1, 1, 1, 1, 1, 1, 1, 1, 1]          # divisor=9
K_SHARPEN = [0, -1, 0, -1, 5, -1, 0, -1, 0]
K_EDGE_SIMPLE = [0, -1, 0, -1, 4, -1, 0, -1, 0]


def adjust_brightness(image_data, delta=0):
    delta = int(delta)
    h, w = len(image_data), len(image_data[0])
    out = [[0]*w for _ in range(h)]
    for y in range(h):
        for x in range(w):
            px = image_data[y][x]
            r = clamp8(get_red(px) + delta)
            g = clamp8(get_green(px) + delta)
            b = clamp8(get_blue(px) + delta)
            out[y][x] = create_pixel(r, g, b)
    return out


def adjust_contrast(image_data, factor=1.0):
    factor = float(factor)
    h, w = len(image_data), len(image_data[0])
    out = [[0]*w for _ in range(h)]
    for y in range(h):
        for x in range(w):
            px = image_data[y][x]
            r = clamp8(128 + factor * (get_red(px) - 128))
            g = clamp8(128 + factor * (get_green(px) - 128))
            b = clamp8(128 + factor * (get_blue(px) - 128))
            out[y][x] = create_pixel(r, g, b)
    return out

# -----------------------------------------------------------------------------
# Smiley generator (for quick demo)
# -----------------------------------------------------------------------------


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


# -----------------------------------------------------------------------------
# Main
# -----------------------------------------------------------------------------

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

    # Strong validation so we never crash downstream
    if (not img) or (not isinstance(img, list)) or (
        img and not isinstance(img[0],
                               list)):
        print("Could not load image.\n"
              "- If it's a URL, use a DIRECT image link "
              "(ends with .jpg/.png).\n"
              "- If it's a local file, ensure the path exists: "
              + os.path.abspath(source))
        sys.exit(1)

    # Baseline outputs
    save_image(img,                          out("original.png"))
    save_image(invert_colors(img),           out("invert.png"))
    save_image(to_grayscale(img),            out("grayscale.png"))
    save_image(remove_green(img),            out("no_green.png"))
    save_image(swap_red_blue(img),           out("swap_rb.png"))
    save_image(posterize_keep_bits(img, 2),  out("posterize_2bits.png"))
    save_image(threshold_bw(img, 128),       out("threshold_128.png"))

    # Advanced outputs
    save_image(sepia(img),                         out("sepia.png"))
    save_image(gamma_correction(img, 2.2),         out("gamma_2_2.png"))
    save_image(apply_kernel(img, K_SHARPEN),       out("sharpen.png"))
    save_image(apply_kernel(img, K_EDGE_SIMPLE),   out("edges.png"))
    # Optional:
    # save_image(adjust_brightness(img, 20),       out("bright_plus20.png"))
    # save_image(adjust_contrast(img, 1.3),        out("contrast_1_3.png"))

    print(f"All outputs saved to: {OUTPUT_DIR}")
