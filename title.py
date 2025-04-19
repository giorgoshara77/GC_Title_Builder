import streamlit as st
import re

st.set_page_config(page_title="GC Title Generator")
st.title("🛍️ GC Title Generator")
st.subheader("Create optimized and eye-catching eBay titles for your jewelry listings.")

# Step 1: Input field for AlamodeOnline product link
product_url = st.text_input("Paste your AlamodeOnline product URL")

# Function to validate AlamodeOnline URLs
def is_valid_alamode_url(url):
    return bool(re.match(r"https://www\.alamodeonline\.com/view-product\?.+", url))

# Show URL status
if product_url:
    if is_valid_alamode_url(product_url):
        st.success("✅ Valid AlamodeOnline URL. Ready to extract product data.")
        st.info("🔧 In the next step, we'll extract title, tags, and other info from this link.")
    else:
        st.error("❌ This doesn't look like a valid AlamodeOnline product URL. Please check the link.")

# Placeholder for next steps
st.markdown("---")
st.markdown("🚧 Next: We'll implement the product info extractor and title generator.")

