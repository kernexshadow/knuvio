"""knuvio wordmark (transparent) and themed launcher icon / banner variants."""
import colorsys
import os
import sys

import numpy as np
from PIL import Image
from scipy import ndimage

mark_src, banner_src, main_res, out_res, preview_dir = sys.argv[1:6]

# Gradient stops (K top -> K bottom-right), sampled from the upstream themed assets.
THEMES = {
    "arctic_blue": ((56, 200, 243), (73, 104, 249)),
    "gold": ((232, 180, 40), (254, 208, 73)),
    "graphite": ((225, 225, 225), (155, 155, 155)),
    "jade": ((89, 224, 115), (20, 208, 149)),
    "emerald": ((89, 224, 115), (20, 208, 149)),
    "rose_gold": ((217, 81, 241), (255, 140, 122)),
    "copper": None,  # sampled from the upstream copper launcher icon below
}


def load(path):
    return np.asarray(Image.open(path).convert("RGB")).astype(np.float64) / 255.0


def sample_copper():
    a = np.asarray(Image.open(os.path.join(main_res, "mipmap-xxxhdpi/ic_launcher_copper.png")).convert("RGB")).astype(int)
    top = a[55:70, 65:80].reshape(-1, 3).mean(0)
    right = a[90:105, 125:138].reshape(-1, 3).mean(0)
    return tuple(int(v) for v in top), tuple(int(v) for v in right)


THEMES["copper"] = sample_copper()


def rgb_to_hsv(img):
    r, g, b = img[..., 0], img[..., 1], img[..., 2]
    mx, mn = img.max(-1), img.min(-1)
    d = mx - mn
    h = np.zeros_like(mx)
    nz = d > 1e-6
    rm = nz & (mx == r)
    gm = nz & (mx == g) & ~rm
    bm = nz & ~rm & ~gm
    h[rm] = ((g - b)[rm] / d[rm]) % 6
    h[gm] = (b - r)[gm] / d[gm] + 2
    h[bm] = (r - g)[bm] / d[bm] + 4
    h = h * 60.0
    s = np.where(mx > 1e-6, d / np.maximum(mx, 1e-6), 0)
    return h, s, mx


def hsv_to_rgb(h, s, v):
    h = (h % 360) / 60.0
    i = np.floor(h).astype(int) % 6
    f = h - np.floor(h)
    p, q, t = v * (1 - s), v * (1 - s * f), v * (1 - s * (1 - f))
    out = np.zeros(h.shape + (3,))
    for k, (rr, gg, bb) in enumerate([(v, t, p), (q, v, p), (p, v, t), (p, q, v), (t, p, v), (v, p, q)]):
        m = i == k
        out[m] = np.stack([rr[m], gg[m], bb[m]], -1)
    return out


def recolor(img, theme, weight=None):
    """Map the K's cyan->magenta hue ramp onto the theme gradient, keeping shading."""
    c0, c1 = (np.array(c, dtype=np.float64) / 255.0 for c in THEMES[theme])
    h, s, v = rgb_to_hsv(img)
    t = np.clip((h - 185.0) / (300.0 - 185.0), 0, 1)[..., None]
    target = c0 * (1 - t) + c1 * t
    th, ts, tv = rgb_to_hsv(target)
    new = hsv_to_rgb(th, ts * np.clip(s / 0.85, 0, 1), np.clip(v * tv, 0, 1))
    if weight is None:
        return new
    w = weight[..., None]
    return new * w + img * (1 - w)


def colour_weight(img):
    """1 on saturated, bright pixels (the K and the glow), 0 on the navy background and white text."""
    _, s, v = rgb_to_hsv(img)
    return np.clip((v - 0.15) / 0.2, 0, 1) * np.clip((s - 0.25) / 0.2, 0, 1)


def matte(img):
    """Pull the K off its dark background: RGBA with straight (unpremultiplied) colour."""
    _, s, v = rgb_to_hsv(img)
    fg_guess = ndimage.binary_dilation(v > 0.25, iterations=12)
    bgw = (~fg_guess).astype(np.float64)
    bg = np.stack([ndimage.gaussian_filter(img[..., c] * bgw, 40) for c in range(3)], -1)
    bg /= np.maximum(ndimage.gaussian_filter(bgw, 40), 1e-6)[..., None]

    diff = np.abs(img - bg).max(-1)
    core = diff > 0.35
    dist, (iy, ix) = ndimage.distance_transform_edt(~core, return_indices=True)
    fg = img[iy, ix]
    num = ((img - bg) * (fg - bg)).sum(-1)
    den = np.maximum(((fg - bg) ** 2).sum(-1), 1e-6)
    alpha = np.clip(num / den, 0, 1)
    alpha[core] = 1
    alpha[dist > 4] = 0
    colour = np.where(core[..., None], img, fg)
    return colour, alpha


def to_image(rgb, alpha=None):
    rgb8 = (np.clip(rgb, 0, 1) * 255 + 0.5).astype(np.uint8)
    if alpha is None:
        return Image.fromarray(rgb8, "RGB")
    a8 = (np.clip(alpha, 0, 1) * 255 + 0.5).astype(np.uint8)
    return Image.fromarray(np.dstack([rgb8, a8]), "RGBA")


def save(img, rel, size=None):
    path = os.path.join(out_res, rel)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    (img.resize(size, Image.LANCZOS) if size else img).save(path, optimize=True)
    print(rel, size or img.size)


