# Generates the static site from data/products.json.
# Run:  python data/build.py     (from D:\PanwarKnitwear)
#
# Visual system: "Mill & Thread" — see css/style.css for the design tokens.
import json, html, os

# ---------------------------------------------------------------------------
# Verified business facts. Sources: panwarknitwear.com and zonixa.com.
# Nothing here is invented — see CLAUDE.md "Content Accuracy".
# ---------------------------------------------------------------------------
BIZ = {
    'name': 'Panwar Knitwear',
    'city': 'Ludhiana',
    'region': 'Punjab',
    'pin': '141008',
    'country': 'India',
    'email': 'zonixa@panwarknitwear.com',
    'hours': 'Mon – Sat, 9:00 AM – 6:00 PM',
    'wa': '919815703769',
    'maps': 'https://maps.app.goo.gl/rrg4VPdpZcRvZTQZ6',
    'moq': '200 – 300 pieces',
    'sizes': 'M to 5XL',
}
PHONES = [
    ('B R Panwar',      'Factory Head',    '+91 98760 45457', '919876045457'),
    ('Rohitash Panwar', 'Digital Manager', '+91 98157 03769', '919815703769'),
    ('Prabhu Panwar',   'Factory Head',    '+91 99999 82998', '919999982998'),
]
FABRICS = ['Spun Fleece', 'Dry Fit', 'Honeycomb Lycra', '100% Cotton',
           'Cotton Lycra', 'NS Bonded', 'Russian Fleece', 'Sherpa']
PROFILES = [
    ('Google Maps', BIZ['maps']),
    ('IndiaMART',   'https://www.indiamart.com/panwar-knitwear'),
    ('JustDial',    'https://jsdl.in/DT-40JPFSTDR23'),
    ('Instagram',   'https://www.instagram.com/panwarknitwear'),
    ('Facebook',    'https://www.facebook.com/Panwarknitwear1'),
    ('LinkedIn',    'https://www.linkedin.com/posts/a-rohitash-panwar-7b3684114_'
                    'panwarknitwear-zonixa-mspsports-activity-7218811071321497600-Dvj6'),
]
CATEGORIES = [
    ('t-shirts',    'T-Shirts',      'zonixa-pc-cotton-half-sleeve-t-shirts.jpg'),
    ('polo',        'Polo / Collar', 'zonixa-dry-fit-ben-collar-half-sleeve-t-shirts.jpg'),
    ('printed',     'Printed',       'zonixa-digital-print-t-shirts.jpg'),
    ('hoodies',     'Hoodies',       'zonixa-320-gsm-heavy-zip-hoodies.jpg'),
    ('sweatshirts', 'Sweatshirts',   'zonixas-feather-bonding-sweatshirts.jpg'),
    ('jackets',     'Jackets',       'zonixa-shape-bonding-ben-collar-jackets.jpg'),
]
MSP_CATS = [
    ('Track Pants',    'Athletic fit bottomwear'),
    ('Lowers',         'Everyday and gym lowers'),
    ('Shorts',         'Summer and sports shorts'),
    ('Capri / Nikkar', 'Half and three-quarter lengths'),
]
# Production sequence for the Manufacturing section. Every line is drawn from
# facts the business already publishes — the fabric list, the in-house Ludhiana
# facility, MOQ and size range, custom tag & polybag packing, and quality checks
# before dispatch. No specific process steps are invented.
PROCESS = [
    ('Fabric',        'Selected per article and season, across a wide GSM range.', None),
    ('Production',    'In-house at our own Ludhiana facility. No middlemen.',
     'moq'),                                  # -> MOQ + size range from BIZ
    ('Customization', 'Your own tags and polybag packing on bulk orders.',
     ['Custom tag', 'Polybag packing']),
    ('Quality',       'Quality checked, then dispatched from Ludhiana.',
     ['Quality checked', 'Dispatch from Ludhiana']),
]

TICKER = ['Knitwear Manufacturer', 'Ludhiana · Punjab', 'Bulk Orders From 200 Pcs',
          'Sizes M–5XL', 'Factory Direct', 'GST Extra', 'Custom Tag & Polybag',
          'Zonixa', 'MSP Sports']

E = lambda s: html.escape(str(s), quote=True)

def wa(msg):
    from urllib.parse import quote
    return 'https://wa.me/%s?text=%s' % (BIZ['wa'], quote(msg))

