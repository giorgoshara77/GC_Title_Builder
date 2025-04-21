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
    elif re.match(r"^[A-Za-z]{2,3}\d{3,5}$", input_value):
        return f"https://alamodeonline.com/products/{input_value.lower()}"
    else:
        return None

def extract_product_info(url):
    try:
        response = requests.get(url, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')

        # Extract product title
        meta_title = soup.find("meta", property="og:title")
        title = meta_title["content"].strip() if meta_title else "No title found"

        # Extract tags from visible tag links
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
    used_terms = set()

    def add_term(term):
        lower_term = term.lower()
        if lower_term not in used_terms:
            used_terms.add(lower_term)
            return term
        return None

    # Priority #1: Target Audience + Product Type
    is_set = "ring sets" in tags or "set" in raw_title.lower()
    base = add_term("Women's Ring Set") if is_set else add_term("Women's Ring")

    # Priority #2: Style
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

    # Priority #3: Stone Info
    if "simulated crystal" in raw_title.lower():
        stone = "Simulated Crystal"
    elif "clear" in raw_title.lower() or "clear" in tags:
        stone = "Clear Cubic Zirconia"
    else:
        stone = "Cubic Zirconia"

    color_match = re.search(r"(champagne|blue|pink|purple|green|black|white|red)", raw_title.lower())
    if color_match:
        stone = stone.replace("Clear", color_match.group().capitalize())

    shape_tag = next((tag.capitalize() for tag in tags if tag in ["round", "heart", "pear", "square"]
                      and tag.capitalize().lower() not in used_terms), None)
    if shape_tag:
        used_terms.add(shape_tag.lower())
        stone = f"{shape_tag} {stone}"

    # Priority #4: Metal Info (smart plating logic)
    plating_keywords = {
        "rose gold": "Rose Gold",
        "gold": "Gold",
        "black": "Black",
        "brown": "Brown",
        "light brown": "Brown",
        "coffee": "Brown",
        "light coffee": "Brown"
    }

    detected_platings = []
    raw_title_lower = raw_title.lower()
    for key, label in plating_keywords.items():
        if f"ip {key}" in raw_title_lower or key in raw_title_lower:
            if label not in detected_platings:
                detected_platings.append(label)
        if len(detected_platings) == 2:
            break

    plating_str = ""
    if detected_platings:
        plating_str = " & ".join(detected_platings) + "-Plated"

    material = ""
    if "stainless" in raw_title_lower:
        material = "Stainless Steel"
    elif "brass" in raw_title_lower or "brass" in tags:
        material = "Brass"

    metal_info_parts = [add_term(material), add_term(plating_str)]
    metal_info = ' '.join(filter(None, metal_info_parts))

    # Priority #5: Optional Descriptors
    descriptors = []
    if is_set:
        added = add_term("2 Pcs")
        if added:
            descriptors.append(added)
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

    for descriptor in descriptors:
        if len(final_title + ", " + descriptor) <= 75:
            final_title += ", " + descriptor

    # Replace Cubic Zirconia with CZ only if over 75 characters
    if len(final_title) > 75 and "Cubic Zirconia" in final_title:
        final_title = final_title.replace("Cubic Zirconia", "CZ")

    return final_title.strip()

# ========== UI Logic ==========

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
    st.write("DEBUG: Extracted Tags", st.session_state.tags)

    if st.button("✨ Generate Title"):
        final_title = transform_title(st.session_state.title, st.session_state.tags)
        st.markdown("### 🛒 Your eBay Title")
        st.text_area("Generated Title", final_title, height=100)
        st.markdown(f"**Character Count:** `{len(final_title)}/75`")
