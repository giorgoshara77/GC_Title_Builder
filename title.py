import streamlit as st
import re
import requests
from bs4 import BeautifulSoup

st.set_page_config(page_title="GC Title Generator")
st.title("🛍️ GC Title Generator")
st.subheader("Create optimized and eye-catching eBay titles for your jewelry listings.")

product_url = st.text_input("Paste your AlamodeOnline product URL")

def is_valid_alamode_url(url):
    return "alamodeonline.com/products/" in url

def extract_product_info(url):
    try:
        response = requests.get(url, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')

        # Extract product title
        meta_title = soup.find("meta", property="og:title")
        title = meta_title["content"].strip() if meta_title else "No title found"

        # Extract tags from the div block with class 'product-single__tags'
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
    # Clean the original title
    title = re.sub(r'^[A-Z0-9\-]+\s*[-–—]?\s*', '', raw_title)

    # Used terms tracker to avoid duplicates
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
    styles = []
    for tag in tags:
        if tag in ["solitaire", "halo", "heart", "stackable", "eternity", "pavé", "midi"]:
            styled = add_term(tag.capitalize())
            if styled:
                styles.append(styled)
    style_str = ' '.join(styles)

    # Priority #3: Stone Info
    stone = "Clear Cubic Zirconia"
    if "simulated crystal" in raw_title.lower():
        stone = "Simulated Crystal"

    color_match = re.search(r"(champagne|blue|clear|pink|purple|green|black|white|red)", raw_title.lower())
    if color_match:
        stone = stone.replace("Clear", color_match.group().capitalize())

    # Stone Shape
    shape_tag = next((tag.capitalize() for tag in tags if tag in ["round", "heart", "pear", "square"]), None)
    if shape_tag and shape_tag.lower() not in used_terms:
        used_terms.add(shape_tag.lower())
        stone = f"{shape_tag} {stone}"

    # Priority #4: Metal Info
    plating = ""
    if "IP Gold" in raw_title:
        plating = "Gold-Plated"
    elif "IP Rose Gold" in raw_title:
        plating = "Rose Gold-Plated"
    elif "IP Black" in raw_title:
        plating = "Black-Plated"
    elif "rhodium" in raw_title.lower() or "rhodium" in tags:
        plating = "Rhodium-Plated"

    material = ""
    if "stainless" in raw_title.lower():
        material = "Stainless Steel"
    elif "brass" in raw_title.lower() or "brass" in tags:
        material = "Brass"

    metal_info_parts = [add_term(material), add_term(plating)]
    metal_info = ' '.join(filter(None, metal_info_parts))

    # Priority #5: Optional Descriptors
    descriptors = []
    if is_set:
        added = add_term("2 Pcs")
        if added:
            descriptors.append(added)
    if "high polished" in raw_title.lower():
        added = add_term("High Polished")
        if added:
            descriptors.append(added)

    gift = add_term("Gift")
    if gift:
        descriptors.append(gift)

    # Build base title in priority order
    parts = list(filter(None, [base, style_str, stone, metal_info]))
    final_title = ', '.join(parts)

    # Fill remaining space with optional descriptors
    for descriptor in descriptors:
        if len(final_title + ", " + descriptor) <= 75:
            final_title += ", " + descriptor

    return final_title.strip()

# UI Logic
if product_url:
    if is_valid_alamode_url(product_url):
        st.success("✅ Valid AlamodeOnline URL. Extracting product data...")
        title, tags = extract_product_info(product_url)

        st.markdown("### 📝 Extracted Product Info")
        st.write(f"**Title:** {title if title else 'No title found'}")
        st.write(f"**Tags:** {', '.join(tags) if tags else 'No tags found'}")
        st.write("DEBUG: Extracted Tags", tags)

        if title and st.button("✨ Generate Title"):
            final_title = transform_title(title, tags)
            st.markdown("### 🛒 Your eBay Title")
            st.text_area("Generated Title", final_title, height=100)
            st.markdown(f"**Character Count:** `{len(final_title)}/75`")
    else:
        st.error("❌ This doesn't look like a valid AlamodeOnline product URL. Please check the link.")
