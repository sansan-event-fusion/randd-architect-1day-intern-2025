import io
import re
import typing

import cv2
import easyocr
import numpy as np
import streamlit as st
from pdf2image import convert_from_bytes
from PIL import Image


def preprocess_image(image: Image.Image) -> Image.Image:
    """Preprocess image to improve OCR quality."""
    # Convert PIL Image to OpenCV format
    img = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)

    # Convert to grayscale
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # Apply adaptive thresholding
    binary = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)

    # Denoise
    denoised = cv2.fastNlMeansDenoising(binary)

    # Convert back to PIL Image
    return Image.fromarray(denoised)


@st.cache_resource
def load_ocr_reader():
    """Load EasyOCR reader with caching."""
    return easyocr.Reader(["ja", "en"])


def extract_name(text_blocks: list[tuple], used_blocks: set) -> str | None:
    """Extract name using improved heuristics."""
    # Common titles and positions to exclude
    titles = {
        "部長",
        "課長",
        "社長",
        "部",
        "課",
        "係長",
        "主任",
        "取締役",
        "代表",
        "チーム",
        "グループ",
        "リーダー",
        "マネージャー",
        "所長",
        "会長",
    }

    for i, (_, text, _) in enumerate(text_blocks):
        text = text.strip()
        if not text or i in used_blocks:
            continue

        # Check if text contains only Japanese characters and is of reasonable length
        if 2 <= len(text) <= 10 and all("一" <= c <= "龥" or "ァ" <= c <= "ヶ" or c == " " for c in text):
            # Exclude texts containing titles or positions
            if not any(title in text for title in titles):
                used_blocks.add(i)
                return text
    return None


def extract_company(text_blocks: list[tuple], used_blocks: set) -> str | None:
    """Extract company name using improved patterns."""
    company_patterns = [
        r"株式会社[\s]*.+",
        r".+[\s]*株式会社",
        r"\(株\)[\s]*.+",
        r".+[\s]*\(株\)",
        r"㈱[\s]*.+",
        r".+[\s]*㈱",
        r"合同会社[\s]*.+",
        r".+[\s]*合同会社",
        r"有限会社[\s]*.+",
        r".+[\s]*有限会社",
    ]

    for i, (_, text, _) in enumerate(text_blocks):
        text = text.strip()
        if not text or i in used_blocks:
            continue

        for pattern in company_patterns:
            if re.match(pattern, text):
                used_blocks.add(i)
                return text
    return None


def _has_address_markers(text: str, postal_code_pattern: str, address_markers: set) -> bool:
    """Check if text contains address markers or postal code."""
    return bool(re.search(postal_code_pattern, text) or any(marker in text for marker in address_markers))


def _collect_address_parts(
    text_blocks: list[tuple],
    current_index: int,
    used_blocks: set,
    postal_code_pattern: str,
    address_markers: set,
) -> list[str]:
    """Collect address parts from adjacent blocks."""
    address_parts = []

    # Check previous block
    if current_index > 0 and current_index - 1 not in used_blocks:
        _, prev_text, _ = text_blocks[current_index - 1]
        if _has_address_markers(prev_text.strip(), postal_code_pattern, address_markers):
            address_parts.append(prev_text.strip())
            used_blocks.add(current_index - 1)

    # Add current block
    _, current_text, _ = text_blocks[current_index]
    address_parts.append(current_text.strip())
    used_blocks.add(current_index)

    # Check next block
    if current_index < len(text_blocks) - 1 and current_index + 1 not in used_blocks:
        _, next_text, _ = text_blocks[current_index + 1]
        if _has_address_markers(next_text.strip(), postal_code_pattern, address_markers):
            address_parts.append(next_text.strip())
            used_blocks.add(current_index + 1)

    return address_parts


def extract_address(text_blocks: list[tuple], used_blocks: set) -> str | None:
    """Extract address from text blocks."""
    address_markers = {"県", "市", "区", "町", "村", "郡", "丁目", "番地", "号"}
    postal_code_pattern = r"〒?\d{3}[-−]?\d{4}"

    for i, (_, text, _) in enumerate(text_blocks):
        if i in used_blocks:
            continue

        text = text.strip()
        if not text:
            continue

        if _has_address_markers(text, postal_code_pattern, address_markers):
            address_parts = _collect_address_parts(text_blocks, i, used_blocks, postal_code_pattern, address_markers)
            return " ".join(address_parts)

    return None


def _check_text_validity(text: str, used_blocks: set, block_index: int) -> bool:
    """Check if text block is valid for processing."""
    return bool(text.strip() and block_index not in used_blocks)


def _match_identifier(text: str, identifier: str | None) -> bool:
    """Check if text matches the identifier."""
    return not identifier or identifier in text.upper()


def _extract_pattern_match(text: str, pattern: str) -> str | None:
    """Extract pattern match from text."""
    match = re.search(pattern, text)
    return match.group(1) if match and match.groups() else match.group(0) if match else None


def _extract_contact_detail(
    text_blocks: list[tuple],
    used_blocks: set,
    pattern: str,
    identifier: str | None = None,
) -> str | None:
    """Extract a specific contact detail (email, phone, or fax) from text blocks."""
    for i, (_, text, _) in enumerate(text_blocks):
        if not _check_text_validity(text, used_blocks, i):
            continue

        text = text.strip()
        if not _match_identifier(text, identifier):
            continue

        result = _extract_pattern_match(text, pattern)
        if result:
            used_blocks.add(i)
            return result

    return None


