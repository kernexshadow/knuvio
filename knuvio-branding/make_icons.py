"""Generate knuvio launcher icons and TV banner from the source artwork."""
import os
import sys

from PIL import Image

mark_src, banner_src, res_dir = sys.argv[1], sys.argv[2], sys.argv[3]


def save(img, rel, size):
    path = os.path.join(res_dir, rel)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    img.resize(size, Image.LANCZOS).save(path, optimize=True)
    print(rel, size)


def center_crop(img, ratio):
    w, h = img.size
    if w / h > ratio:
        nw = round(h * ratio)
        left = (w - nw) // 2
        return img.crop((left, 0, left + nw, h))
    nh = round(w / ratio)
    top = (h - nh) // 2
    return img.crop((0, top, w, top + nh))


mark = center_crop(Image.open(mark_src).convert("RGB"), 1)
for density, px in {"mdpi": 48, "hdpi": 72, "xhdpi": 96, "xxhdpi": 144, "xxxhdpi": 192}.items():
    save(mark, f"mipmap-{density}/ic_launcher.png", (px, px))
save(mark, "drawable/ic_launcher.png", (1080, 1080))
save(mark, "drawable/app_logo_mark.png", (1080, 1080))

banner = center_crop(Image.open(banner_src).convert("RGB"), 16 / 9)
save(banner, "mipmap-xhdpi/banner.png", (320, 180))
