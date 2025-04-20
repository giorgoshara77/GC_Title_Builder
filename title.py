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
    # Clean original title
    title = re.sub(r'^[A-Z0-9\-]+\s*[-–—]?\s*', '', raw_title)

    # Priority #1: Target Audience + Product Type
    is_set = "ring sets" in tags or "set" in raw_title.lower()
    base = "Women's Ring Set" if is_set else "Women's Ring"

    # Priority #2: Style
    style_terms = ["solitaire", "halo", "heart", "stackable", "eternity", "pavé", "midi"]
    styles = [tag.capitalize() for tag in tags if tag in style_terms]
    style_str = ' '.join(styles).strip()

    # Priority #3: Stone Info
    stone = "Clear Cubic Zirconia"
    if "simulated crystal" in raw_title.lower():
        stone = "Simulated Crystal"

    color_match = re.search(r"(champagne|blue|clear|pink|purple|green|black|white|red)", raw_title.lower())
    if color_match:
        stone = stone.replace("Clear", color_match.group().capitalize())

    # Avoid duplicate shape if already in styles
    shape_terms = ["round", "heart", "pear", "square"]
    shapes = [tag.capitalize() for tag in tags if tag in shape_terms and tag.capitalize() not in styles]
    if shapes:
        stone = f"{' '.join(shapes)} {stone}"

    # Priority #4: Metal Info
    material = ""
    if "brass" in raw_title.lower():
        material = "Brass"
    elif "stainless" in raw_title.lower():
        material = "Stainless Steel"

    plating = ""
    if "rhodium" in raw_title.lower():
        plating = "Rhodium-Plated"
    elif "IP Gold" in raw_title:
        plating = "Gold-Plated"
    elif "IP Rose Gold" in raw_title:
        plating = "Rose Gold-Plated"
    elif "IP Black" in raw_title:
        plating = "Black-Plated"

    metal_info = f"{material} {plating}".strip()

    # Priority #5: Optional Descriptors
    descriptors = []
    if is_set:
        descriptors.append("2 Pcs")
    if "high polished" in raw_title.lower():
        descriptors.append("High Polished")
    descriptors.append("Gift")

    # Final title assembly
    parts = [base]
    if style_str:
        parts.append(style_str)
    if stone:
        parts.append(stone)
    if metal_info:
        parts.append(metal_info)

    final_title = ', '.join(parts)

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
