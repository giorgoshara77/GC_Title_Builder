import streamlit as st
import re
import requests
from bs4 import BeautifulSoup

st.set_page_config(page_title="GC Title Generator")
st.title("🛍️ GC Title Generator")
st.subheader("Create optimized and eye-catching eBay titles for your jewelry listings.")

product_url = st.text_input("Paste your AlamodeOnline product URL")

def is_valid_alamode_url(url):
    return bool(re.match(r"https://alamodeonline\.com/.+/products/.+", url))

def extract_product_info(url):
    try:
        response = requests.get(url, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')

        # Extract product title
        meta_title = soup.find("meta", property="og:title")
        title = meta_title["content"].strip() if meta_title else "No title found"

        # Find the paragraph that contains "Tags:" anywhere in its text
        tag_block = soup.find("p", class_="tags")
        tags = []

        if tag_block:
            # Get full text of the tag block (ignoring <strong>)
            raw_tags = tag_block.get_text(separator=" ", strip=True)
            if "Tags:" in raw_tags:
                raw_tags = raw_tags.split("Tags:")[-1]
            tags = [t.strip().lower() for t in raw_tags.split(",") if t.strip()]
            st.write("DEBUG: Extracted Tags", tags)

        return title, tags
    except Exception as e:
        st.write("DEBUG: Error extracting tags", str(e))
        return None, []



def transform_title(raw_title, tags):
    # Clean the original title
    title = re.sub(r'^[A-Z0-9\-]+\s*[-–—]?\s*', '', raw_title)

    # Priority #1: Target Audience + Product Type
    is_set = "ring sets" in tags or "set" in raw_title.lower()
    base = "Women's Ring Set" if is_set else "Women's Ring"

    # Priority #2: Style
    styles = [tag.capitalize() for tag in tags if tag in ["solitaire", "halo", "heart", "stackable", "eternity", "pavé"]]
    style_str = ' '.join(styles)

    # Priority #3: Stone Info
    stone = "Clear Cubic Zirconia"
    if "simulated crystal" in raw_title.lower():
        stone = "Simulated Crystal"

    color_match = re.search(r"(champagne|blue|clear|pink|purple|green|black|white|red)", raw_title.lower())
    if color_match:
        stone = stone.replace("Clear", color_match.group().capitalize())

    shape = [tag.capitalize() for tag in tags if tag in ["round", "heart", "pear", "square"]]
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

    material = ""
    if "stainless" in raw_title.lower():
        material = "Stainless Steel"
    elif "brass" in raw_title.lower():
        material = "Brass"

    metal_info = f"{plating} {material}".strip()

    # Priority #5: Optional Descriptors
    descriptors = []

    if is_set:
        descriptors.append("2 Pcs")

    if "high polished" in raw_title.lower():
        descriptors.append("High Polished")

    descriptors.append("Gift")  # Only added if there's space later

    # Build base title in priority order
    parts = [base]
    if style_str:
        parts.append(style_str)
    if stone:
        parts.append(stone)
    if metal_info:
        parts.append(metal_info)

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