# --- Inline SVG icons -------------------------------------------------------
ICON = {
 'phone': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M22 16.9v3a2 2 0 0 1-2.2 2 19.8 19.8 0 0 1-8.6-3.1 19.5 19.5 0 0 1-6-6A19.8 19.8 0 0 1 2.1 4.2 2 2 0 0 1 4.1 2h3a2 2 0 0 1 2 1.7c.1 1 .4 1.9.7 2.8a2 2 0 0 1-.5 2.1L8.1 9.9a16 16 0 0 0 6 6l1.3-1.3a2 2 0 0 1 2.1-.4c.9.3 1.8.6 2.8.7a2 2 0 0 1 1.7 2z"/></svg>',
 'whatsapp': '<svg viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M17.5 14.4c-.3-.2-1.7-.9-2-1-.3-.1-.5-.2-.7.1s-.7 1-.9 1.2-.4.2-.7.1a8.2 8.2 0 0 1-2.4-1.5 9 9 0 0 1-1.7-2.1c-.2-.3 0-.5.1-.6l.5-.6.3-.5v-.5l-1-2.3c-.2-.6-.5-.5-.7-.5h-.6a1.1 1.1 0 0 0-.8.4A3.3 3.3 0 0 0 5.9 9c0 1.4 1 2.8 1.2 3a11.5 11.5 0 0 0 4.4 3.9c.6.3 1.1.4 1.5.5a3.6 3.6 0 0 0 1.6.1 2.9 2.9 0 0 0 1.9-1.4 2.4 2.4 0 0 0 .2-1.3zM12 2a10 10 0 0 0-8.5 15.3L2 22l4.8-1.4A10 10 0 1 0 12 2m0 1.8a8.2 8.2 0 0 1 6 13.9 8.1 8.1 0 0 1-9.9 1.3l-.4-.2-2.9.8.8-2.8-.2-.4A8.2 8.2 0 0 1 12 3.8"/></svg>',
 'quote': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><path d="M14 2v6h6M16 13H8M16 17H8M10 9H8"/></svg>',
 'mail': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><rect x="2" y="4" width="20" height="16" rx="1"/><path d="m22 7-10 6L2 7"/></svg>',
 'pin': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M20 10c0 6-8 12-8 12s-8-6-8-12a8 8 0 0 1 16 0z"/><circle cx="12" cy="10" r="3"/></svg>',
 'clock': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><circle cx="12" cy="12" r="10"/><path d="M12 6v6l4 2"/></svg>',
 'arrow': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M5 12h14M13 6l6 6-6 6"/></svg>',
}

FONTS = ('https://fonts.googleapis.com/css2?'
         'family=Bricolage+Grotesque:opsz,wght@12..96,600;12..96,800'
         '&family=DM+Mono:wght@400;500'
         '&family=Inter+Tight:wght@400;500;600&display=swap')

# --- Shared chrome ----------------------------------------------------------
def head(title, desc, rel='', canonical='', extra='', intro=False):
    intro_attr = ' data-intro="on"' if intro else ''
    return f"""<!DOCTYPE html>
<html lang="en" data-wa="{BIZ['wa']}"{intro_attr}>
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{E(title)}</title>
<meta name="description" content="{E(desc)}">
<meta name="robots" content="index, follow">
<link rel="canonical" href="https://panwarknitwear.com/{canonical}">
<meta property="og:title" content="{E(title)}">
<meta property="og:description" content="{E(desc)}">
<meta property="og:type" content="website">
<link rel="icon" href="{rel}img/logo.png">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="{FONTS}">
<link rel="stylesheet" href="{rel}css/style.css">
<script>
/* Stage animated elements only when motion is welcome. main.js removes this
   class again if GSAP is unavailable, so content can never stay hidden. */
try {{
  var r = document.documentElement;
  if (matchMedia('(prefers-reduced-motion: no-preference)').matches) {{
    r.classList.add('anim');
    /* Arm the brand intro only on the homepage, once per tab session, and only
       when motion is welcome. The timeout is a self-contained failsafe: if
       main.js or GSAP never arrives, the overlay still clears itself. */
    if (r.dataset.intro === 'on' && !sessionStorage.getItem('pk-intro')) {{
      r.classList.add('intro-armed');
    }}
    /* Self-contained failsafe. main.js normally clears both of these far
       earlier; this covers the case where main.js itself never arrives, so a
       total script failure still degrades to a fully visible page. */
    window.__pkFailsafe = setTimeout(function () {{
      r.classList.remove('intro-armed');
      r.classList.remove('anim');
    }}, 6000);
  }}
}} catch (e) {{}}
</script>
<script src="https://cdn.jsdelivr.net/npm/gsap@3.12.5/dist/gsap.min.js" defer></script>
<script src="https://cdn.jsdelivr.net/npm/gsap@3.12.5/dist/ScrollTrigger.min.js" defer></script>
<script src="{rel}js/main.js" defer></script>
{extra}</head>
<body>
"""

def header(rel='', current='', solid=True):
    def item(href, label, key):
        cur = ' aria-current="page"' if key == current else ''
        return f'<li><a href="{rel}{href}"{cur}>{label}</a></li>'
    cls = 'site-header site-header--solid' if solid else 'site-header'
    return f"""<header class="{cls}">
<div class="wrap header-inner">
<a class="brand" href="{rel}index.html" aria-label="Panwar Knitwear — home">
<img src="{rel}img/logo.png" alt="Panwar Knitwear — Zonixa &amp; MSP Sports" width="168" height="40">
</a>
<button class="nav-toggle" type="button" aria-expanded="false" aria-controls="main-nav">
<span></span><span class="visually-hidden">Menu</span>
</button>
<nav class="main-nav" id="main-nav" aria-label="Main">
<ul>
{item('index.html', 'Index', 'home')}
{item('products.html', 'Products', 'products')}
{item('about.html', 'About', 'about')}
{item('contact.html', 'Contact', 'contact')}
</ul>
</nav>
<div class="header-cta">
<a class="btn btn--onDark btn--sm" href="tel:+919876045457">{ICON['phone']} Call</a>
<a class="btn btn--wa btn--sm" href="{wa('Hello Panwar Knitwear, I would like a wholesale enquiry.')}" target="_blank" rel="noopener">{ICON['whatsapp']} WhatsApp</a>
</div>
</div>
</header>
"""

