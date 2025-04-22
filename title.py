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

    def normalize(text):
        return unicodedata.normalize("NFKD", text).encode("ASCII", "ignore").decode().lower()

    # Target Audience
    is_set = "ring sets" in tags or "set" in raw_title_lower
    if "men" in tags:
        base = add_term("Men's Ring")
    elif "women" in tags:
        base = add_term("Women's Ring Set" if is_set else "Women's Ring")
    else:
        base = add_term("Ring")

    # Style
    style_terms = ["solitaire", "halo", "heart", "stackable", "eternity", "pavé", "midi"]
    normalized_style_map = {normalize(term): term.capitalize() for term in style_terms}
    styles = []
    for tag in tags:
        tag_normalized = normalize(tag)
        for norm_term, display_term in normalized_style_map.items():
            if norm_term in tag_normalized:
                added = add_term(display_term)
                if added:
                    styles.append(added)
                break
    style_str = ' '.join(styles)

    # === STONE SHAPE DETECTION ===
    stone_shape = ""
    shape_priority = ["round", "heart", "square", "pear", "triangle", "oblong", "stellar"]
    for shape in shape_priority:
        if shape in [tag.lower() for tag in tags]:
            stone_shape = shape.capitalize()
            break

    # === STONE DETECTION ===
    stone_type_substitutions = {
        "top grade crystal": "Simulated Crystal", "synthetic glass": "Synthetic Glass",
        "cubic zirconia": "Cubic Zirconia", "aaa cubic zirconia": "Cubic Zirconia", "aaa cz": "CZ", "cz": "CZ",
        "epoxy": "Epoxy", "precious stone conch": "Simulated Stone Conch",
        "precious stone lapis": "Simulated Stone Lapis", "precious stone pink crystal": "Simulated Stone PINK CRYSTAL",
        "precious stone amethyst crystal": "Simulated Stone Amethyst Crystal", "synthetic acrylic": "Synthetic Acrylic",
        "synthetic imitation amber": "Synthetic Imitation Amber", "ceramic": "Ceramic",
        "synthetic synthetic glass": "Synthetic Glass", "synthetic glass bead": "Simulated Glass Bead",
        "semi-precious jade": "Simulated Jade", "synthetic jade": "Simulated Jade",
        "synthetic cat eye": "Simulated Cat Eye", "semi-precious marcasite": "Simulated Marcasite",
        "synthetic spinel": "Simulated Spinel", "synthetic turquoise": "Simulated Turquoise",
        "synthetic pearl": "Simulated Pearl", "synthetic synthetic stone": "Synthetic Stone"
    }

    stone_color_substitutions = {
        "jet": "Black", "black": "Black", "light gray": "Gray", "gray": "Gray", "white": "White",
        "clear": "Clear", "siam": "Red", "ruby": "Ruby-Colored", "rose": "Rose", "garnet": "Garnet-Colored",
        "light rose": "Rose", "orange": "Orange", "champagne": "Champagne", "multi color": "Multicolor",
        "citrine yellow": "Yellow", "topaz": "Topaz-Colored", "citrine": "Citrine-Colored", "light gold": "Light Gold",
        "emerald": "Emerald-Colored", "blue zircon": "Blue", "peridot": "Peridot Colored",
        "olivine color": "Olive Green", "apple green color": "Apple Green", "sapphire": "Sapphire-Colored",
        "montana": "Montana", "sea blue": "Sea Blue", "aquamarine": "Aquamarine", "london blue": "Blue",
        "tanzanite": "Tanzanite-Colored", "amethyst": "Amethyst-Colored", "light amethyst": "Amethyst-Colored",
        "brown": "Brown", "smoked quartz": "Smoky Brown", "coffee": "Coffee", "light coffee": "Coffee"
    }

    normalized_tags = [tag.strip().lower() for tag in tags]
    stone = ""
    if "epoxy" in raw_title_lower or "epoxy" in normalized_tags:
        stone = "Epoxy"
    elif "no stone" in raw_title_lower or "no stone" in normalized_tags:
        stone = ""
    else:
        matched_type = None
        for raw_type, formatted in stone_type_substitutions.items():
            if raw_type in raw_title_lower or raw_type in normalized_tags:
                matched_type = formatted
                break
        if matched_type:
            match = re.search(r'in ([a-zA-Z ]+)', raw_title_lower)
            if match:
                raw_color = match.group(1).strip().lower()
                color = stone_color_substitutions.get(raw_color, raw_color.title())
                if stone_shape:
                    stone = f"{stone_shape} {color} {matched_type}"
                else:
                    stone = f"{color} {matched_type}"
            else:
                if stone_shape:
                    stone = f"{stone_shape} {matched_type}"
                else:
                    stone = matched_type
        elif "cz" in raw_title_lower:
            stone = "Cubic Zirconia"

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

    descriptors = []
    if "high polished" in raw_title_lower:
        added = add_term("High Polished")
        if added:
            descriptors.append(added)

    parts = list(filter(None, [base, style_str, stone, metal_info]))
    final_title = ', '.join(parts)

    # Priority: 1) 2 Pcs, 2) High Polished (already prioritized), stone shape already used inside "stone"
    if is_set and "2 pcs" not in used_terms and len(final_title + ", 2 Pcs") <= 80:
        final_title += ", 2 Pcs"
        used_terms.add("2 pcs")

    for descriptor in descriptors:
        if descriptor.lower() == "high polished" and len(final_title + ", " + descriptor) <= 80:
            final_title += ", " + descriptor
            break

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
