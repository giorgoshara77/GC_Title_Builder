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
    return bool(re.match(r"https://www\.alamodeonline\.com/view-product\?.+", url))

# Step 2: Extract product title and tags
def extract_product_info(url):
    try:
        response = requests.get(url, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')

        # Title
        title_tag = soup.find("h1")
        title = title_tag.text.strip() if title_tag else "No title found"

        # Tags
        tags = []
        tag_spans = soup.find_all("span", class_="tag")
        for span in tag_spans:
            tag = span.text.strip()
            if tag:
                tags.append(tag)

        return title, tags

    except Exception as e:
        return None, []

# Step 3: Display product info
if product_url:
    if is_valid_alamode_url(product_url):
        st.success("✅ Valid AlamodeOnline URL. Extracting product data...")

        title, tags = extract_product_info(product_url)

        st.markdown("### 📝 Product Info Extracted:")
        st.write(f"**Title:** {title}")
        st.write(f"**Tags:** {', '.join(tags) if tags else 'No tags found'}")

        # Placeholder for next step
        st.markdown("---")
        st.markdown("✅ Ready to generate your eBay title in the next step.")
    else:
        st.error("❌ This doesn't look like a valid AlamodeOnline product URL.")


