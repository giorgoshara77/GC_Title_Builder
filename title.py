import streamlit as st

st.set_page_config(page_title="GC Title Generator", page_icon="🛍️")

st.title("🛍️ GC Title Generator")
st.subheader("Create optimized and eye-catching eBay titles for your jewelry listings.")

# Input from the user
product_description = st.text_input("Describe your product (e.g., 'gold-plated ring with clear CZ')")

# Title style options
st.markdown("**Choose title style preferences:**")
style_options = st.multiselect(
    "Select style(s) to apply:",
    ["Elegant", "Minimal", "Keyword-rich", "Bold", "Occasion-based"]
)

# Keyword emphasis
emphasize_keywords = st.checkbox("Emphasize important keywords (like 'Gift', 'Fashion', etc.)", value=True)

# Generate button
if st.button("Generate Title"):
    if not product_description:
        st.warning("Please enter a product description.")
    else:
        # Basic logic for demonstration
        base_title = product_description.title()

        if "Elegant" in style_options:
            base_title = "Elegant " + base_title
        if "Minimal" in style_options:
            base_title = base_title.split(",")[0]
        if "Keyword-rich" in style_options:
            base_title += " | Jewelry, Fashion, Gift"
        if "Bold" in style_options:
            base_title = f"**{base_title}**"
        if "Occasion-based" in style_options:
            base_title += " - Perfect for Any Occasion"

        if emphasize_keywords:
            base_title += " 💎"

        st.success("Here's your generated title:")
        st.write(base_title)
