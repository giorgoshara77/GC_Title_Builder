import streamlit as st
import re
import requests
from bs4 import BeautifulSoup

st.set_page_config(page_title="GC Title Generator")
st.title("🛍️ GC Title Generator")
st.subheader("Create optimized and eye-catching eBay titles for your jewelry listings.")

user_input = st.text_input("Paste AlamodeOnline product URL or enter SKU (e.g. TK3180)")

# --------------------
# Configuration
# --------------------

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

stone_color_map = {
    "jet": "Black", "black": "Black", "light gray": "Gray", "gray": "Gray",
    "white": "White", "clear": "Clear", "siam": "Red", "ruby": "Ruby-Colored",
    "rose": "Rose", "garnet": "Garnet-Colored", "light rose": "Rose", "orange": "Orange",
    "champagne": "Champagne", "multi color": "Multicolor", "citrine yellow": "Yellow",
    "topaz": "Topaz-Colored", "citrine": "Citrine-Colored", "light gold": "Light Gold",
    "emerald": "Emerald-Colored", "blue zircon": "Blue", "peridot": "Peridot Colored",
    "olivine color": "Olive Green", "apple green color": "Apple Green",
    "sapphire": "Sapphire-Colored", "montana": "Montana", "sea blue": "Sea Blue",
    "aquamarine": "Aquamarine", "london blue": "Blue", "tanzanite": "Tanzanite-Colored",
    "amethyst": "Amethyst-Colored", "light amethyst": "Amethyst-Colored",
    "brown": "Brown", "smoked quartz": "Smoky Brown", "coffee": "Coffee", "light coffee": "Coffee"
}

stone_shape_tags = ["round", "pear", "heart", "triangle", "square", "oblong", "stellar"]

# --------------------
# Functions
# --------------------

def is_valid_alamode_url(url):
    return url.startswith("https://alamodeonline.com/products/")

def build_product_url(input_value):
    input_value = input_value.strip()
    if input_value.lower().startswith("https://alamodeonline.com/products/"):
        return input_value
    elif re.match(r"^[A-Za-z]{2,3}\d{3,5}[a-z]*$", input_value):  # Match SKUs like TK3180, TK1869lj
        return f"https://alamodeonline.com/products/{input_value.lower()}"
    else:
        return None

def extract_product_info(url):
    try:
        response = requests.get(url, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')
        title = soup.find("meta", property="og:title")["content"].strip()
        tag_container = soup.find("div", class_="product-single__tags")
        tags = []
        if tag_container:
            tag_links = tag_container.find_all("a")
            tags = [a.get_text(strip=True).lower().rstrip(',') for a in tag_links if a.get_text(strip=True)]
        return title, tags
    except Exception as e:
        st.write("DEBUG: Error extracting product info:", str(e))
        return None, []

def transform_title(raw_title, tags):
    raw_title_lower = raw_title.lower()
    title = re.sub(r'^[A-Z0-9\-]+\s*[-–—]?\s*', '', raw_title)

    used_terms = set()
    def add_term(term):
        term_lower = term.lower()
        if term_lower not in used_terms:
            used_terms.add(term_lower)
            return term
        return None

    # Gender
    gender = "Women's"
    if any("men" in t for t in tags):
        gender = "Men's"
    elif any("women" in t for t in tags):
        gender = "Women's"
    base = add_term(f"{gender} Ring Set" if "ring sets" in tags or "set" in raw_title_lower else f"{gender} Ring")

    # Styles
    style_terms = ["solitaire", "halo", "heart", "stackable", "eternity", "pavé", "midi"]
    styles = [add_term(s.capitalize()) for t in tags for s in style_terms if s in t]
    style_str = ' '.join(filter(None, styles))

    # Stone Info
    stone_type = ""
    for phrase in stone_type_map:
        if phrase in raw_title_lower:
            stone_type = stone_type_map[phrase]
            break

    stone_color = ""
    color_match = re.search(r"in ([a-zA-Z\s]+)", raw_title)
    if color_match:
        color_raw = color_match.group(1).strip().lower()
        if color_raw in stone_color_map:
            stone_color = stone_color_map[color_raw]

    shape = next((s.capitalize() for s in tags if s in stone_shape_tags), "")
    stone = " ".join(filter(None, [shape, stone_color, stone_type])).strip()

    # Metal Info
    plating_matches = re.findall(r"IP\s*([a-zA-Z\s]+)\s*\(Ion Plating\)", raw_title)
    plating_list = []
    for plate in plating_matches:
        p = plate.strip().lower()
        if p == "gold":
            plating_list.append("Gold-Plated")
        elif p == "rose gold":
            plating_list.append("Rose Gold-Plated")
        elif p == "black":
            plating_list.append("Black-Plated")
        elif "brown" in p or "coffee" in p:
            plating_list.append("Brown-Plated")
    plating = " & ".join(sorted(set(plating_list)))

    material = ""
    if "stainless" in raw_title_lower:
        material = "Stainless Steel"
    elif "brass" in raw_title_lower or "brass" in tags:
        material = "Brass"

    metal_info = " ".join(filter(None, [material, plating]))
    metal_info = add_term(metal_info)

    # Optional Descriptors
    descriptors = []
    if "high polished" in raw_title_lower:
        desc = add_term("High Polished")
        if desc:
            descriptors.append(desc)

    parts = list(filter(None, [base, style_str, stone, metal_info]))
    final_title = ', '.join(parts)

    for descriptor in descriptors:
        if len(final_title + ", " + descriptor) <= 80:
            final_title += ", " + descriptor

    if "ring sets" in tags and "2 pcs" not in used_terms and len(final_title + ", 2 Pcs") <= 80:
        final_title += ", 2 Pcs"
        used_terms.add("2 pcs")

    if len(final_title) > 80 and "Cubic Zirconia" in final_title:
        final_title = final_title.replace("Cubic Zirconia", "CZ")

    return final_title.strip()

# --------------------------
# UI Logic
# --------------------------

if "title" not in st.session_state:
    st.session_state.title = ""
if "tags" not in st.session_state:
    st.session_state.tags = []

product_url = build_product_url(user_input)

if st.button("🔍 Load Product Info") and product_url:
    if is_valid_alamode_url(product_url):
        title, tags = extract_product_info(product_url)
        st.session_state.title = title
        st.session_state.tags = tags
        st.success("✅ Product data loaded.")
    else:
        st.error("❌ Invalid URL or SKU format.")

if st.session_state.title and st.session_state.tags:
    st.markdown("### 📝 Extracted Product Info")
    st.write(f"**Title:** {st.session_state.title}")
    st.write(f"**Tags:** {', '.join(st.session_state.tags)}")

    if st.button("✨ Generate Title"):
        final_title = transform_title(st.session_state.title, st.session_state.tags)
        st.markdown("### 🛒 Your eBay Title")
        st.text_area("Generated Title", final_title, height=100)
        st.markdown(f"**Character Count:** `{len(final_title)}/80`")