def intro(hero_image):
    """Brand intro overlay (homepage only): spec sheet -> product -> business.

    Uses the SAME image as the hero, so the hand-off is one cached request and
    the crop appears to expand into the hero visual. Built from <p> elements,
    not headings, so the page's heading hierarchy is untouched, and aria-hidden
    so assistive tech skips it entirely."""
    specs = ''.join(f'<li>{E(x)}</li>' for x in ('Fabric', 'GSM', 'Sizes', 'Bulk'))
    return f"""<div class="intro" id="intro" aria-hidden="true">
<div class="intro-inner">
<p class="intro-brand"><span class="l"><span>{BIZ['name']}</span></span></p>
<p class="intro-loc">{BIZ['city']} / {BIZ['country']}</p>
<ul class="intro-specs">{specs}</ul>
<figure class="intro-media">
<img src="img/{hero_image}" alt="" width="700" height="818" decoding="async">
</figure>
<p class="intro-line">
<span class="l"><span>Made for bulk.</span></span>
<span class="l"><span>Built for business.</span></span>
</p>
<p class="intro-cue"><span>Scroll to enter</span><i></i></p>
</div>
</div>
"""

def ticker():
    run = ''.join(f'<span>{E(t)}</span>' for t in TICKER)
    # Duplicated once so the -50% keyframe loops seamlessly
    return f"""<div class="ticker" aria-hidden="true">
<div class="ticker-track">{run}{run}</div>
</div>
"""

def sec_label(num, label):
    return f'<p class="sec-label"><span>{num}</span> <b>&mdash; {E(label)}</b></p>'

def action_bar(rel=''):
    return f"""<nav class="action-bar" aria-label="Quick contact">
<a href="tel:+919876045457">{ICON['phone']}Call</a>
<a class="is-whatsapp" href="{wa('Hello Panwar Knitwear, I would like a wholesale enquiry.')}" target="_blank" rel="noopener">{ICON['whatsapp']}WhatsApp</a>
<a class="is-quote" href="{rel}contact.html#quote">{ICON['quote']}Quote</a>
</nav>
"""

# Shipped hidden and shown by main.js only once something is selected, so a
# visitor without JS never sees a bar that cannot do anything.
def shortlist_bar():
    return f"""<div class="shortlist-bar" id="shortlist" hidden>
<div class="wrap shortlist-inner">
<p class="shortlist-count" id="shortlist-count" aria-live="polite"></p>
<div class="shortlist-actions">
<button type="button" class="shortlist-clear" id="shortlist-clear">Clear</button>
<a class="btn btn--wa btn--sm" id="shortlist-send" href="#" target="_blank" rel="noopener">{ICON['whatsapp']} Enquire on WhatsApp</a>
</div>
</div>
</div>
"""

def footer(rel=''):
    phones = '\n'.join(
        f'<li><a href="tel:+91{p[3][2:]}">{E(p[2])}</a></li>' for p in PHONES)
    cats = '\n'.join(f'<li><a href="{rel}products.html#{k}">{E(l)}</a></li>' for k, l, _ in CATEGORIES)
    profs = '\n'.join(f'<li><a href="{E(u)}" target="_blank" rel="noopener">{E(n)}</a></li>' for n, u in PROFILES)
    return f"""{shortlist_bar()}{action_bar(rel)}
<footer class="site-footer">
<div class="wrap">
<div class="footer-grid">
<div>
<img class="footer-logo" src="{rel}img/logo.png" alt="Panwar Knitwear" width="160" height="40">
<p class="footer-about">Knitwear manufacturer and wholesale supplier in Ludhiana, Punjab. Home to <strong>ZONIXA</strong> and <strong>MSP Sports</strong>.</p>
<address class="footer-address">
{BIZ['name']}<br>
{BIZ['city']}, {BIZ['region']} {BIZ['pin']}<br>
{BIZ['country']}
</address>
</div>
<div>
<h3>Products</h3>
<ul>{cats}
<li><a href="{rel}products.html">All products</a></li>
</ul>
</div>
<div>
<h3>Contact</h3>
<ul>
{phones}
<li><a href="mailto:{BIZ['email']}">{BIZ['email']}</a></li>
<li>{BIZ['hours']}</li>
</ul>
</div>
<div>
<h3>Find us on</h3>
<ul>{profs}</ul>
</div>
</div>
<div class="footer-bottom">
<span>&copy; 2024 {BIZ['name']}</span>
<span>Ludhiana &middot; Punjab &middot; India</span>
</div>
</div>
</footer>
</body>
</html>
"""

LOCALBUSINESS_LD = json.dumps({
    "@context": "https://schema.org",
    "@type": ["LocalBusiness", "ClothingStore"],
    "name": BIZ['name'],
    "description": "Knitwear manufacturer and wholesale supplier in Ludhiana, Punjab. "
                   "T-shirts, polos, hoodies, sweatshirts and jackets under the ZONIXA brand, "
                   "and bottomwear under MSP Sports.",
    "url": "https://panwarknitwear.com/",
    "email": BIZ['email'],
    "telephone": ["+91" + p[3][2:] for p in PHONES],
    "address": {"@type": "PostalAddress", "addressLocality": BIZ['city'],
                "addressRegion": BIZ['region'], "postalCode": BIZ['pin'], "addressCountry": "IN"},
    "areaServed": "IN",
    "openingHours": "Mo-Sa 09:00-18:00",
    "hasMap": BIZ['maps'],
    "brand": [{"@type": "Brand", "name": "ZONIXA"}, {"@type": "Brand", "name": "MSP Sports"}],
    "sameAs": [u for _, u in PROFILES],
}, indent=1)

