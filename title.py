import streamlit as st
import re
import requests
from bs4 import BeautifulSoup
import unicodedata

st.set_page_config(page_title="GC Title Generator")
st.title("🛍️ GC Title Generator")
st.subheader("Create optimized and eye-catching eBay titles for your jewelry listings.")

user_input = st.text_input("Paste AlamodeOnline product URL or enter SKU (e.g. TK3180)")

def is_valid_alamode_url(url):
    return url.startswith("https://alamodeonline.com/products/")

def build_product_url(input_value):
    input_value = input_value.strip()
    if input_value.lower().startswith("https://alamodeonline.com/products/"):
        return input_value
    elif re.match(r"^[a-zA-Z0-9]{5,10}$", input_value):
        return f"https://alamodeonline.com/products/{input_value.lower()}"
    else:
        return None

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

        full_text = soup.get_text(separator=' ').lower()

        return title, tags, full_text
    except Exception as e:
        st.write("DEBUG: Error extracting tags", str(e))
        return None, [], ""

def get_stone_type(product_title, full_text, tags):
    stone_type_substitutions = {
        "top grade crystal": "Simulated Crystal",
        "synthetic glass": "Synthetic Glass",
        "cubic zirconia": "Cubic Zirconia",
        "aaa cubic zirconia": "Cubic Zirconia",
        "aaa cz": "CZ",
        "cz": "CZ",
        "precious stone garnet": "Simulated Garnet",
        "synthetic garnet": "Simulated Garnet",
        "synthetic turquoise": "Simulated Turquoise",
        "precious stone turquoise": "Simulated Turquoise",
        "semi-precious turquoise": "Simulated Turquoise",
        "precious stone conch": "Simulated Stone Conch",
        "precious stone lapis": "Simulated Stone Lapis",
        "precious stone pink crystal": "Simulated Stone PINK CRYSTAL",
        "precious stone amethyst crystal": "Simulated Stone Amethyst Crystal",
        "synthetic acrylic": "Synthetic Acrylic",
        "synthetic imitation amber": "Synthetic Imitation Amber",
        "ceramic": "Ceramic",
        "synthetic synthetic glass": "Synthetic Glass",
        "synthetic glass bead": "Simulated Glass Bead",
        "semi-precious jade": "Simulated Jade",
        "synthetic jade": "Simulated Jade",
        "synthetic cat eye": "Simulated Cat Eye",
        "semi-precious marcasite": "Simulated Marcasite",
        "synthetic spinel": "Simulated Spinel",
        "synthetic pearl": "Simulated Pearl",
        "synthetic synthetic stone": "Synthetic Stone"
    }

    combined_text = (product_title + " " + full_text).lower()
    tags = [tag.lower() for tag in tags]

    if "no stone" in combined_text or "no stone" in tags:
        return None

    for raw_type, formatted in stone_type_substitutions.items():
        if raw_type in combined_text:
            return formatted

    if "aaa grade cz" in tags or "cubic zirconia" in tags:
        return "Cubic Zirconia"

    return None

def transform_title(raw_title, tags, full_text):
    title = re.sub(r'^[A-Z0-9\-]+\s*[-–—]?\s*', '', raw_title)
    raw_title_lower = raw_title.lower()
    used_terms = set()

    def add_term(term):
        lower_term = term.lower()
        if lower_term not in used_terms:
            used_terms.add(lower_term)
            return term
        return None

    normalized_tags = [tag.lower() for tag in tags]
    gender = "Women" if "women" in normalized_tags else "Men" if "men" in normalized_tags else ""
    is_set = "ring sets" in normalized_tags or "set" in raw_title_lower

    product_type = "Ring"  # Fallback default
    if "bands" in normalized_tags and any(r in normalized_tags for r in ["rings", "ring"]):
        product_type = "Ring Band"
    elif "cocktail & statement" in normalized_tags and "rings" in normalized_tags and "women" in normalized_tags:
        product_type = "Cocktail Ring"

    if gender:
        base = add_term(f"{gender}'s {product_type}")
    else:
        base = add_term(product_type)

    style_terms = ["solitaire", "halo", "heart", "stackable", "eternity", "pavé", "midi"]
    styles = [add_term(term.capitalize()) for term in style_terms if term in normalized_tags]
    style_str = ' '.join([s for s in styles if s])

    shape_priority = ["round", "heart", "square", "pear", "triangle", "oblong", "stellar"]
    stone_shape = next((shape.capitalize() for shape in shape_priority if shape in normalized_tags), "")

    matched_type = get_stone_type(raw_title, full_text, tags)

    color = ""
    if matched_type:
        match = re.search(r'in ([a-zA-Z ]+)', raw_title_lower)
        if match:
            raw_color = match.group(1).strip().lower()
            color_map = {
                "ruby": "Red", "turquoise": "Blue", "garnet": "Red", "amethyst": "Purple", "black": "Black",
                "sea blue": "Blue", "montana": "Blue", "clear": "Clear", "siam": "Red", "peridot": "Green"
            }
            color = color_map.get(raw_color, raw_color.title())
        title = re.sub(r'in\s+[a-zA-Z ]+', '', title).strip(', ')

    stone = f"{stone_shape + ' ' if stone_shape else ''}{color + ' ' if color else ''}{matched_type}".strip() if matched_type else ""

    plating = "Sterling Silver" if "sterling" in raw_title_lower else ""
    parts = list(filter(None, [base, style_str, stone, plating]))
    final_title = ', '.join(parts)

    if is_set and len(final_title) + len(", 2 Pcs") <= 80:
        final_title += ", 2 Pcs"
    if "high polished" in raw_title_lower and len(final_title) + len(", High Polished") <= 80:
        final_title += ", High Polished"
    if len(final_title) > 80 and "Cubic Zirconia" in final_title:
        final_title = final_title.replace("Cubic Zirconia", "CZ")
    return final_title.strip()

if "title" not in st.session_state:
    st.session_state.title = ""
if "tags" not in st.session_state:
    st.session_state.tags = []
if "text" not in st.session_state:
    st.session_state.text = ""

product_url = build_product_url(user_input)
if st.button("🔍 Load Product Info") and product_url:
    if is_valid_alamode_url(product_url):
        st.success("✅ Valid product input. Extracting product data...")
        title, tags, text = extract_product_info(product_url)
        st.session_state.title = title
        st.session_state.tags = tags
        st.session_state.text = text
    else:
        st.error("❌ Invalid product URL or SKU format.")

if st.session_state.title and st.session_state.tags:
    st.markdown("### 📝 Extracted Product Info")
    st.write(f"**Title:** {st.session_state.title}")
    st.write(f"**Tags:** {', '.join(st.session_state.tags)}")
    if st.button("✨ Generate Title"):
        final_title = transform_title(st.session_state.title, st.session_state.tags, st.session_state.text)
        st.markdown("### 🛒 Your eBay Title")
        st.text_area("Generated Title", final_title, height=100)
        st.markdown(f"**Character Count:** `{len(final_title)}/80`")
