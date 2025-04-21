import streamlit as st
import re
import requests
from bs4 import BeautifulSoup

st.set_page_config(page_title="GC Title Generator")
st.title("🛍️ GC Title Generator")
st.subheader("Create optimized and eye-catching eBay titles for your jewelry listings.")

user_input = st.text_input("Paste AlamodeOnline product URL or enter SKU (e.g. TK3180)")

# Validation
def is_valid_alamode_url(url):
    return url.startswith("https://alamodeonline.com/products/")

def build_product_url(input_value):
    input_value = input_value.strip()
    if input_value.lower().startswith("https://alamodeonline.com/products/"):
        return input_value
    elif re.match(r"^[A-Za-z]{2,4}\d{3,6}[a-z]{0,3}$", input_value):  # Extended pattern
        return f"https://alamodeonline.com/products/{input_value.lower()}"
    else:
        return None

# Data extraction
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
            tags = [a.get_text(strip=True).lower().rstrip(',') for a in tag_links if a.get_text(strip=True)]

        st.write("DEBUG: Extracted Tags", tags)
        return title, tags
    except Exception as e:
        st.write("DEBUG: Error extracting tags", str(e))
        return None, []

# Title transformation
def transform_title(raw_title, tags):
    title = re.sub(r'^[A-Z0-9\-]+\s*[-–—]?\s*', '', raw_title)
    raw_title_lower = raw_title.lower()
    used_terms = set()

    def add_term(term):
        lower_term = term.lower()
        if lower_term not in used_terms:
            used_terms.add(lower_term)
            return term
        return None

    # Audience
    gender = "Women's"
    if "men" in tags:
        gender = "Men's"
    elif "women" in tags:
        gender = "Women's"

    is_set = "ring sets" in tags or "set" in raw_title.lower()
    base = add_term(f"{gender} Ring Set") if is_set else add_term(f"{gender} Ring")

    # Style
    style_terms = ["solitaire", "halo", "heart", "stackable", "eternity", "pavé", "midi"]
    styles = []
    for tag in tags:
        for style in style_terms:
            if style in tag:
                styled = add_term(style.capitalize())
                if styled:
                    styles.append(styled)
                break
    style_str = ' '.join(styles)

    # Stone logic (simplified)
    stone = "Clear Cubic Zirconia"
    if "simulated crystal" in raw_title_lower:
        stone = "Simulated Crystal"
    elif "aaa cz" in raw_title_lower:
        stone = "CZ"
    elif "aaa cubic zirconia" in raw_title_lower:
        stone = "Cubic Zirconia"

    color_match = re.search(r" in (\w+)", raw_title, re.IGNORECASE)
    if color_match:
        color = color_match.group(1).capitalize()
        stone = stone.replace("Clear", color)

    shape_tags = ["round", "heart", "pear", "square", "triangle", "oblong", "stellar"]
    shape = [tag.capitalize() for tag in tags if tag in shape_tags]
    if shape:
        stone = f"{' '.join(shape)} {stone}"

    # Metal info
    plating = ""
    platings_found = []
    if "IP Gold" in raw_title:
        platings_found.append("Gold-Plated")
    if "IP Rose Gold" in raw_title:
        platings_found.append("Rose Gold-Plated")
    if "IP Black" in raw_title:
        platings_found.append("Black-Plated")
    if "IP Brown" in raw_title or "IP Coffee" in raw_title:
        platings_found.append("Brown-Plated")
    if "rhodium" in raw_title_lower or "rhodium" in tags:
        platings_found.append("Rhodium-Plated")

    plating = " & ".join(platings_found[:2])

    material = ""
    if "stainless" in raw_title_lower:
        material = "Stainless Steel"
    elif "brass" in raw_title_lower or "brass" in tags:
        material = "Brass"

    metal_info = " ".join(filter(None, [add_term(material), add_term(plating)]))

    # Descriptors
    descriptors = []
    if "high polished" in raw_title_lower:
        added = add_term("High Polished")
        if added:
            descriptors.append(added)

    parts = list(filter(None, [base, style_str, stone, metal_info]))
    final_title = ', '.join(parts)

    for descriptor in descriptors:
        if len(final_title + ", " + descriptor) <= 80:
            final_title += ", " + descriptor

    if is_set and "2 pcs" not in used_terms:
        if len(final_title + ", 2 Pcs") <= 80:
            final_title += ", 2 Pcs"
            used_terms.add("2 pcs")

    if len(final_title) > 80 and "Cubic Zirconia" in final_title:
        final_title = final_title.replace("Cubic Zirconia", "CZ")

    return final_title.strip()

# UI Logic
if "title" not in st.session_state:
    st.session_state.title = ""
if "tags" not in st.session_state:
    st.session_state.tags = []

product_url = build_product_url(user_input)

if st.button("🔍 Load Product Info") and product_url:
    if is_valid_alamode_url(product_url):
        st.success("✅ Valid product input. Extracting product data...")
        title, tags = extract_product_info(product_url)
        st.session_state.title = title
        st.session_state.tags = tags
    else:
        st.error("❌ Invalid product URL or SKU format.")

if st.session_state.title and st.session_state.tags:
    st.markdown("### 📝 Extracted Product Info")
    st.write(f"**Title:** {st.session_state.title}")
    st.write(f"**Tags:** {', '.join(st.session_state.tags)}")
    st.write("DEBUG: Extracted Tags", st.session_state.tags)

    if st.button("✨ Generate Title"):
        final_title = transform_title(st.session_state.title, st.session_state.tags)
        st.markdown("### 🛒 Your eBay Title")
        st.text_area("Generated Title", final_title, height=100)
        st.markdown(f"**Character Count:** `{len(final_title)}/80`")
