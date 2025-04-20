import streamlit as st
import re
import requests
from bs4 import BeautifulSoup

st.set_page_config(page_title="GC Title Generator")
st.title("🛍️ GC Title Generator")
st.subheader("Create optimized and eye-catching eBay titles for your jewelry listings.")

product_url = st.text_input("Paste your AlamodeOnline product URL")
load_button = st.button("🔍 Load Product Info")

def is_valid_alamode_url(url):
    return "alamodeonline.com/products/" in url

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
            tags = []
            for a in tag_links:
                tag_text = a.get_text(strip=True).lower().rstrip(',')
                tag_text = tag_text.encode('latin1').decode('utf-8')  # Fix encoding
                if tag_text and tag_text not in tags:
                    tags.append(tag_text)

        st.write("DEBUG: Extracted Tags", tags)
        return title, tags

    except Exception as e:
        st.write("DEBUG: Error extracting tags", str(e))
        return None, []

def transform_title(raw_title, tags):
    title = re.sub(r'^[A-Z0-9\-]+\s*[-–—]?\s*', '', raw_title)

    # Avoid duplicates
    used_words = set()

    is_set = "ring sets" in tags or "set" in raw_title.lower()
    base = "Women's Ring Set" if is_set else "Women's Ring"
    parts = [base]
    used_words.add(base.lower())

    # Style: heart, midi, solitaire, etc.
    style_tags = ["solitaire", "halo", "heart", "stackable", "eternity", "pavé", "midi"]
    style_strs = [tag.capitalize() for tag in style_tags if tag in tags and tag not in used_words]
    for style in style_strs:
        if style.lower() not in used_words:
            parts.append(style)
            used_words.add(style.lower())

    # Stone
    stone = "Clear Cubic Zirconia"
    if "simulated crystal" in raw_title.lower():
        stone = "Simulated Crystal"
    color_match = re.search(r"(champagne|blue|clear|pink|purple|green|black|white|red)", raw_title.lower())
    if color_match:
        stone = stone.replace("Clear", color_match.group().capitalize())

    shape_tags = ["round", "heart", "pear", "square"]
    shape = [tag.capitalize() for tag in shape_tags if tag in tags and tag not in used_words]
    if shape:
        stone = f"{' '.join(shape)} {stone}"
        used_words.update(tag.lower() for tag in shape)

    if stone.lower() not in used_words:
        parts.append(stone)
        used_words.add(stone.lower())

    # Metal info
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

    metal_combo = " ".join([material, plating]).strip() if plating else f"{material} {plating}".strip()
    if metal_combo and metal_combo.lower() not in used_words:
        parts.append(metal_combo.strip())
        used_words.add(metal_combo.lower())

    final_title = ', '.join(parts)

    # No duplicates, max 75 chars
    return final_title[:75]

# ==== UI Logic ====
if product_url and load_button:
    if is_valid_alamode_url(product_url):
        st.success("✅ Valid AlamodeOnline URL. Extracting product data...")
        title, tags = extract_product_info(product_url)

        st.markdown("### 📝 Extracted Product Info")
        st.write(f"**Title:** {title if title else 'No title found'}")
        st.write(f"**Tags:** {', '.join(tags) if tags else 'No tags found'}")

        if title:
            if st.button("✨ Generate Title"):
                final_title = transform_title(title, tags)
                st.markdown("### 🛒 Your eBay Title")
                st.text_area("Generated Title", final_title, height=100)
                st.markdown(f"**Character Count:** `{len(final_title)}/75`")
    else:
        st.error("❌ This doesn't look like a valid AlamodeOnline product URL. Please check the link.")
