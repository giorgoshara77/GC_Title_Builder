import streamlit as st
import re
import requests
from bs4 import BeautifulSoup

st.set_page_config(page_title="GC Title Generator")
st.title("🛍️ GC Title Generator")
st.subheader("Create optimized and eye-catching eBay titles for your jewelry listings.")

# Step 1: Input field for AlamodeOnline product link
product_url = st.text_input("Paste your AlamodeOnline product URL")

# Validate the AlamodeOnline URL
def is_valid_alamode_url(url):
    return bool(re.match(r"https://alamodeonline\.com/.+/products/.+", url))

# Step 2: Extract product title and tags
def extract_product_info(url):
    try:
        response = requests.get(url, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')

        meta_title = soup.find("meta", property="og:title")
        title = meta_title["content"].strip() if meta_title else "No title found"

        tags = []
        tag_spans = soup.find_all("span", class_="tag")
        for span in tag_spans:
            tag = span.text.strip()
            if tag:
                tags.append(tag)

        return title, tags
    except Exception:
        return None, []

# Step 3: Clean + Optimize Title
def optimize_title(original_title, tags=None):
    if not original_title:
        return "No title found"

    # Remove SKU or product code (e.g., TK1318 - )
    cleaned = re.sub(r"^[A-Z0-9\-]+\s*[-–—]\s*", "", original_title)

    # Capitalize key terms
    cleaned = cleaned.replace("aaa grade cz", "AAA CZ")
    cleaned = cleaned.replace("no plating", "no plating")
    cleaned = cleaned.replace("stainless steel", "Stainless Steel")
    cleaned = cleaned.replace("high polished", "High Polished")

    # Optional: Add helpful eBay keywords if space allows
    if len(cleaned) < 70:
        cleaned += " | Gift"

    # Final cleanup
    cleaned = cleaned.strip()
    cleaned = re.sub(r"\s{2,}", " ", cleaned)

    # Limit to 75 characters
    return cleaned[:75]

# Step 4: App logic
if product_url:
    if is_valid_alamode_url(product_url):
        st.success("✅ Valid AlamodeOnline URL. Extracting product data...")
        title, tags = extract_product_info(product_url)

        st.markdown("### 📝 Extracted Product Info")
        st.write(f"**Title:** {title if title else 'No title found'}")
        st.write(f"**Tags:** {', '.join(tags) if tags else 'No tags found'}")

        if title and st.button("✨ Generate Title"):
            final_title = optimize_title(title, tags)
            st.markdown("### 🛒 Your eBay Title")
            st.success(final_title)
    else:
        st.error("❌ This doesn't look like a valid AlamodeOnline product URL. Please check the link.")
