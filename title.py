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

        meta_title = soup.find("meta", property="og:title")
        title = meta_title["content"].strip() if meta_title else "No title found"

        tags = []
        tag_spans = soup.find_all("span", class_="tag")
        for span in tag_spans:
            tag = span.text.strip().lower()
            if tag:
                tags.append(tag)

        return title, tags
    except Exception:
        return None, []

def transform_title(raw_title, tags):
    # Remove product code (e.g. TK1318)
    title = re.sub(r'^[A-Z0-9\-]+\s*[-–—]?\s*', '', raw_title)

    # Base
    base = "Women's Ring"
    if "set" in raw_title.lower():
        base = "Women's Ring Set"

    # Materials
    material = ""
    if "stainless" in raw_title.lower():
        material = "Stainless Steel"
    elif "brass" in raw_title.lower():
        material = "Brass"

    # Plating
    plating = ""
    if "IP Gold" in raw_title:
        plating = "Gold Plated"
    elif "IP Rose Gold" in raw_title:
        plating = "Rose Gold Plated"
    elif "IP Black" in raw_title:
        plating = "Black Plated"

    # Stone
    stone = "Clear Cubic Zirconia"
    if "simulated crystal" in raw_title.lower():
        stone = "Simulated Crystal"

    # Shape from tags
    shape = [t.capitalize() for t in tags if t in ["round", "pear", "heart", "square"]]
    if shape:
        stone = f"{' '.join(shape)} {stone}"

    # Styles from tags
    styles = [t.capitalize() for t in tags if t in ["halo", "pavé", "solitaire", "eternity"]]

    # Final title parts
    parts = [base]
    parts += styles
    if plating:
        parts.append(plating)
    if material:
        parts.append(material)
    parts += ["with", stone, "Gift Jewelry"]

    final = ' '.join(parts)
    final = final.replace("  ", " ")

    return final.strip()[:75]

# App logic
if product_url:
    if is_valid_alamode_url(product_url):
        st.success("✅ Valid AlamodeOnline URL. Extracting product data...")
        title, tags = extract_product_info(product_url)

        st.markdown("### 📝 Extracted Product Info")
        st.write(f"**Title:** {title if title else 'No title found'}")
        st.write(f"**Tags:** {', '.join(tags) if tags else 'No tags found'}")

        if title and st.button("✨ Generate Title"):
            final_title = transform_title(title, tags)
            st.markdown("### 🛒 Your eBay Title")
            st.text_area("Generated Title", final_title, height=100)
            st.markdown(f"**Character Count:** `{len(final_title)}/75`")
    else:
        st.error("❌ This doesn't look like a valid AlamodeOnline product URL. Please check the link.")