def center_crop(img, ratio):
    w, h = img.size
    if w / h > ratio:
        nw = round(h * ratio)
        return img.crop(((w - nw) // 2, 0, (w - nw) // 2 + nw, h))
    nh = round(w / ratio)
    return img.crop((0, (h - nh) // 2, w, (h - nh) // 2 + nh))


mark = load(mark_src)
banner = load(banner_src)

# ---- Layout proportions from the knuvio banner (K vs "nuvio" text) ----
_, bs, bv = rgb_to_hsv(banner)
text_mask = (bs < 0.15) & (bv > 0.7)
k_mask = (bs > 0.35) & (bv > 0.5)
ty, tx = np.where(text_mask)
ky, kx = np.where(k_mask)
k_h = ky.max() - ky.min()
ratio_text_h = (ty.max() - ty.min()) / k_h
ratio_gap = (tx.min() - kx.max()) / k_h
ratio_text_top = (ty.min() - ky.min()) / k_h
print("banner ratios: text_h %.3f gap %.3f text_top %.3f" % (ratio_text_h, ratio_gap, ratio_text_top))

# ---- Transparent K ----
k_rgb, k_alpha = matte(mark)
ys, xs = np.where(k_alpha > 0.02)
box = (xs.min(), ys.min(), xs.max() + 1, ys.max() + 1)
k_rgb = k_rgb[box[1]:box[3], box[0]:box[2]]
k_alpha = k_alpha[box[1]:box[3], box[0]:box[2]]

# ---- "nuvio" text from the upstream wordmark (same typeface, already transparent) ----
up = Image.open(os.path.join(main_res, "drawable/app_logo_wordmark.png")).convert("RGBA")
ua = np.asarray(up)
cols = np.where(ua[..., 3].max(0) > 0)[0]
gap_cols = [c for c in range(300, 420) if c not in set(cols)]
text_x0 = max(gap_cols) + 1
text = up.crop((text_x0, 0, up.width, up.height))
text = text.crop(text.getbbox())

W, H = up.size  # keep the upstream canvas so every layout behaves the same
k_target_h = H
text_h = round(k_target_h * ratio_text_h)
text_w = round(text.width * text_h / text.height)
k_w = round(k_rgb.shape[1] * k_target_h / k_rgb.shape[0])
gap = round(k_target_h * ratio_gap)
total = k_w + gap + text_w
scale = min(1.0, W / total)
k_target_h, k_w, gap, text_w, text_h = (round(v * scale) for v in (k_target_h, k_w, gap, text_w, text_h))
total = k_w + gap + text_w
x0 = (W - total) // 2
y0 = (H - k_target_h) // 2
text_img = text.resize((text_w, text_h), Image.LANCZOS)
text_y = y0 + round(k_target_h * ratio_text_top)
print("wordmark layout: K %dx%d gap %d text %dx%d x0 %d" % (k_w, k_target_h, gap, text_w, text_h, x0))


def wordmark(k_colour):
    canvas = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    k_img = to_image(k_colour, k_alpha).resize((k_w, k_target_h), Image.LANCZOS)
    canvas.alpha_composite(k_img, (x0, y0))
    canvas.alpha_composite(text_img, (x0 + k_w + gap, text_y))
    return canvas


previews = {}
previews["wordmark"] = wordmark(k_rgb)
save(previews["wordmark"], "drawable/app_logo_wordmark.png")
for theme in ("arctic_blue", "gold", "graphite", "jade", "rose_gold"):
    img = wordmark(recolor(k_rgb, theme))
    previews["wordmark_" + theme] = img
    save(img, f"drawable/app_logo_wordmark_{theme}.png")

# ---- Alternative launcher icons and banners ----
mark_sq = np.asarray(center_crop(to_image(mark), 1)).astype(np.float64) / 255.0
banner_169 = np.asarray(center_crop(to_image(banner), 16 / 9)).astype(np.float64) / 255.0
mark_w = colour_weight(mark_sq)
banner_w = colour_weight(banner_169)
for theme in ("arctic_blue", "emerald", "rose_gold", "copper", "graphite"):
    icon = to_image(recolor(mark_sq, theme, mark_w))
    for density, px in {"mdpi": 48, "hdpi": 72, "xhdpi": 96, "xxhdpi": 144, "xxxhdpi": 192}.items():
        save(icon, f"mipmap-{density}/ic_launcher_{theme}.png", (px, px))
    ban = to_image(recolor(banner_169, theme, banner_w))
    save(ban, f"mipmap-xhdpi/banner_{theme}.png", (320, 180))
    previews["icon_" + theme] = icon
    previews["banner_" + theme] = ban

# ---- Preview sheet ----
sheet = Image.new("RGB", (2 * 560 + 30, 3 * 190 + 40 + 2 * 230), (38, 38, 38))
order = ["wordmark", "wordmark_arctic_blue", "wordmark_gold", "wordmark_graphite", "wordmark_jade", "wordmark_rose_gold"]
for i, key in enumerate(order):
    im = previews[key].resize((540, 171), Image.LANCZOS)
    x, y = 10 + (i % 2) * 570, 10 + (i // 2) * 190
    sheet.paste(im, (x, y), im)
for i, theme in enumerate(("arctic_blue", "emerald", "rose_gold", "copper", "graphite")):
    x = 10 + i * 225
    sheet.paste(previews["icon_" + theme].resize((110, 110)), (x, 3 * 190 + 30))
    sheet.paste(previews["banner_" + theme].resize((215, 121)), (x, 3 * 190 + 150))
sheet.save(os.path.join(preview_dir, "variants_preview.png"))
# Wordmark on light background too, to check the matte edges.
light = Image.new("RGB", (W, H), (235, 235, 240))
light.paste(previews["wordmark"], (0, 0), previews["wordmark"])
light.save(os.path.join(preview_dir, "wordmark_on_light.png"))
