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
        soup = BeautifulSoup(response.content, 'html.parser')  # Use .content instead of .text for encoding safety

        # Extract product title
        meta_title = soup.find("meta", property="og:title")
        title = meta_title["content"].strip() if meta_title else "No title found"

        # Extract tags
        tags = []
        tag_container = soup.find("div", class_="product-single__tags")
        if tag_container:
            tag_links = tag_container.find_all("a")
            for a in tag_links:
                tag_text = a.get_text(strip=True)
                tag_text = tag_text.replace("â™¡", "heart").replace("™", "").strip()  # Fix encoding issues
                tag_text = tag_text.lower()
                if tag_text and tag_text not in tags:
                    tags.append(tag_text)

        return title, tags

    except Exception as e:
        st.write("DEBUG: Error extracting tags", str(e))
        return None, []

def transform_title(raw_title, tags):
    title = re.sub(r'^[A-Z0-9\-]+\s*[-–—]?\s*', '', raw_title)

    # Priority #1: Target Audience + Product Type
    is_set = "ring sets" in tags or "set" in raw_title.lower()
    base = "Women's Ring Set" if is_set else "Women's Ring"

    # Priority #2: Style
    style_tags = ["solitaire", "halo", "heart", "stackable", "eternity", "pavé", "midi"]
    styles = []
    for tag in style_tags:
        if tag in tags and tag.capitalize() not in styles:
            styles.append(tag.capitalize())
    style_str = ' '.join(styles)

    # Priority #3: Stone Info
    stone = "Clear Cubic Zirconia"
    if "simulated crystal" in raw_title.lower():
        stone = "Simulated Crystal"
    color_match = re.search(r"(champagne|blue|clear|pink|purple|green|black|white|red)", raw_title.lower())
    if color_match:
        stone = stone.replace("Clear", color_match.group().capitalize())

    shape_tags = ["round", "heart", "pear", "square"]
    shape = [tag.capitalize() for tag in tags if tag in shape_tags]
    if shape:
        stone = f"{' '.join(shape)} {stone}"

    # Priority #4: Metal Info
    plating = ""
    if "IP Gold" in raw_title:
        plating = "Gold-Plated"
    elif "IP Rose Gold" in raw_title:
        plating = "Rose Gold-Plated"
    elif "IP Black" in raw_title:
        plating = "Black-Plated"
    elif "rhodium" in tags:
        plating = "Rhodium-Plated"

    material = ""
    if "stainless" in raw_title.lower():
        material = "Stainless Steel"
    elif "brass" in tags:
        material = "Brass"

    metal_info = " ".join(filter(None, [material, plating])).strip()

    # Priority #5: Optional Descriptors
    descriptors = []
    if is_set:
        descriptors.append("2 Pcs")
    if "high polished" in raw_title.lower():
        descriptors.append("High Polished")
    descriptors.append("Gift")  # Add gift if space allows

    # Build base title in order
    parts = [base]
    if style_str:
        parts.append(style_str)
    if stone:
        parts.append(stone)
    if metal_info:
        parts.append(metal_info)

    final_title = ', '.join(parts)

    # Add optional descriptors if space allows
    for descriptor in descriptors:
        if len(final_title + ", " + descriptor) <= 75:
            final_title += ", " + descriptor

    return final_title.strip()

# ========== UI Logic ==========

if is_valid_alamode_url(product_url):
    st.success("✅ Valid AlamodeOnline URL. Extracting product data...")

    if st.button("🔍 Load Product Info"):
        title, tags = extract_product_info(product_url)
        st.session_state.title = title
        st.session_state.tags = tags

    if "title" in st.session_state and "tags" in st.session_state:
        st.markdown("### 📝 Extracted Product Info")
        st.write(f"**Title:** {st.session_state.title if st.session_state.title else 'No title found'}")
        st.write(f"**Tags:** {', '.join(st.session_state.tags) if st.session_state.tags else 'No tags found'}")
        st.write("DEBUG: Extracted Tags", st.session_state.tags)

        if st.button("✨ Generate Title"):
            final_title = transform_title(st.session_state.title, st.session_state.tags)
            st.markdown("### 🛒 Your eBay Title")
            st.text_area("Generated Title", final_title, height=100)
            st.markdown(f"**Character Count:** `{len(final_title)}/75`")
else:
    st.error("❌ This doesn't look like a valid AlamodeOnline product URL. Please check the link.")
