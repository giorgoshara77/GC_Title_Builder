import streamlit as st
import re
import requests
from bs4 import BeautifulSoup

st.set_page_config(page_title="GC Title Generator")
st.title("🛍️ GC Title Generator")
st.subheader("Create optimized and eye-catching eBay titles for your jewelry listings.")

user_input = st.text_input("Paste AlamodeOnline product URL or enter SKU (e.g. TK3180)")

def is_valid_alamode_url(url):
    return url.startswith("https://alamodeonline.com/products/")

def build_product_url(input_value):
    input_value = input_value.strip()
    if input_value.lower().startswith("https://alamodeonline.com/products/"):
        return input_value
    elif re.match(r"^[A-Za-z]{2,3}\d{3,6}[a-z]{0,2}$", input_value.lower()):
        return f"https://alamodeonline.com/products/{input_value.lower()}"
    else:
        return None

def extract_product_info(url):
    try:
        response = requests.get(url, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')

        meta_title = soup.find("meta", property="og:title")
        title = meta_title["content"].strip() if meta_title else "No title found"

        tags = []
        tag_container = soup.find("div", class_="product-single__tags")
        if tag_container:
            tag_links = tag_container.find_all("a")
            tags = [a.get_text(strip=True).lower().rstrip(',') for a in tag_links if a.get_text(strip=True)]

        st.write("DEBUG: Extracted Tags", tags)
        return title, tags

    except Exception as e:
        st.write("DEBUG: Error extracting tags", str(e))
        return None, []

def transform_title(raw_title, tags):
    title = re.sub(r'^[A-Z0-9\-]+\s*[-–—]?\s*', '', raw_title)
    raw_title_lower = raw_title.lower()
    used_terms = set()

    def add_term(term):
        lower_term = term.lower()
        if lower_term not in used_terms:
            used_terms.add(lower_term)
            return term
        return None

    # Target Audience + Type
    is_set = "ring sets" in tags or "set" in raw_title_lower
    if "men" in tags:
        base = add_term("Men's Ring")
    elif "women" in tags:
        base = add_term("Women's Ring Set" if is_set else "Women's Ring")
    else:
        base = add_term("Ring")

    # Style
    style_terms = ["solitaire", "halo", "heart", "stackable", "eternity", "pavé", "midi"]
    styles = []
    for tag in tags:
        for style in style_terms:
            if style in tag:
                styled = add_term(style.capitalize())
                if styled:
                    styles.append(styled)
                break
    style_str = ' '.join(styles)

    # === STONE DETECTION LOGIC ===
    stone_type_substitutions = {
        "top grade crystal": "Simulated Crystal",
        "synthetic glass": "Synthetic Glass",
        "cubic zirconia": "Cubic Zirconia",
        "aaa cubic zirconia": "Cubic Zirconia",
        "aaa cz": "CZ",
        "cz": "CZ",
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

    # Check for "No Stone" or "Epoxy"
    stone = ""
    if "no stone" in raw_title_lower or "no stone" in tags:
        stone = ""
    elif "epoxy" in raw_title_lower or "epoxy" in tags:
        stone = "Epoxy"
    else:
        found_type = None
        for raw_type, formatted in stone_type_substitutions.items():
            if raw_type in raw_title_lower:
                found_type = formatted
                break
        if found_type:
            stone = found_type
        elif "cz" in raw_title_lower:
            stone = "Cubic Zirconia"

    # Metal Info (detect multiple platings)
    plating_keywords = {
        "ip gold": "Gold-Plated",
        "ip rose gold": "Rose Gold-Plated",
        "ip black": "Black-Plated",
        "ip brown": "Brown-Plated",
        "ip light brown": "Brown-Plated",
        "ip coffee": "Brown-Plated",
        "ip light coffee": "Brown-Plated",
        "rhodium": "Rhodium-Plated"
    }

    platings_found = []
    for keyword, label in plating_keywords.items():
        if keyword in raw_title_lower:
            platings_found.append(label)

    if len(platings_found) == 2:
        plating = f"{platings_found[1].split('-')[0]} & {platings_found[0]}"
    elif platings_found:
        plating = platings_found[0]
    else:
        plating = ""

    material = ""
    if "stainless" in raw_title_lower:
        material = "Stainless Steel"
    elif "brass" in raw_title_lower or "brass" in tags:
        material = "Brass"

    metal_info_parts = [add_term(material), add_term(plating)]
    metal_info = ' '.join(filter(None, metal_info_parts))

    # Optional descriptors (no Gift)
    descriptors = []
    if "high polished" in raw_title_lower:
        added = add_term("High Polished")
        if added:
            descriptors.append(added)

    # Build core title
    parts = list(filter(None, [base, style_str, stone, metal_info]))
    final_title = ', '.join(parts)

    # Add optional descriptors
    for descriptor in descriptors:
        if len(final_title + ", " + descriptor) <= 80:
            final_title += ", " + descriptor

    # Add 2 Pcs if set and space
    if is_set and "2 pcs" not in used_terms and len(final_title + ", 2 Pcs") <= 80:
        final_title += ", 2 Pcs"
        used_terms.add("2 pcs")

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

if st.session_state.title and st.session_state.tags:
    st.markdown("### 📝 Extracted Product Info")
    st.write(f"**Title:** {st.session_state.title}")
    st.write(f"**Tags:** {', '.join(st.session_state.tags)}")
    st.write("DEBUG: Extracted Tags", st.session_state.tags)

    if st.button("✨ Generate Title"):
        final_title = transform_title(st.session_state.title, st.session_state.tags)
        st.markdown("### 🛒 Your eBay Title")
        st.text_area("Generated Title", final_title, height=100)
        st.markdown(f"**Character Count:** `{len(final_title)}/80`")
