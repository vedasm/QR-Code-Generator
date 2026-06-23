import io
import qrcode
import streamlit as st
from PIL import Image

st.set_page_config(page_title="QR Code Generator", page_icon="🔗", layout="centered")

st.title("QR Code Generator")
st.write("Enter any text or link below to create a QR code.")

with st.form("qr_form"):
    text = st.text_input("Enter Text or URL", placeholder="https://example.com")
    col1, col2 = st.columns(2)

    with col1:
        front_color = st.color_picker("QR Color","#000000")

    with col2:
        back_color = st.color_picker("Background", "#FFFFFF")

    qr_size = st.selectbox(
        "QR Code Size",
        ["Small", "Medium", "Large", "HD"],
        index=1
    )

    logo = st.file_uploader(
        "Upload Logo (Optional)",
        type=["png", "jpg", "jpeg"]
    )

    generate = st.form_submit_button(
        "Generate QR Code",
        use_container_width=True
    )

if generate:
    if text.strip() == "":
        st.warning("Please enter some text or URL.")

    elif front_color == back_color:
        st.warning("QR color and background color cannot be the same.")

    else:
        size_map = {
            "Small": 5,
            "Medium": 8,
            "Large": 12,
            "HD": 18
        }


        qr = qrcode.QRCode(
            version=None,
            error_correction=qrcode.constants.ERROR_CORRECT_H, # type: ignore
            box_size=size_map[qr_size],
            border=2,
        )

        qr.add_data(text)
        qr.make(fit=True)

        image = qr.make_image(
            fill_color=front_color,
            back_color=back_color
        ).convert("RGB") # type: ignore

        if logo is not None:

            logo_img = Image.open(logo).convert("RGBA")

            qr_width, qr_height = image.size
            logo_size = qr_width // 5

            logo_img.thumbnail((logo_size, logo_size))
            x = (qr_width - logo_img.width) // 2
            y = (qr_height - logo_img.height) // 2

            image.paste(logo_img, (x, y), logo_img)

        buffer = io.BytesIO()
        image.save(buffer, format="PNG")

        qr_image = buffer.getvalue()

        st.subheader("Generated QR Code")
        st.image(qr_image, width=300)

        st.download_button(
            "Download PNG",
            data=qr_image,
            file_name="qrcode.png",
            mime="image/png",
            use_container_width=True,
        )