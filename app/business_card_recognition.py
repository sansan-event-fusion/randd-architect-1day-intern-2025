import io
import re
from typing import Dict, List, Optional

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


def extract_name(text_blocks: List[tuple], used_blocks: set) -> Optional[str]:
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

    for i, (box, text, conf) in enumerate(text_blocks):
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


def extract_company(text_blocks: List[tuple], used_blocks: set) -> Optional[str]:
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

    for i, (box, text, conf) in enumerate(text_blocks):
        text = text.strip()
        if not text or i in used_blocks:
            continue

        for pattern in company_patterns:
            if re.match(pattern, text):
                used_blocks.add(i)
                return text
    return None


def extract_address(text_blocks: List[tuple], used_blocks: set) -> Optional[str]:
    """Extract address using improved patterns."""
    address_markers = {"県", "市", "区", "町", "村", "郡", "丁目", "番地", "号"}
    postal_code_pattern = r"〒?\d{3}[-−]?\d{4}"

    for i, (box, text, conf) in enumerate(text_blocks):
        text = text.strip()
        if not text or i in used_blocks:
            continue

        # Check for postal code or address markers
        if re.search(postal_code_pattern, text) or any(marker in text for marker in address_markers):
            address_parts = []

            # Look at previous block
            if i > 0 and i - 1 not in used_blocks:
                prev_box, prev_text, prev_conf = text_blocks[i - 1]
                prev_text = prev_text.strip()
                if re.search(postal_code_pattern, prev_text) or any(marker in prev_text for marker in address_markers):
                    address_parts.append(prev_text)
                    used_blocks.add(i - 1)

            address_parts.append(text)
            used_blocks.add(i)

            # Look at next block
            if i < len(text_blocks) - 1 and i + 1 not in used_blocks:
                next_box, next_text, next_conf = text_blocks[i + 1]
                next_text = next_text.strip()
                if any(marker in next_text for marker in address_markers):
                    address_parts.append(next_text)
                    used_blocks.add(i + 1)

            return " ".join(address_parts)
    return None


def extract_contact_info(
    text_blocks: List[tuple], used_blocks: set
) -> tuple[Optional[str], Optional[str], Optional[str]]:
    """Extract email, phone number, and fax using improved patterns."""
    email_pattern = r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"
    phone_pattern = r"(?:(?:TEL|電話|携帯)[\s:：]*)?" r"((?:\+81|0)\d{1,4}[-\s]?\d{1,4}[-\s]?\d{3,4})"
    fax_pattern = r"(?:FAX[\s:：]*)?" r"((?:\+81|0)\d{1,4}[-\s]?\d{1,4}[-\s]?\d{3,4})"

    email = None
    phone = None
    fax = None

    for i, (box, text, conf) in enumerate(text_blocks):
        text = text.strip()
        if not text or i in used_blocks:
            continue

        # Extract email
        if not email and "@" in text:
            email_match = re.search(email_pattern, text)
            if email_match:
                email = email_match.group(0)
                used_blocks.add(i)

        # Extract phone
        if not phone:
            phone_match = re.search(phone_pattern, text)
            if phone_match:
                phone = phone_match.group(1)
                used_blocks.add(i)

        # Extract fax
        if not fax and "FAX" in text.upper():
            fax_match = re.search(fax_pattern, text)
            if fax_match:
                fax = fax_match.group(1)
                used_blocks.add(i)

        if email and phone and fax:
            break

    return email, phone, fax


def extract_department_and_title(text_blocks: List[tuple], used_blocks: set) -> tuple[Optional[str], Optional[str]]:
    """Extract department and title information."""
    department_markers = {"部", "課", "グループ", "チーム", "本部", "事業部", "支社", "支店"}
    title_markers = {"部長", "課長", "社長", "係長", "主任", "取締役", "代表", "リーダー", "マネージャー"}

    department = None
    title = None

    for i, (box, text, conf) in enumerate(text_blocks):
        text = text.strip()
        if not text or i in used_blocks:
            continue

        # Extract department
        if not department and any(marker in text for marker in department_markers):
            if not any(marker in text for marker in title_markers):
                department = text
                used_blocks.add(i)

        # Extract title
        if not title and any(marker in text for marker in title_markers):
            title = text
            used_blocks.add(i)

        if department and title:
            break

    return department, title


def extract_info_from_text(text_blocks: List[tuple]) -> Dict[str, str]:
    """Extract relevant information from OCR text blocks using improved extraction logic."""
    used_blocks = set()  # Track which blocks have been used

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


def process_business_card(file_bytes: bytes, file_type: str) -> Dict[str, str]:
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
        st.error(f"Error processing business card: {str(e)}")
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
