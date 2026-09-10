"""Build the default social share card, img/og-cover.jpg.

Run once by hand; not part of the normal build.py run. Open Graph scrapers
(WhatsApp, Facebook, LinkedIn) crop to 1200x630, so crop deliberately here
rather than let them guess at our portrait hero.
"""
import os
from PIL import Image

SRC = 'img/orig/zonixa-heavy-320-gsm-round-neck-hoodies-with-logo.jpg'
DST = 'img/og-cover.jpg'
W, H = 1200, 630

im = Image.open(SRC).convert('RGB')
# The source is portrait and the garments sit in the upper half, so take the
# widest possible 1200:630 band and bias it upward instead of centring.
band = round(im.width * H / W)
top = round((im.height - band) * 0.28)
im = im.crop((0, top, im.width, top + band))
im = im.resize((W, H), Image.LANCZOS)
im.save(DST, 'JPEG', quality=82, optimize=True, progressive=True)

print(f'{DST}: {Image.open(DST).size[0]}x{Image.open(DST).size[1]}, '
      f'{os.path.getsize(DST)/1e3:.0f} KB')
