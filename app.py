import io

import qrcode
import streamlit as st

st.set_page_config(page_title="QR Code Generator", page_icon="🛠️", layout="centered")


def generate_qr(data: str, fg_color: str, bg_color: str, box_size: int, border: int) -> bytes:
    """Generate a QR code PNG and return it as raw bytes."""
    qr = qrcode.QRCode(
        version=None,
        error_correction=qrcode.constants.ERROR_CORRECT_M,  # type: ignore
        box_size=box_size,
        border=border,
    )
    qr.add_data(data)
    qr.make(fit=True)

    img = qr.make_image(fill_color=fg_color, back_color=bg_color).convert("RGB")  # type: ignore

    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()

st.title("QR Code Generator")
st.caption("Generate QR codes with custom colors, preview them, and download as PNG.")

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
        st.warning(
            "Foreground and background colors are identical — "
            "the QR code won't be scannable. Pick contrasting colors."
        )
    else:
        png_bytes = generate_qr(data, fg_color, bg_color, box_size, border)
        st.subheader("Preview")
        st.image(png_bytes, caption=data, width=300)
        st.download_button(
            label="Download PNG",
            data=png_bytes,
            file_name=f"qr_code_{data.strip()}.png",
            mime="image/png",
            use_container_width=True,
        )