def ld(obj):
    return '<script type="application/ld+json">\n' + obj + '\n</script>\n'

# --- Catalogue plate --------------------------------------------------------
def plate(p, rel=''):
    msg = 'Hello Panwar Knitwear, I am interested in "%s". Please share wholesale details.' % p['name']
    spec = E(p['cardspec']) if p['cardspec'] else 'Details on enquiry'
    return f"""<li class="plate" data-anim="plate" data-categories="{E(' '.join(p['categories']))}" data-slug="{E(p['slug'])}" data-name="{E(p['name'])}">
<span class="plate-media">
<span class="plate-num">{p['plate']}</span>
<img src="{rel}img/{p['image']}" alt="{E(p['name'])}" width="700" height="818" loading="lazy" decoding="async">
</span>
<span class="plate-body">
<span class="plate-title"><a href="{rel}product/{p['slug']}.html">{E(p['name'])}</a></span>
<span class="plate-spec">{spec}</span>
<a class="plate-cta" href="{wa(msg)}" target="_blank" rel="noopener">{ICON['whatsapp']} Enquire</a>
</span>
</li>"""

def cta_band(rel='', heading='Ready to place a bulk order?',
             text='Send your article and quantity on WhatsApp — we reply with a quote the same working day.'):
    return f"""<div class="wrap section section--tight">
<div class="cta-band" data-anim="up">
<div>
<h2>{heading}</h2>
<p>{text}</p>
</div>
<div class="btn-row">
<a class="btn btn--wa" href="{wa('Hello Panwar Knitwear, I would like a wholesale quote.')}" target="_blank" rel="noopener">{ICON['whatsapp']} WhatsApp</a>
<a class="btn btn--onDark" href="tel:+919876045457">{ICON['phone']} Call</a>
<a class="btn btn--onDark" href="{rel}contact.html#quote">{ICON['quote']} Get Quote</a>
</div>
</div>
</div>"""

def quote_form():
    opts = ''.join(f'<option>{E(l)}</option>' for _, l, _ in CATEGORIES)
    return f"""<form class="form-card" id="quote-form" action="mailto:{BIZ['email']}" method="post" enctype="text/plain">
<h2>Request a quote</h2>
<div class="field-row">
<div class="field"><label for="q-name">Your name</label><input id="q-name" name="Name" type="text" autocomplete="name" required></div>
<div class="field"><label for="q-biz">Business name</label><input id="q-biz" name="Business" type="text" autocomplete="organization" required></div>
</div>
<div class="field-row">
<div class="field"><label for="q-wa">WhatsApp number</label><input id="q-wa" name="WhatsApp" type="tel" inputmode="tel" autocomplete="tel" required></div>
<div class="field"><label for="q-city">City / State</label><input id="q-city" name="City" type="text" autocomplete="address-level2" required></div>
</div>
<div class="field-row">
<div class="field"><label for="q-prod">Product interest</label>
<select id="q-prod" name="Product"><option value="">Select a category</option>{opts}<option>MSP Sports bottomwear</option><option>Other / mixed</option></select></div>
<div class="field"><label for="q-qty">Estimated quantity</label>
<select id="q-qty" name="Quantity"><option value="">Select a range</option><option>200 – 500 pieces</option><option>500 – 1,000 pieces</option><option>1,000 – 2,000 pieces</option><option>2,000 – 5,000 pieces</option><option>5,000+ pieces</option></select></div>
</div>
<button class="btn btn--rust btn--block" type="submit">{ICON['quote']} Send enquiry</button>
<p class="form-note">Minimum order {BIZ['moq']}. Prefer to talk? <a href="{wa('Hello Panwar Knitwear, I would like a wholesale quote.')}" target="_blank" rel="noopener">Message us on WhatsApp</a>.</p>
</form>"""

def contact_rows():
    items = ''.join(f"""<li><a class="contact-item" href="tel:+91{p[3][2:]}">
<span class="ic">{ICON['phone']}</span>
<span><b>{E(p[2])}</b><small>{E(p[0])} &middot; {E(p[1])}</small></span></a></li>""" for p in PHONES)
    return f"""<ul class="contact-list">
{items}
<li><a class="contact-item" href="{wa('Hello Panwar Knitwear, I would like a wholesale enquiry.')}" target="_blank" rel="noopener">
<span class="ic">{ICON['whatsapp']}</span>
<span><b>WhatsApp</b><small>Fastest route for bulk enquiries</small></span></a></li>
<li><a class="contact-item" href="mailto:{BIZ['email']}">
<span class="ic">{ICON['mail']}</span>
<span><b>{BIZ['email']}</b><small>Email enquiries</small></span></a></li>
<li><a class="contact-item" href="{BIZ['maps']}" target="_blank" rel="noopener">
<span class="ic">{ICON['pin']}</span>
<span><b>{BIZ['city']}, {BIZ['region']} {BIZ['pin']}</b><small>View on Google Maps</small></span></a></li>
<li><div class="contact-item">
<span class="ic">{ICON['clock']}</span>
<span><b>{BIZ['hours']}</b><small>Business hours</small></span></div></li>
</ul>"""

# ---------------------------------------------------------------------------
products = json.load(open('data/products.json', encoding='utf-8'))
for i, p in enumerate(products, 1):
    p['plate'] = f'{i:02d}'
by_slug = {p['slug']: p for p in products}

