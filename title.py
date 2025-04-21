import streamlit as st
import re
import requests
from bs4 import BeautifulSoup

st.set_page_config(page_title="GC Title Generator")
st.title("🛍️ GC Title Generator")
st.subheader("Create optimized and eye-catching eBay titles for your jewelry listings.")

user_input = st.text_input("Paste your AlamodeOnline product URL or SKU")

def is_valid_alamode_url(url):
    return "alamodeonline.com/products/" in url

def build_product_url(input_text):
    if input_text.startswith("http"):
        return input_text
    return f"https://alamodeonline.com/products/{input_text.strip()}"

def extract_product_info(url):
    try:
        response = requests.get(url, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')

        # Extract product title
        meta_title = soup.find("meta", property="og:title")
        title = meta_title["content"].strip() if meta_title else "No title found"

        # Extract tags
        tags = []
        tag_container = soup.find("div", class_="product-single__tags")
        if tag_container:
            tag_links = tag_container.find_all("a")
            tags = [a.get_text(strip=True).replace("â™¡", "heart").replace("™", "").strip().lower().rstrip(',') for a in tag_links if a.get_text(strip=True)]

        return title, tags

    except Exception as e:
        st.write("DEBUG: Error extracting tags", str(e))
        return None, []

def transform_title(raw_title, tags):
    title_clean = re.sub(r'^[A-Z0-9\-]+\s*[-–—]?\s*', '', raw_title)
    raw_title_lower = raw_title.lower()
    used_terms = set()

    def add_term(term):
        lower = term.lower()
        if lower not in used_terms:
            used_terms.add(lower)
            return term
        return None

    # Priority #1: Target Audience + Product Type
    is_set = "ring sets" in tags or "set" in raw_title_lower
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
    stone = "Cubic Zirconia"
    if "simulated crystal" in raw_title_lower:
        stone = "Simulated Crystal"

    if "clear" in raw_title_lower or "clear" in tags:
        stone = "Clear " + stone

    shape_tag = next((tag.capitalize() for tag in tags if tag in ["round", "heart", "pear", "square"]
                      and tag.capitalize().lower() not in used_terms), None)
    if shape_tag:
        used_terms.add(shape_tag.lower())
        stone = f"{shape_tag} {stone}"

    # Priority #4: Metal Info
    plating_types = {
        "ip gold": "Gold-Plated",
        "ip rose gold": "Rose Gold-Plated",
        "ip black": "Black-Plated",
        "ip brown": "Brown-Plated",
        "ip coffee": "Brown-Plated",
        "ip light brown": "Brown-Plated",
        "ip light coffee": "Brown-Plated"
    }

    detected_platings = []
    for key, value in plating_types.items():
        if key in raw_title_lower and value not in detected_platings:
            detected_platings.append(value)

    plating = ""
    if len(detected_platings) >= 2:
        plating = ' & '.join([detected_platings[0].replace("-Plated", ""), detected_platings[1]])
    elif detected_platings:
        plating = detected_platings[0]

    material = ""
    if "stainless" in raw_title_lower:
        material = "Stainless Steel"
    elif "brass" in raw_title_lower or "brass" in tags:
        material = "Brass"

    metal_info_parts = [add_term(material), add_term(plating)]
    metal_info = ' '.join(filter(None, metal_info_parts))

    # Priority #5: Optional Descriptors (excluding "2 Pcs" for now)
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

    # Add other descriptors if space allows
    for descriptor in descriptors:
        if len(final_title + ", " + descriptor) <= 75:
            final_title += ", " + descriptor

    # ✅ Add "2 Pcs" if it's a set, not already used, and space allows
    if is_set and "2 pcs" not in used_terms:
        if len(final_title + ", 2 Pcs") <= 75:
            final_title += ", 2 Pcs"
            used_terms.add("2 pcs")

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
