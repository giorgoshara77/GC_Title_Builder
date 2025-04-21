import streamlit as st
import re
import requests
from bs4 import BeautifulSoup

st.set_page_config(page_title="GC Title Generator")
st.title("🛍️ GC Title Generator")
st.subheader("Create optimized and eye-catching eBay titles for your jewelry listings.")

user_input = st.text_input("Paste AlamodeOnline product URL or enter SKU (e.g. TK3180)")

# ========== Helpers ==========

def is_valid_alamode_url(url):
    return url.startswith("https://alamodeonline.com/products/")

def build_product_url(input_value):
    input_value = input_value.strip()
    # Match SKU: 2–3 letters, 3–6 digits, optional single letter suffix
    if re.match(r"^[A-Za-z]{2,3}\d{3,6}[A-Za-z]?$", input_value):
        return f"https://alamodeonline.com/products/{input_value.lower()}"
    elif is_valid_alamode_url(input_value):
        return input_value
    else:
        return None

def extract_product_info(url):
    try:
        response = requests.get(url, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')

        meta_title = soup.find("meta", property="og:title")
        title = meta_title["content"].strip() if meta_title else "No title found"

        # Extract tags from tag container
        tags = []
        tag_container = soup.find("div", class_="product-single__tags")
        if tag_container:
            tag_links = tag_container.find_all("a")
            tags = [a.get_text(strip=True).lower().rstrip(',') for a in tag_links if a.get_text(strip=True)]

        return title, tags

    except Exception as e:
        st.write("DEBUG: Error extracting tags", str(e))
        return None, []

# ========== Title Builder ==========

def transform_title(raw_title, tags):
    title = re.sub(r'^[A-Z0-9\-]+\s*[-–—]?\s*', '', raw_title)
    raw_title_lower = raw_title.lower()
    used_terms = set()

    def add_term(term):
        lower = term.lower()
        if lower not in used_terms:
            used_terms.add(lower)
            return term
        return None

    # Priority 1: Target Audience + Product Type
    is_set = "ring sets" in tags or "set" in raw_title_lower
    base = add_term("Women's Ring Set") if is_set else add_term("Women's Ring")

    # Priority 2: Style
    style_terms = ["solitaire", "halo", "heart", "stackable", "eternity", "pavé", "midi"]
    styles = []
    for tag in tags:
        for style in style_terms:
            if style in tag and add_term(style.capitalize()):
                styles.append(style.capitalize())
                break
    style_str = ' '.join(styles)

    # Priority 3: Stone Info (Type ➝ Color ➝ Shape)
    stone_type_map = {
        "top grade crystal": "Simulated Crystal",
        "synthetic glass": "Synthetic Glass",
        "cubic zirconia": "Cubic Zirconia",
        "cz": "CZ",
        "aaa cubic zirconia": "Cubic Zirconia",
        "aaa cz": "CZ",
        "precious stone conch": "Simulated Stone Conch",
        "precious stone lapis": "Simulated Stone Lapis",
        "precious stone pink crystal": "Simulated Stone PINK CRYSTAL",
        "precious stone amethyst crystal": "Simulated Stone Amethyst Crystal",
        "synthetic acrylic": "Synthetic Acrylic",
        "synthetic imitation amber": "Synthetic Imitation Amber",
        "ceramic": "Ceramic",
        "synthetic synthetic glass": "Synthetic Glass",
        "synthetic glass bead": "Simulated Glass Bead",
        "semi-precious jade": "Simulated Jade",
        "synthetic jade": "Simulated Jade",
        "synthetic cat eye": "Simulated Cat Eye",
        "semi-precious marcasite": "Simulated Marcasite",
        "synthetic spinel": "Simulated Spinel",
        "synthetic turquoise": "Simulated Turquoise",
        "synthetic pearl": "Simulated Pearl",
        "synthetic synthetic stone": "Synthetic Stone"
    }

    stone_type = next((stone_type_map[k] for k in stone_type_map if k in raw_title_lower), "")
    if not stone_type:
        stone_type = "Cubic Zirconia"  # Default

    # Color
    color_map = {
        "jet": "Black", "black": "Black", "light gray": "Gray", "gray": "Gray", "white": "White", "clear": "Clear",
        "siam": "Red", "ruby": "Ruby-Colored", "rose": "Rose", "garnet": "Garnet-Colored", "light rose": "Rose",
        "orange": "Orange", "champagne": "Champagne", "multi color": "Multicolor", "citrine yellow": "Yellow",
        "topaz": "Topaz-Colored", "citrine": "Citrine-Colored", "light gold": "Light Gold", "emerald": "Emerald-Colored",
        "blue zircon": "Blue", "peridot": "Peridot Colored", "olivine color": "Olive Green",
        "apple green color": "Apple Green", "sapphire": "Sapphire-Colored", "montana": "Montana",
        "sea blue": "Sea Blue", "aquamarine": "Aquamarine", "london blue": "Blue", "tanzanite": "Tanzanite-Colored",
        "amethyst": "Amethyst-Colored", "light amethyst": "Amethyst-Colored", "brown": "Brown",
        "smoked quartz": "Smoky Brown", "coffee": "Coffee", "light coffee": "Coffee"
    }

    color = ""
    for k, v in color_map.items():
        if f"in {k}" in raw_title_lower:
            color = v
            break

    # Shape
    shapes = ["round", "heart", "pear", "square", "triangle", "oblong", "stellar"]
    shape_tag = next((tag.capitalize() for tag in tags if tag in shapes), "")

    stone_parts = list(filter(None, [shape_tag, color, stone_type]))
    stone = ' '.join(stone_parts)

    # Priority 4: Metal Info – support dual plating
    plating_keywords = {
        "ip gold": "Gold-Plated", "ip rose gold": "Rose Gold-Plated", "ip black": "Black-Plated",
        "ip brown": "Brown-Plated", "ip coffee": "Brown-Plated", "ip light brown": "Brown-Plated", "ip light coffee": "Brown-Plated"
    }

    found_platings = []
    for key, label in plating_keywords.items():
        if key in raw_title:
            found_platings.append(label)

    plating = " & ".join(found_platings[:2]) if found_platings else ""

    material = ""
    if "stainless" in raw_title_lower:
        material = "Stainless Steel"
    elif "brass" in raw_title_lower or "brass" in tags:
        material = "Brass"

    metal_info_parts = [add_term(material), add_term(plating)]
    metal_info = ' '.join(filter(None, metal_info_parts)).strip()

    # Optional Descriptors
    descriptors = []
    if "high polished" in raw_title_lower:
        added = add_term("High Polished")
        if added:
            descriptors.append(added)

    gift = add_term("Gift")
    if gift:
        descriptors.append(gift)

    # Build base title
    parts = list(filter(None, [base, style_str, stone, metal_info]))
    final_title = ', '.join(parts)

    # Add descriptors if space allows
    for descriptor in descriptors:
        if len(final_title + ", " + descriptor) <= 80:
            final_title += ", " + descriptor

    # Add "2 Pcs" if space allows at the end
    if is_set and "2 pcs" not in used_terms:
        if len(final_title + ", 2 Pcs") <= 80:
            final_title += ", 2 Pcs"
            used_terms.add("2 pcs")

    # If final title exceeds 80, replace "Cubic Zirconia" with "CZ"
    if len(final_title) > 80 and "Cubic Zirconia" in final_title:
        final_title = final_title.replace("Cubic Zirconia", "CZ")

    return final_title.strip()

# ========================
# UI Logic
# ========================

if "title" not in st.session_state:
    st.session_state.title = ""
if "tags" not in st.session_state:
    st.session_state.tags = []

product_url = build_product_url(user_input)

if st.button("🔍 Load Product Info") and product_url:
    if is_valid_alamode_url(product_url):
        st.success("✅ Valid product input. Extracting product data...")
        title, tags = extract_product_info(product_url)
        st.session_state.title = title
        st.session_state.tags = tags
    else:
        st.error("❌ Invalid product URL or SKU format.")

# Show product info if loaded
if st.session_state.title and st.session_state.tags:
    st.markdown("### 📝 Extracted Product Info")
    st.write(f"**Title:** {st.session_state.title}")
    st.write(f"**Tags:** {', '.join(st.session_state.tags)}")

    if st.button("✨ Generate Title"):
        final_title = transform_title(st.session_state.title, st.session_state.tags)
        st.markdown("### 🛒 Your eBay Title")
        st.text_area("Generated Title", final_title, height=100)
        st.markdown(f"**Character Count:** `{len(final_title)}/80`")