# --- index.html -------------------------------------------------------------
def build_index():
    hero_p = by_slug['zonixa-heavy-320-gsm-round-neck-hoodies-with-logo']

    cats = '\n'.join(f"""<a class="cat-row" href="products.html#{k}">
<span class="cat-idx">{i:02d}</span>
<span class="cat-name">{E(l)}</span>
<span class="cat-thumb"><img src="img/{img}" alt="" width="700" height="818" loading="lazy" decoding="async"></span>
<span class="cat-go">{ICON['arrow']}</span>
</a>""" for i, (k, l, img) in enumerate(CATEGORIES, 1))

    featured = [by_slug[s] for s in (
        'zonixa-320-gsm-heavy-zip-hoodies',
        'zonixa-dry-fit-ben-collar-half-sleeve-t-shirts',
        'zonixa-digital-print-t-shirts',
        'zonixas-feather-bonding-sweatshirts',
        'zonixa-shape-bonding-ben-collar-jackets',
        'zonixa-pc-cotton-half-sleeve-t-shirts',
    )]
    plates = '\n'.join(plate(p) for p in featured)

    msp = '\n'.join(f"""<a class="msp-tile" href="{wa('Hello Panwar Knitwear, I would like details on MSP Sports %s.' % n)}" target="_blank" rel="noopener">
<span><b>{E(n)}</b><small>{E(d)}</small></span>
<span class="tlink">Enquire {ICON['arrow']}</span>
</a>""" for n, d in MSP_CATS)

    odo = ''.join(f'<span>{i:02d}</span>' for i in range(1, len(PROCESS) + 1))
    stage_html = []
    for i, (nm, desc, meta) in enumerate(PROCESS, 1):
        if meta is None:
            chips = FABRICS                                  # the real fabric list
        elif meta == 'moq':
            chips = ['MOQ ' + BIZ['moq'], 'Sizes ' + BIZ['sizes']]   # single source
        else:
            chips = meta
        chip_html = ''.join(f'<li>{E(x)}</li>' for x in chips)
        stage_html.append(f"""<li class="proc-item" data-stage="{i-1}">
<span class="proc-idx">{i:02d}</span>
<h3 class="proc-name">{E(nm)}</h3>
<p class="proc-desc">{E(desc)}</p>
<ul class="proc-meta">{chip_html}</ul>
</li>""")
    stages = chr(10).join(stage_html)

    swatches = '\n'.join(f"""<div class="swatch-tile">
<span class="swatch-idx">{i:02d}</span>
<span class="swatch-name">{E(f)}</span>
</div>""" for i, f in enumerate(FABRICS, 1))

    return (head(
        'Knitwear Manufacturer & Wholesale Supplier in Ludhiana | Panwar Knitwear',
        'Panwar Knitwear is a Ludhiana-based knitwear manufacturer and wholesale supplier. '
        'T-shirts, polos, hoodies, sweatshirts and jackets under ZONIXA, and bottomwear under '
        'MSP Sports. Bulk orders from 200 pieces. Call or WhatsApp for a quote.',
        canonical='', extra=ld(LOCALBUSINESS_LD), intro=True)
    + intro(hero_p['image'])
    + header(current='home', solid=False)
    + f"""<main>

<section class="hero">
<div class="wrap hero-inner">
<p class="hero-rail" data-anim="fade">Ludhiana &middot; Punjab &middot; India</p>
<div class="hero-grid">
<div class="hero-copy">
<h1 class="hero-title t-hero" data-anim="fade">
<span class="line"><span>Knitwear</span></span>
<span class="line"><span>manufacturer &amp;</span></span>
<span class="line"><span>wholesale supplier</span></span>
<span class="line"><span>in <em>Ludhiana</em></span></span>
</h1>
<p class="lede" data-anim="fade">We manufacture T-shirts, polos, hoodies, sweatshirts and jackets under <strong>ZONIXA</strong>, and track pants, lowers and shorts under <strong>MSP Sports</strong> — factory direct to retailers, wholesalers and distributors across India.</p>
<div class="btn-row">
<a class="btn btn--wa" data-anim="cta" href="{wa('Hello Panwar Knitwear, I would like a wholesale enquiry.')}" target="_blank" rel="noopener">{ICON['whatsapp']} WhatsApp Enquiry</a>
<a class="btn btn--onDark" data-anim="cta" href="tel:+919876045457">{ICON['phone']} Call Now</a>
<a class="btn btn--onDark" data-anim="cta" href="contact.html#quote">{ICON['quote']} Get Quote</a>
</div>
</div>
<div class="hero-media">
<figure data-anim="fade">
<img src="img/{hero_p['image']}" alt="Zonixa heavy 320 GSM round neck hoodies manufactured by Panwar Knitwear, Ludhiana" width="700" height="818" fetchpriority="high" decoding="async">
<figcaption class="hero-tag">Zonixa &middot; 320 GSM Heavy Hoodies</figcaption>
</figure>
</div>
</div>
<div class="hero-foot">
<span data-anim="fade">MOQ {BIZ['moq']}</span>
<span data-anim="fade">Sizes {BIZ['sizes']}</span>
<span data-anim="fade">GST Extra</span>
<span data-anim="fade">Dispatch from Ludhiana</span>
</div>
</div>
</section>

{ticker()}

<section class="section" id="range">
<div class="wrap">
<div class="sec-head sec-head--split" data-anim="up">
{sec_label('01', 'Range')}
<h2 class="t-section">Shop by<br>category</h2>
<a class="tlink" href="products.html">All 29 products {ICON['arrow']}</a>
</div>
<div class="cat-list" data-anim="up">
{cats}
</div>
</div>
</section>

<section class="section panel brand-band" id="zonixa">
<div class="wrap">
<div class="sec-head sec-head--split" data-anim="up">
{sec_label('02', 'Brand')}
<div>
<h2 class="t-section">ZONIXA</h2>
<p class="brand-sig">A Panwar Knitwear brand &mdash; topwear</p>
</div>
<a class="tlink" href="products.html">View catalogue {ICON['arrow']}</a>
</div>
<p class="lede" data-anim="up" style="margin-bottom:2.5rem">Round neck and collar T-shirts, printed tees, sweatshirts, hoodies and jackets — summer cottons and dry fit through to 320 GSM winter fleece.</p>
<ul class="plates plates--editorial">
{plates}
</ul>
</div>
</section>

<section class="section panel panel--olive brand-band" id="msp-sports">
<div class="wrap">
<div class="sec-head" data-anim="up">
{sec_label('03', 'Brand')}
<h2 class="t-section">MSP Sports</h2>
<p class="brand-sig">A Panwar Knitwear brand &mdash; bottomwear</p>
<p class="lede" style="margin-top:1.25rem">Track pants, lowers, shorts and capri for sportswear retailers and wholesalers. Message us and we will share the current range.</p>
</div>
<div class="msp-tiles" data-anim="up">
{msp}
</div>
</div>
</section>

<section class="section section--sand" id="manufacturing">
<div class="wrap">
<div class="sec-head" data-anim="up">
{sec_label('04', 'Manufacturing')}
<h2 class="t-section">From material<br>to finished<br>apparel.</h2>
</div>
<div class="proc" data-proc>
<div class="proc-top" data-anim="up">
<p class="proc-caption">Stage <b id="proc-current">01</b> / 04</p>
<div class="proc-odo" aria-hidden="true"><div class="proc-odo-track">{odo}</div></div>
</div>
<ol class="proc-stages">
<span class="proc-fill" aria-hidden="true"></span>
{stages}
</ol>
</div>

<div class="figures" data-anim="up" style="margin-top:clamp(2.5rem,5vw,4rem)">
<div class="figure-cell"><b>15+</b><span>Years manufacturing</span></div>
<div class="figure-cell"><b>1000+</b><span>Distributors supplied</span></div>
<div class="figure-cell"><b>200</b><span>Minimum order pcs</span></div>
</div>
</div>
</section>

<section class="section panel" id="bulk">
<div class="wrap">
<div class="split">
<div data-anim="up">
{sec_label('05', 'Bulk orders')}
<h2 class="t-section">What wholesale<br>buyers need<br>to know</h2>
<div class="hero-foot" style="margin-top:2rem">
<span>Minimum order {BIZ['moq']}</span>
<span>Sizes {BIZ['sizes']}</span>
<span>GST extra</span>
<span>Factory-direct pricing</span>
<span>Dispatch from Ludhiana</span>
<span>Custom tag &amp; polybag</span>
</div>
<div class="btn-row" style="margin-top:2rem">
<a class="btn btn--wa" href="{wa('Hello Panwar Knitwear, I would like a wholesale quote.')}" target="_blank" rel="noopener">{ICON['whatsapp']} WhatsApp us</a>
<a class="btn btn--onDark" href="contact.html">All contact details</a>
</div>
</div>
<div id="quote" data-anim="up">
{quote_form()}
</div>
</div>
</div>
</section>

</main>
""" + footer())

