# Panwar Knitwear — website

Static site. Plain HTML, one CSS file, ~80 lines of vanilla JS. No framework, no
build tooling, no dependencies. Upload the folder to any web host and it works.

## Pages

| File | Purpose |
|---|---|
| `index.html` | Homepage — hero, trust strip, categories, ZONIXA products, MSP Sports, manufacturing, bulk info, quote form |
| `products.html` | All 29 ZONIXA articles with category filtering |
| `product/<slug>.html` | 29 product detail pages |
| `about.html` | Company, brands, fabrics, leadership |
| `contact.html` | Phone/WhatsApp/email/address/hours + quote form |

## Editing content

The HTML pages are **generated** — do not hand-edit them, your changes will be
overwritten. Edit the source and regenerate:

```bash
python data/build.py
```

- **Business facts** (address, phones, email, hours, MOQ, sizes, WhatsApp number,
  categories, fabrics, social links) live at the top of `data/build.py` in the
  `BIZ`, `PHONES`, `FABRICS`, `PROFILES`, `CATEGORIES` and `MSP_CATS` blocks.
- **Product data** lives in `data/products.json` (name, specs, colours,
  description, categories). Edit it directly, then rebuild.
- **Layout and styling** is `css/style.css` — one file, no framework. The design
  tokens (colour, type, spacing) are the CSS custom properties at the top.
- **Motion** is `js/main.js` plus GSAP + ScrollTrigger from a CDN.

## Visual system — "Mill & Thread"

The language of a working textile mill: unbleached swatch-card cream, warm ink,
one dyehouse pigment. Reads as a manufacturer's catalogue, not a brochure.

| Token | Value | Role |
|---|---|---|
| `--ground` / `--ground-2` | `#f2ede3` / `#e8e1d4` | Cream page ground, sand band |
| `--ink` / `--ink-2` / `--ink-3` | `#1a1917` / `#4a463f` / `#645e4f` | Type and full-bleed panels |
| `--rust` | `#c1542a` | Decorative only — rules, numerals, hover sweeps (3.94:1) |
| `--rust-text` | `#a3421f` | Small text on cream, button fills (5.36:1) |
| `--rust-light` | `#d4652f` | Small text on charcoal (4.77:1) |
| `--olive` | `#5a5f3d` | MSP Sports |
| `--on-dark-2` / `--on-dark-3` | `#cfc8ba` / `#918a7d` | Text on charcoal |
| `--on-olive-2` | `#e4dfd4` | Secondary text on olive (`--on-dark-2` is only 4.02 there) |

Rust exists in three values on purpose: the mid rust is beautiful but only
3.94:1, so it is never used for small text. Pick the token by ground, not by eye.

**Type** — Bricolage Grotesque 600/800 (display), Inter Tight 400/500/600 (body),
DM Mono 400/500 (the spec layer: article numbers, GSM, section numerals, ticker).

**Motion** — GSAP + ScrollTrigger, all inside a `prefers-reduced-motion` gate.
Nothing is hidden by CSS except under `html.anim`, which an inline head script
adds only when motion is welcome and `main.js` removes if GSAP fails to load.
Scroll reveals use `ScrollTrigger.batch` with `once: true`, so observers detach
after firing (verified: 0 active triggers after a full scroll). A 2.5s timeout
in `main.js` is a final safety net. **If you add an animated element, give it
`data-anim` and animate it to `opacity: 1` — never hide anything in CSS alone.**

### Manufacturing process sequence

The `04 — MANUFACTURING` section runs a scroll-driven sequence:
`01 FABRIC → 02 PRODUCTION → 03 CUSTOMIZATION → 04 QUALITY`.

- Stage copy lives in `PROCESS` in `data/build.py`, beside the other verified-fact
  blocks. Stage 01's chips come from `FABRICS`; stage 02's come from `BIZ['moq']`
  and `BIZ['sizes']`, so the MOQ can never drift from the rest of the site.
- **Desktop (≥861px):** the `.proc` block is pinned for 1040px of scroll and
  scrubbed. Progress drives the active stage, the rust rail fill, and the large
  odometer numeral. The pin releases after stage 04.
- **Mobile (≤860px):** no pinning. Each stage activates as it reaches mid-viewport
  and the rail fills vertically.
- **Fallback:** JS adds `.proc.is-enhanced`, and *every* dimming rule is scoped to
  it. Under reduced motion or a failed GSAP load the class is never added, so all
  four stages render at full opacity as a plain readable stack. Verified: with the
  CDN blocked, 0/4 stages are dimmed.

The product grid is uniform on `products.html` (filtering must not reflow oddly)
and asymmetric on the homepage brand band via `.plates--editorial`.

### Adding a product

1. Put the photo in `img/` as `<slug>.jpg`.
2. Add an entry to `data/products.json` following an existing one.
3. `python data/build.py`

### Images

`data/optimise.py` resizes originals from `img/orig/` to 700px wide and
compresses them into `img/`. Drop new full-size photos into `img/orig/` and run
it. Current set: 6.8 MB → 3.1 MB.

`data/ogimage.py` builds the default social share card, `img/og-cover.jpg`, by
cropping the homepage hero original to 1200×630 — the size WhatsApp, Facebook
and LinkedIn crop link previews to. Run it only if the hero photo changes;
`build.py` does not. Product pages share their own garment photo instead.

## How the data was produced

`data/products.txt` and `data/raw/` are the scraped originals from the previous
panwarknitwear.com site — kept so the extraction is reproducible and auditable.
`data/extract.py` parses them into `products.json`; `data/categorise.py` assigns
categories. Neither needs to be re-run unless re-importing from the old site.

> Note: `data/raw/` contains the *old* pages, including the `email@example.com`
> placeholder that was on the live site. Nothing in it is served.

## Conversion actions

WhatsApp is the primary CTA and points to **+91 98157 03769** throughout
(`BIZ['wa']` in `data/build.py`). Product pages and product cards prefill the
WhatsApp message with the article name. `tel:` links use all three published
numbers. A sticky Call / WhatsApp / Get Quote bar shows on screens ≤900px.

The quote form uses a `mailto:` action — it opens the visitor's mail client.
**If the host supports PHP or a form service, point the form's `action` at it**
so enquiries arrive reliably; `mailto:` is a fallback, not a submission handler.

## Still needed from the business owner

- **Full street address.** Only `Ludhiana, Punjab 141008` is published anywhere;
  the site and its `LocalBusiness` structured data use that until the street
  address is confirmed.
- **MSP Sports product photos.** MSP Sports is presented as a brand with
  category tiles and enquiry links, but has no product cards — the old site's
  "Product 1…5" entries were placeholders and were not carried over.
- **Factory / manufacturing photos.** Would strengthen the About and
  Manufacturing sections.
- The `1000+ distributors` figure is taken from zonixa.com, which also states
  `500+` elsewhere on the same page. Worth reconciling.
