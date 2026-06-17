import io
from datetime import datetime

import qrcode
import streamlit as st
from PIL import Image

st.set_page_config(page_title="QR Code Generator", page_icon="🔳", layout="centered")

# ---------- Session state setup ----------
if "history" not in st.session_state:
    st.session_state.history = [] 


def generate_qr(data: str, fg_color: str, bg_color: str, box_size: int, border: int) -> bytes:
    """Generate a QR code PNG and return it as raw bytes."""
    qr = qrcode.QRCode(
        version=None,
        error_correction=qrcode.constants.ERROR_CORRECT_M, # type: ignore
        box_size=box_size,
        border=border,
    )
    qr.add_data(data)
    qr.make(fit=True)

    img = qr.make_image(fill_color=fg_color, back_color=bg_color).convert("RGB") # type: ignore

    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()


# ---------- UI ----------
st.title("🔳 QR Code Generator")
st.caption("Generate QR codes with custom colors, preview them, download as PNG, and revisit your history.")

with st.form("qr_form"):
    data = st.text_input("Text or URL to encode", placeholder="https://example.com")

    col1, col2 = st.columns(2)
    with col1:
        fg_color = st.color_picker("Foreground color", "#000000")
    with col2:
        bg_color = st.color_picker("Background color", "#FFFFFF")

    col3, col4 = st.columns(2)
    with col3:
        box_size = st.slider("Box size (pixel scale)", min_value=4, max_value=20, value=10)
    with col4:
        border = st.slider("Border size", min_value=1, max_value=10, value=4)

    submitted = st.form_submit_button("Generate QR Code", use_container_width=True)

if submitted:
    if not data.strip():
        st.warning("Please enter some text or a URL first.")
    elif fg_color.lower() == bg_color.lower():
        st.warning("Foreground and background colors are identical — the QR code won't be scannable. Pick contrasting colors.")
    else:
        png_bytes = generate_qr(data, fg_color, bg_color, box_size, border)
        st.session_state.last_result = {
            "text": data,
            "fg": fg_color,
            "bg": bg_color,
            "png_bytes": png_bytes,
        }
        st.session_state.history.insert(
            0,
            {
                "text": data,
                "fg": fg_color,
                "bg": bg_color,
                "box_size": box_size,
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "png_bytes": png_bytes,
            },
        )

# ---------- Show latest result ----------
if "last_result" in st.session_state:
    st.subheader("Preview")
    result = st.session_state.last_result
    st.image(result["png_bytes"], caption=result["text"], width=300)
    st.download_button(
        label="Download PNG",
        data=result["png_bytes"],
        file_name=f"qr_code_{data.strip()}.png",
        mime="image/png",
        use_container_width=True,
    )

# ---------- History ----------
st.divider()
st.subheader("History")

if not st.session_state.history:
    st.info("No QR codes generated yet. Your generated codes will appear here.")
else:
    col_a, col_b = st.columns([3, 1])
    with col_b:
        if st.button("Clear history", use_container_width=True):
            st.session_state.history = []
            st.rerun()

    for i, item in enumerate(st.session_state.history):
        with st.container(border=True):
            c1, c2 = st.columns([1, 3])
            with c1:
                st.image(item["png_bytes"], width=100)
            with c2:
                st.write(f"**{item['text']}**")
                st.caption(f"FG: {item['fg']} · BG: {item['bg']} · {item['timestamp']}")
                st.download_button(
                    label="Download",
                    data=item["png_bytes"],
                    file_name=f"qr_code_{data.strip()}.png",
                    mime="image/png",
                    key=f"download_{i}",
                )