# --- products.html ----------------------------------------------------------
def build_products():
    chips = '<button class="chip" type="button" data-filter="all" aria-pressed="true">All</button>\n'
    chips += '\n'.join(f'<button class="chip" type="button" data-filter="{k}" aria-pressed="false">{E(l)}</button>'
                       for k, l, _ in CATEGORIES)
    plates = '\n'.join(plate(p) for p in products)
    return (head(
        'Wholesale T-Shirts, Hoodies & Sweatshirts | Panwar Knitwear, Ludhiana',
        'Browse the full ZONIXA range from Panwar Knitwear, Ludhiana — T-shirts, polos, printed '
        'tees, hoodies, sweatshirts and jackets. Filter by category and enquire on WhatsApp for '
        'bulk wholesale prices.',
        canonical='products.html')
    + header(current='products')
    + f"""<main>
<div class="wrap"><p class="breadcrumb"><a href="index.html">Index</a> / Products</p></div>

<section class="section section--tight">
<div class="wrap">
<div class="sec-head">
{sec_label('01', 'Catalogue')}
<h1 class="t-section">Zonixa product<br>catalogue</h1>
<p class="lede">{len(products)} articles currently listed. Price on enquiry — minimum order {BIZ['moq']}, GST extra.</p>
</div>

<div class="filters" role="group" aria-label="Filter products by category">
{chips}
</div>
<p class="filter-count" id="filter-count" aria-live="polite">{len(products)} Products</p>

<h2 class="visually-hidden">Product list</h2>
<ul class="plates">
{plates}
</ul>
</div>
</section>

{cta_band()}
</main>
""" + footer())

