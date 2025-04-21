import streamlit as st
import re
import requests
from bs4 import BeautifulSoup

st.set_page_config(page_title="GC Title Generator")
st.title("🛍️ GC Title Generator")
st.subheader("Create optimized and eye-catching eBay titles for your jewelry listings.")

user_input = st.text_input("Paste AlamodeOnline product URL or enter SKU (e.g. TK3180)")

# ✅ URL Builder: supports URL or SKU (even tricky ones like TK1869lj, 1w004, etc.)
def build_product_url(input_value):
    input_value = input_value.strip()
    if input_value.lower().startswith("https://alamodeonline.com/products/"):
        return input_value
    elif re.match(r"^[A-Za-z]{1,3}\d{2,5}[A-Za-z0-9]*$", input_value):  # Updated pattern
        return f"https://alamodeonline.com/products/{input_value.lower()}"
    else:
        return None

def is_valid_alamode_url(url):
    return url.startswith("https://alamodeonline.com/products/")

def extract_product_info(url):
    try:
        response = requests.get(url, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')

        # Extract product title
        meta_title = soup.find("meta", property="og:title")
        title = meta_title["content"].strip() if meta_title else "No title found"

        # Extract tags from visible tag links
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

    # Priority #1: Target Audience + Product Type
    is_set = "ring sets" in tags or "set" in raw_title_lower
    base = add_term("Women's Ring Set") if is_set else add_term("Women's Ring")

    # Priority #2: Style (from tags)
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

    # Priority #3: Stone Info
    stone = "Clear Cubic Zirconia"
    if "simulated crystal" in raw_title_lower:
        stone = "Simulated Crystal"

    if "clear" not in raw_title_lower and "clear" not in tags:
        stone = stone.replace("Clear ", "")  # remove "Clear" if not present in title/tags

    color_match = re.search(r"(champagne|blue|pink|purple|green|black|white|red)", raw_title_lower)
    if color_match:
        color = color_match.group().capitalize()
        stone = stone.replace("Clear", color)

    shape_tag = next((tag.capitalize() for tag in tags if tag in ["round", "heart", "pear", "square"]
                      and tag.capitalize().lower() not in used_terms), None)
    if shape_tag:
        used_terms.add(shape_tag.lower())
        stone = f"{shape_tag} {stone}"

    # Priority #4: Metal Info (supports dual plating)
    platings = []
    if "IP Gold" in raw_title:
        platings.append("Gold-Plated")
    if "IP Rose Gold" in raw_title:
        platings.append("Rose Gold-Plated")
    if "IP Black" in raw_title:
        platings.append("Black-Plated")
    if any(x in raw_title for x in ["IP Brown", "IP Coffee"]):
        platings.append("Brown-Plated")
    if "rhodium" in raw_title_lower or "rhodium" in tags:
        platings.append("Rhodium-Plated")

    unique_platings = list(dict.fromkeys(platings))[:2]  # Max 2 unique, preserve order
    plating_str = " & ".join(unique_platings)

    material = ""
    if "stainless" in raw_title_lower:
        material = "Stainless Steel"
    elif "brass" in raw_title_lower or "brass" in tags:
        material = "Brass"

    metal_info_parts = [add_term(material), add_term(plating_str)]
    metal_info = ' '.join(filter(None, metal_info_parts))

    # Priority #5: Optional Descriptors
    descriptors = []
    if "high polished" in raw_title_lower:
        added = add_term("High Polished")
        if added:
            descriptors.append(added)
    gift = add_term("Gift")
    if gift:
        descriptors.append(gift)

    # Build base title
    parts = list(filter(None, [base, style_str, stone, metal_info]))
    final_title = ', '.join(parts)

    for descriptor in descriptors:
        if len(final_title + ", " + descriptor) <= 75:
            final_title += ", " + descriptor

    # ✅ Add "2 Pcs" at the end ONLY if it's a set and space allows
    if is_set and "2 pcs" not in used_terms:
        if len(final_title + ", 2 Pcs") <= 75:
            final_title += ", 2 Pcs"
            used_terms.add("2 pcs")

    # ✅ Replace Cubic Zirconia with CZ if needed
    if len(final_title) > 75 and "Cubic Zirconia" in final_title:
        final_title = final_title.replace("Cubic Zirconia", "CZ")

    return final_title.strip()

# ========================
# UI Logic
# ========================

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

# Show product info if loaded
if st.session_state.title and st.session_state.tags:
    st.markdown("### 📝 Extracted Product Info")
    st.write(f"**Title:** {st.session_state.title}")
    st.write(f"**Tags:** {', '.join(st.session_state.tags)}")
    st.write("DEBUG: Extracted Tags", st.session_state.tags)

    if st.button("✨ Generate Title"):
        final_title = transform_title(st.session_state.title, st.session_state.tags)
        st.markdown("### 🛒 Your eBay Title")
        st.text_area("Generated Title", final_title, height=100)
        st.markdown(f"**Character Count:** `{len(final_title)}/75`")
