import os, glob
from PIL import Image

# Cards render ~300px wide, PDP/hero ~600px. Serve 700px wide — plenty for 2x
# on cards and 1x on the detail view, at a fraction of the weight.
TARGET_W = 700
before = after = 0
files = sorted(glob.glob('img/orig/*.jpg'))
for src in files:
    dst = 'img/' + os.path.basename(src)
    before += os.path.getsize(src)
    im = Image.open(src).convert('RGB')
    if im.width > TARGET_W:
        im = im.resize((TARGET_W, round(im.height * TARGET_W / im.width)), Image.LANCZOS)
    im.save(dst, 'JPEG', quality=82, optimize=True, progressive=True)
    after += os.path.getsize(dst)
print(f'{len(files)} images: {before/1e6:.1f} MB -> {after/1e6:.1f} MB')
print('new dimensions:', Image.open('img/zonixa-320-gsm-heavy-zip-hoodies.jpg').size)