# --- product detail ---------------------------------------------------------
def build_product(p):
    msg = 'Hello Panwar Knitwear, I am interested in "%s". Please share wholesale price and MOQ details.' % p['name']

    rows = []
    for s in p['specs']:
        label, value = s['label'], s['value']
        if isinstance(value, list):
            body = '<ul class="chiplist">' + ''.join(f'<li>{E(v)}</li>' for v in value) + '</ul>'
        else:
            body = E(value)
        rows.append(f'<div><dt>{E(label)}</dt><dd>{body}</dd></div>')
    if p['colors']:
        sw = ''.join(f'<span class="swatch" style="background:{E(c)}"></span>' for c in p['colors'])
        rows.append(f'<div><dt>Colours</dt><dd><div class="swatches">{sw}</div></dd></div>')
    rows.append(f'<div><dt>Minimum order</dt><dd>{BIZ["moq"]}</dd></div>')
    rows.append('<div><dt>Price</dt><dd>On enquiry &middot; GST extra</dd></div>')

    desc = '\n'.join(f'<p>{E(par)}</p>' for par in p['description'].split('\n') if par.strip())

    cat = p['categories'][0]
    related = [q for q in products if q['slug'] != p['slug'] and cat in q['categories']][:4]
    if len(related) < 4:
        related += [q for q in products if q['slug'] != p['slug'] and q not in related][:4 - len(related)]
    rel_plates = '\n'.join(plate(q, rel='../') for q in related)

    product_ld = json.dumps({
        "@context": "https://schema.org",
        "@type": "Product",
        "name": p['name'],
        "image": f"https://panwarknitwear.com/img/{p['image']}",
        "description": p['description'].split('\n')[0][:300],
        "brand": {"@type": "Brand", "name": "ZONIXA"},
        "manufacturer": {"@type": "Organization", "name": BIZ['name'],
                         "address": {"@type": "PostalAddress", "addressLocality": BIZ['city'],
                                     "addressRegion": BIZ['region'], "addressCountry": "IN"}},
        "category": cat,
    }, indent=1)

    meta = p['description'].split('\n')[0][:150].rsplit(' ', 1)[0]
    return (head(
        f"{p['name']} | Wholesale from Panwar Knitwear, Ludhiana",
        f"{meta}… Available for bulk wholesale from Panwar Knitwear, Ludhiana. "
        f"Minimum order {BIZ['moq']}. Enquire on WhatsApp.",
        rel='../', canonical=f'product/{p["slug"]}.html', extra=ld(product_ld))
    + header(rel='../', current='products')
    + f"""<main>
<div class="wrap"><p class="breadcrumb"><a href="../index.html">Index</a> / <a href="../products.html">Products</a> / {E(p['name'])}</p></div>

<section class="section section--tight">
<div class="wrap pdp">
<figure class="pdp-media">
<figcaption class="pdp-plate">Plate {p['plate']} &middot; Zonixa</figcaption>
<img src="../img/{p['image']}" alt="{E(p['name'])} — wholesale knitwear manufactured by Panwar Knitwear, Ludhiana" width="700" height="818" fetchpriority="high" decoding="async">
</figure>
<div class="pdp-info">
<h1 class="t-sub">{E(p['name'])}</h1>

<dl class="specs">
{chr(10).join(rows)}
</dl>

<div class="enquiry-box" data-slug="{E(p['slug'])}" data-name="{E(p['name'])}">
<span class="mono">Price on enquiry</span>
<p>Send us the article and quantity — we reply with wholesale rates.</p>
<div class="btn-row">
<a class="btn btn--wa" href="{wa(msg)}" target="_blank" rel="noopener">{ICON['whatsapp']} Enquire on WhatsApp</a>
<a class="btn btn--onDark" href="tel:+919876045457">{ICON['phone']} Call Now</a>
<a class="btn btn--onDark" href="../contact.html#quote">{ICON['quote']} Get Quote</a>
</div>
</div>

<div class="pdp-desc">
<h2>Product description</h2>
{desc}
</div>
</div>
</div>
</section>

<section class="section section--sand">
<div class="wrap">
<div class="sec-head sec-head--split" data-anim="up">
{sec_label('02', 'Also in this range')}
<h2 class="t-sub">Similar products</h2>
<a class="tlink" href="../products.html">View all {ICON['arrow']}</a>
</div>
<ul class="plates">
{rel_plates}
</ul>
</div>
</section>
</main>
""" + footer(rel='../'))

