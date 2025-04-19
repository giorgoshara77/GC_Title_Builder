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

        # Extract title from meta tag
        meta_title = soup.find("meta", property="og:title")
        title = meta_title["content"].strip() if meta_title else "No title found"

        # Tags – not currently used (fallback only)
        tags = []
        tag_spans = soup.find_all("span", class_="tag")
        for span in tag_spans:
            tag = span.text.strip()
            if tag:
                tags.append(tag)

        return title, tags

    except Exception:
        return None, []

# Step 3: Display product info and show Generate button
if product_url:
    if is_valid_alamode_url(product_url):
        st.success("✅ Valid AlamodeOnline URL. Extracting product data...")

        title, tags = extract_product_info(product_url)

        st.markdown("### 📝 Extracted Product Info")
        st.write(f"**Title:** {title if title else 'No title found'}")
        st.write(f"**Tags:** {', '.join(tags) if tags else 'No tags found'}")

        if title and st.button("✨ Generate Title"):
            # Step 4: Clean and simplify the title for eBay
            cleaned_title = re.sub(r"[^a-zA-Z0-9,| '-]", "", title)
            cleaned_title = cleaned_title.replace("  ", " ")
            final_title = cleaned_title.strip()

            st.markdown("### 🛒 Your eBay Title")
            st.success(final_title)
    else:
        st.error("❌ This doesn't look like a valid AlamodeOnline product URL. Please check the link.")
