import streamlit as st
import re
import requests
from bs4 import BeautifulSoup

st.set_page_config(page_title="GC Title Generator")
st.title("🛍️ GC Title Generator")
st.subheader("Create optimized and eye-catching eBay titles for your jewelry listings.")

# Step 1: Input field for AlamodeOnline product link
product_url = st.text_input("Paste your AlamodeOnline product URL")

# Step 2: Validate the AlamodeOnline URL
def is_valid_alamode_url(url):
    return bool(re.match(r"https://alamodeonline\.com/.+/products/.+", url))

# Step 3: Extract product title and tags
@st.cache_data(show_spinner=False)
def extract_product_info(url):
    try:
        response = requests.get(url)
        soup = BeautifulSoup(response.text, "html.parser")

        # Extract product title
        title_element = soup.select_one("div.product-info h1")
        title = title_element.get_text(strip=True) if title_element else "Title not found"

        # Extract tags
        tag_spans = soup.select("div#product-tags span.tag")
        tags = [span.get_text(strip=True) for span in tag_spans] if tag_spans else []

        return title, tags
    except Exception as e:
        return "Error", [str(e)]

# Step 4: Display product info
if product_url:
    if is_valid_alamode_url(product_url):
        st.success("✅ Valid AlamodeOnline URL. Extracting product data...")

        title, tags = extract_product_info(product_url)

        st.markdown("### 📝 Extracted Product Info")
        st.write(f"**Title:** {title}")
        st.write(f"**Tags:** {', '.join(tags) if tags else 'No tags found'}")

        st.markdown("---")
        st.markdown("🏗️ Next: We’ll use this info to generate a compliant eBay title.")
    else:
        st.error("❌ This doesn't look like a valid AlamodeOnline product URL. Please check the link.")