def extract_contact_info(text_blocks: list[tuple], used_blocks: set) -> tuple[str | None, str | None, str | None]:
    """Extract email, phone number, and fax from text blocks."""
    patterns = {
        "email": r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}",
        "phone": r"(?:(?:TEL|電話|携帯)[\s:：]*)?((?:\+81|0)\d{1,4}[-\s]?\d{1,4}[-\s]?\d{3,4})",
        "fax": r"(?:FAX[\s:：]*)?((?:\+81|0)\d{1,4}[-\s]?\d{1,4}[-\s]?\d{3,4})",
    }

    email = _extract_contact_detail(text_blocks, used_blocks, patterns["email"])
    phone = _extract_contact_detail(text_blocks, used_blocks, patterns["phone"])
    fax = _extract_contact_detail(text_blocks, used_blocks, patterns["fax"], "FAX")

    return email, phone, fax


def _check_department_markers(text: str, markers: set[str]) -> bool:
    """Check if text contains department markers."""
    return any(marker in text for marker in markers)


def _process_department(text: str, block_index: int, used_blocks: set, department_markers: set[str]) -> str | None:
    """Process text block for department information."""
    if _check_department_markers(text, department_markers):
        used_blocks.add(block_index)
        return text
    return None


def _process_title(text: str, block_index: int, used_blocks: set, title_markers: set[str]) -> str | None:
    """Process text block for title information."""
    if _check_department_markers(text, title_markers):
        used_blocks.add(block_index)
        return text
    return None


def _extract_single_field(
    text_blocks: list[tuple],
    used_blocks: set,
    markers: set[str],
    process_func: typing.Callable[[str, int, set, set[str]], str | None],
) -> str | None:
    """Extract a single field (department or title) from text blocks.

    Args:
        text_blocks: List of tuples containing OCR results
        used_blocks: Set of already processed block indices
        markers: Set of marker strings to look for
        process_func: Function that processes a single text block

    Returns:
        Extracted field text or None if not found
    """
    for i, (_, text, _) in enumerate(text_blocks):
        if not _check_text_validity(text, used_blocks, i):
            continue

        text = text.strip()
        result = process_func(text, i, used_blocks, markers)
        if result:
            return result

    return None


def extract_department_and_title(text_blocks: list[tuple], used_blocks: set) -> tuple[str | None, str | None]:
    """Extract department and title from text blocks."""
    department_markers = {"部", "課", "グループ", "チーム", "本部", "事業部", "支社", "支店", "営業所"}
    title_markers = {
        "部長",
        "課長",
        "社長",
        "係長",
        "主任",
        "取締役",
        "代表",
        "リーダー",
        "マネージャー",
        "所長",
        "会長",
    }

    department = _extract_single_field(text_blocks, used_blocks, department_markers, _process_department)
    title = _extract_single_field(text_blocks, used_blocks, title_markers, _process_title)

    return department, title


def extract_info_from_text(text_blocks: list[tuple]) -> dict[str, str]:
    """Extract relevant information from OCR text blocks using improved extraction logic."""
    used_blocks: set[int] = set()  # Track which blocks have been used

    # Extract information in order of reliability
    company = extract_company(text_blocks, used_blocks)
    email, phone, fax = extract_contact_info(text_blocks, used_blocks)
    address = extract_address(text_blocks, used_blocks)
    department, title = extract_department_and_title(text_blocks, used_blocks)
    name = extract_name(text_blocks, used_blocks)

    return {
        "name": name or "",
        "company": company or "",
        "department": department or "",
        "title": title or "",
        "address": address or "",
        "email": email or "",
        "phone": phone or "",
        "fax": fax or "",
    }


def process_business_card(file_bytes: bytes, file_type: str) -> dict[str, str]:
    """Process business card image and extract information with improved preprocessing."""
    try:
        if file_type == "pdf":
            # Convert PDF to image
            images = convert_from_bytes(file_bytes)
            if not images:
                raise ValueError("Could not convert PDF to image")
            image = images[0]
        else:
            # For image files
            image = Image.open(io.BytesIO(file_bytes))

        # Convert image to RGB if it's not
        if image.mode != "RGB":
            image = image.convert("RGB")

        # Preprocess image
        processed_image = preprocess_image(image)

        # Perform OCR using EasyOCR
        reader = load_ocr_reader()
        results = reader.readtext(np.array(processed_image))

        # Extract information from OCR results
        extracted_info = extract_info_from_text(results)
        return extracted_info

    except Exception as e:
        st.error(f"Error processing business card: {e!s}")
        return {
            "name": "",
            "company": "",
            "department": "",
            "title": "",
            "address": "",
            "email": "",
            "phone": "",
            "fax": "",
        }


def main():
    st.title("名刺情報抽出")

    uploaded_file = st.file_uploader("名刺画像をアップロード", type=["jpg", "jpeg", "png"])

    if uploaded_file is not None:
        file_bytes = uploaded_file.read()
        file_type = uploaded_file.type

        info = process_business_card(file_bytes, file_type)

        st.subheader("抽出された情報")
        st.write("名前:", info["name"])
        st.write("会社名:", info["company"])
        st.write("部署:", info["department"])
        st.write("役職:", info["title"])
        st.write("住所:", info["address"])
        st.write("電話番号:", info["phone"])
        st.write("メールアドレス:", info["email"])
        st.write("FAX:", info["fax"])


if __name__ == "__main__":
    main()
