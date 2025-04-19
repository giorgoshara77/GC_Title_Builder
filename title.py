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
@st.cache_data(show_spinner=False)
def extract_product_info(url):
    try:
        response = requests.get(url)
        soup = BeautifulSoup(response.text, "html.parser")

        # Extract title
        title_element = soup.find("h1", class_="product-title")
        title = title_element.get_text(strip=True) if title_element else "Title not found"

        # Extract tags
        tags_section = soup.find("div", class_="tags")
        tags = [tag.get_text(strip=True) for tag in tags_section.find_all("a")] if tags_section else []

        return title, tags
    except Exception as e:
        return "Error", [str(e)]

# Step 3: Display product info
if product_url:
    if is_valid_alamode_url(product_url):
        st.success("✅ Valid AlamodeOnline URL. Extracting product data...")

        title, tags = extract_product_info(product_url)

        if title == "Error":
            st.error("❌ Failed to extract product info.")
        else:
            st.markdown("---")
            st.markdown("### 📝 Extracted Product Info")
            st.write(f"**Title:** {title}")
            st.write(f"**Tags:** {', '.join(tags) if tags else 'No tags found'}")
    else:
        st.error("❌ This doesn't look like a valid AlamodeOnline product URL. Please check the link.")

# Placeholder for next step
st.markdown("---")
st.markdown("🚧 Next: We’ll use this info to generate a compliant eBay title.")