# --- about.html -------------------------------------------------------------
def build_about():
    swatches = '\n'.join(f"""<div class="swatch-tile">
<span class="swatch-idx">{i:02d}</span>
<span class="swatch-name">{E(f)}</span>
</div>""" for i, f in enumerate(FABRICS, 1))
    people = [
        ('Mohar Singh Panwar', 'Founder &amp; promoter — business vision and strategy'),
        ('Prabhu Panwar &amp; Bhala Ram Panwar', 'Co-founders — production, quality control and dispatch'),
        ('Rohitash Panwar', 'Digital manager — online presence and buyer enquiries'),
    ]
    leaders = '\n'.join(f"""<div class="cat-row">
<span class="cat-idx">{i:02d}</span>
<span>
<span class="cat-name" style="font-size:clamp(1.2rem,1rem + .9vw,1.75rem)">{n}</span>
<span class="mono" style="display:block;margin-top:.4rem;color:var(--ink-3)">{r}</span>
</span>
</div>""" for i, (n, r) in enumerate(people, 1))

    return (head(
        'About Panwar Knitwear | Knitwear Manufacturer in Ludhiana',
        'Panwar Knitwear is a family-run knitwear manufacturer in Ludhiana, Punjab, producing '
        'topwear under ZONIXA and bottomwear under MSP Sports for wholesalers and distributors '
        'across India.',
        canonical='about.html')
    + header(current='about')
    + f"""<main>
<div class="wrap"><p class="breadcrumb"><a href="index.html">Index</a> / About</p></div>

<section class="section section--tight">
<div class="wrap split">
<div>
{sec_label('01', 'About')}
<h1 class="t-section">A Ludhiana<br>knitwear<br>manufacturer</h1>
<p class="lede" style="margin-top:1.75rem">Panwar Knitwear is a manufacturer based in Ludhiana, Punjab, specialising in knitted garments. We produce T-shirts, track pants, lowers, shorts, sweatshirts and hoodies under our two brands, <strong>ZONIXA</strong> and <strong>MSP Sports</strong>.</p>
<p class="lede" style="margin-top:1rem">With over 15 years in garment manufacturing, we supply 1000+ distributors, working directly with retailers, wholesalers and clothing brands — no middlemen between our factory and your shop.</p>
<div class="btn-row" style="margin-top:2rem">
<a class="btn btn--wa" href="{wa('Hello Panwar Knitwear, I would like a wholesale enquiry.')}" target="_blank" rel="noopener">{ICON['whatsapp']} WhatsApp us</a>
<a class="btn btn--line" href="products.html">Browse products</a>
</div>
</div>
<figure class="pdp-media">
<img src="img/zonixas-feather-bonding-sweatshirts.jpg" alt="Zonixa feather bonding sweatshirts manufactured by Panwar Knitwear, Ludhiana" width="700" height="818" loading="lazy" decoding="async" data-parallax>
</figure>
</div>
</section>

<section class="section panel">
<div class="wrap">
<div class="sec-head" data-anim="up">
{sec_label('02', 'Brands')}
<h2 class="t-section">Two brands,<br>one factory</h2>
</div>
<div class="split" data-anim="up">
<div>
<h3 style="font-size:clamp(1.35rem,1.1rem + 1vw,1.9rem)">ZONIXA — topwear</h3>
<p class="lede" style="margin-top:.85rem">Round neck and collar T-shirts, printed tees, sweatshirts, hoodies and jackets. Summer cottons and dry fit through to 320 GSM heavy winter fleece.</p>
<p style="margin-top:1.25rem"><a class="tlink" href="products.html">See the Zonixa range {ICON['arrow']}</a></p>
</div>
<div>
<h3 style="font-size:clamp(1.35rem,1.1rem + 1vw,1.9rem);font-style:italic">MSP Sports — bottomwear</h3>
<p class="lede" style="margin-top:.85rem">Track pants, lowers, shorts, capri and nikkar, preferred by sports retailers and wholesalers. Message us for the current range.</p>
<p style="margin-top:1.25rem"><a class="tlink" href="{wa('Hello Panwar Knitwear, I would like details on the MSP Sports range.')}" target="_blank" rel="noopener">Enquire about MSP Sports {ICON['arrow']}</a></p>
</div>
</div>
</div>
</section>

<section class="section section--sand">
<div class="wrap">
<div class="sec-head" data-anim="up">
{sec_label('03', 'Craftsmanship')}
<h2 class="t-section">Fabrics we<br>work with</h2>
<p class="lede">Fabric is selected per article and season, across a wide GSM range.</p>
</div>
<div class="swatches-grid" data-anim="up">
{swatches}
</div>
</div>
</section>

<section class="section">
<div class="wrap">
<div class="sec-head" data-anim="up">
{sec_label('04', 'Leadership')}
<h2 class="t-section">A family-run<br>business</h2>
</div>
<div class="cat-list" data-anim="up">
{leaders}
</div>
</div>
</section>

{cta_band()}
</main>
""" + footer())

# --- contact.html -----------------------------------------------------------
def build_contact():
    profs = '\n'.join(f'<a class="chip" style="text-decoration:none;display:inline-flex;align-items:center" href="{E(u)}" target="_blank" rel="noopener">{E(n)}</a>' for n, u in PROFILES)
    return (head(
        'Contact Panwar Knitwear | Wholesale Enquiries, Ludhiana',
        'Contact Panwar Knitwear in Ludhiana for wholesale and bulk knitwear enquiries. '
        'Call, WhatsApp or email us, or send a quote request. Minimum order 200 – 300 pieces.',
        canonical='contact.html', extra=ld(LOCALBUSINESS_LD))
    + header(current='contact')
    + f"""<main>
<div class="wrap"><p class="breadcrumb"><a href="index.html">Index</a> / Contact</p></div>

<section class="section section--tight">
<div class="wrap">
<div class="sec-head">
{sec_label('01', 'Contact')}
<h1 class="t-section">Talk to us about<br>your bulk order</h1>
<p class="lede">WhatsApp is the fastest way to reach us. Share the article, quantity and your city, and we will reply with a quote.</p>
</div>
<div class="split">
<div>
{contact_rows()}
<h2 class="mono" style="margin-top:2.5rem;color:var(--ink-3)">Also find us on</h2>
<div class="btn-row" style="margin-top:1rem">
{profs}
</div>
</div>
<div id="quote">
{quote_form()}
</div>
</div>
</div>
</section>
</main>
""" + footer())

# ---------------------------------------------------------------------------
def write(path, content):
    os.makedirs(os.path.dirname(path) or '.', exist_ok=True)
    open(path, 'w', encoding='utf-8').write(content)

write('index.html', build_index())
write('products.html', build_products())
write('about.html', build_about())
write('contact.html', build_contact())
for p in products:
    write(f'product/{p["slug"]}.html', build_product(p))

print(f'Built: index, products, about, contact + {len(products)} product pages')
