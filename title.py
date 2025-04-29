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

    product_type = ""
    if "bands" in normalized_tags and any(r in normalized_tags for r in ["rings", "ring"]):
        product_type = "Ring Band"
    elif "cocktail & statement" in normalized_tags and any(r in normalized_tags for r in ["rings", "ring"]) and "women" in normalized_tags:
        product_type = "Cocktail Ring"
    elif "earrings" in normalized_tags and "women" in normalized_tags:
        if "stud" in normalized_tags:
            product_type = "Stud Earrings"
        elif "dangle & drop" in normalized_tags:
            product_type = "Dangle & Drop Earrings"
        elif "hoops & huggies" in normalized_tags:
            product_type = "Hoops & Huggies Earrings"
        else:
            product_type = "Earrings"
    elif "rings" in normalized_tags or re.search(r'\bring\b', raw_title_lower):
        product_type = "Ring Set" if is_set else "Ring"
    elif "bracelet" in normalized_tags or "bracelet" in raw_title_lower:
        product_type = "Bracelet"
    elif "necklaces" in normalized_tags:
        if "chain pendant" in normalized_tags and "chain pendant" in raw_title_lower:
            product_type = "Chain Pendant Necklace"
            title = re.sub(r"(?i)\bpendant with\b", "", title).strip(", ")
            raw_title_lower = title.lower()
        elif "pendant" in normalized_tags and "pendant" in raw_title_lower:
            product_type = "Pendant"
        else:
            product_type = "Necklace"

    if gender and product_type:
        base = add_term(f"{gender}'s {product_type}")
    elif product_type:
        base = add_term(product_type)
    else:
        base = add_term("Jewelry")

    style_terms = ["solitaire", "halo", "heart", "stackable", "eternity", "pavé", "midi"]
    normalized_style_map = {unicodedata.normalize("NFKD", term).encode("ASCII", "ignore").decode().lower(): term.capitalize() for term in style_terms}
    styles = []
    for tag in tags:
        tag_normalized = unicodedata.normalize("NFKD", tag).encode("ASCII", "ignore").decode().lower()
        for norm_term, display_term in normalized_style_map.items():
            if norm_term in tag_normalized:
                added = add_term(display_term)
                if added:
                    styles.append(added)
                break
    style_str = ' '.join(styles)

    stone_shape = ""
    shape_priority = ["round", "heart", "square", "pear", "triangle", "oblong", "stellar"]
    for shape in shape_priority:
        if shape in normalized_tags:
            stone_shape = shape.capitalize()
            break

    stone_color_substitutions = {
        "jet": "Black", "black": "Black", "light gray": "Light Gray", "gray": "Gray", "white": "White",
        "clear": "Clear", "siam": "Red", "ruby": "Red", "rose": "Rose", "garnet": "Red", "light rose": "Rose",
        "orange": "Orange", "champagne": "Champagne", "multi color": "Multicolor", "citrine yellow": "Yellow",
        "topaz": "Yellow", "citrine": "Yellow", "light gold": "Light Gold", "emerald": "Green", "blue zircon": "Blue",
        "peridot": "Green", "olivine color": "Green", "apple green color": "Green", "sapphire": "Blue",
        "montana": "Blue", "sea blue": "Blue", "aquamarine": "Blue", "london blue": "Blue", "tanzanite": "Blue",
        "amethyst": "Purple", "light amethyst": "Light Purple", "brown": "Brown", "smoked quartz": "Smoky Brown",
        "coffee": "Coffee", "light coffee": "Coffee"
    }

    stone_type_substitutions = {
        "synthetic pearl": "Simulated Pearl", "top grade crystal": "Simulated Crystal",
        "synthetic glass": "Synthetic Glass", "cubic zirconia": "Cubic Zirconia",
        "aaa cubic zirconia": "Cubic Zirconia", "aaa cz": "CZ", "cz": "CZ",
        "precious stone garnet": "Simulated Garnet", "synthetic garnet": "Simulated Garnet",
        "synthetic turquoise": "Simulated Turquoise", "precious stone turquoise": "Simulated Turquoise",
        "semi-precious turquoise": "Simulated Turquoise"
    }

    stone = ""
    matched_type = None
    combined_text = raw_title_lower + " " + full_text

    # Skip stone detection if 'No Stone' found
    if "no stone" not in raw_title_lower and "no stone" not in full_text and "no stone" not in normalized_tags:
        for raw_type, formatted in stone_type_substitutions.items():
            if raw_type in combined_text:
                matched_type = formatted
                break

    if matched_type:
        match = re.search(r'in ([a-zA-Z ]+)', raw_title_lower)
        if match:
            raw_color = match.group(1).strip().lower()
            color = stone_color_substitutions.get(raw_color, raw_color.title())
        else:
            color = ""

        title = re.sub(r'in\s+[a-zA-Z ]+', '', title).strip(', ')
        raw_title_lower = title.lower()

        if color:
            stone = f"{stone_shape + ' ' if stone_shape else ''}{color} {matched_type}".strip()
        else:
            stone = f"{stone_shape + ' ' if stone_shape else ''}{matched_type}".strip()

    plating_keywords = {
        "ip gold": "Gold-Plated", "ip rose gold": "Rose Gold-Plated", "ip black": "Black-Plated",
        "ip brown": "Brown-Plated", "ip light brown": "Brown-Plated", "ip coffee": "Brown-Plated",
        "ip light coffee": "Brown-Plated", "rhodium": "Rhodium-Plated"
    }
    platings_found = [label for keyword, label in plating_keywords.items() if keyword in raw_title_lower]
    plating = f"{platings_found[1].split('-')[0]} & {platings_found[0]}" if len(platings_found) == 2 else platings_found[0] if platings_found else ""

    material = ""
    if "stainless" in raw_title_lower:
        material = "Stainless Steel"
    elif "925 sterling silver" in raw_title_lower or "simply sterling" in normalized_tags or "925 sterling silver" in normalized_tags:
        material = "Sterling Silver"
    elif "iron" in raw_title_lower or "iron" in normalized_tags:
        material = "Iron"
    elif "brass" in raw_title_lower or "brass" in normalized_tags:
        material = "Brass"

    metal_info_parts = [add_term(material), add_term(plating)]
    metal_info = ' '.join(filter(None, metal_info_parts))

    parts = list(filter(None, [base, style_str, stone, metal_info]))
    final_title = ', '.join(parts)

    if is_set and "2 pcs" not in used_terms and len(final_title + ", 2 Pcs") <= 80:
        final_title += ", 2 Pcs"
        used_terms.add("2 pcs")

    if "high polished" in raw_title_lower and len(final_title + ", High Polished") <= 80:
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
