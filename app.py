import io
import qrcode
import streamlit as st
from PIL import Image
from qrcode.image.styledpil import StyledPilImage
from qrcode.image.styles.colormasks import SolidFillColorMask
from qrcode.image.styles.moduledrawers.pil import CircleModuleDrawer, RoundedModuleDrawer
import cv2
import numpy as np

st.set_page_config(page_title="QR Code Generator/Decoder", page_icon="🔗", layout="centered")

st.title("QR Code Generator/Decoder")

tab1, tab2 = st.tabs(["⚙️ Generator", "🔍 Decoder"])


def hex_to_rgb(hex_color):
    hex_color = hex_color.lstrip("#")
    return tuple(int(hex_color[index:index + 2], 16) for index in (0, 2, 4))

with tab1:
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
            file_format = st.selectbox(
                "Download Format",
                ["PNG", "JPG", "SVG"],
                index=0
            )
            module_style = st.selectbox(
                "Module Style",
                ["Classic Squares", "Rounded", "Circles"],
                index=0
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

            if module_style == "Classic Squares":
                image = qr.make_image(
                    fill_color=front_color,
                    back_color=back_color
                ).convert("RGB") # type: ignore
            else:
                module_drawers = {
                    "Rounded": RoundedModuleDrawer(),
                    "Circles": CircleModuleDrawer(),
                }

                image = qr.make_image(
                    image_factory=StyledPilImage,
                    module_drawer=module_drawers[module_style],
                    color_mask=SolidFillColorMask(
                        front_color=hex_to_rgb(front_color), # type: ignore
                        back_color=hex_to_rgb(back_color), # type: ignore
                    ),
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
                
                if file_format == "PNG":
                    image.save(buffer, format="PNG")
                    mime_type = "image/png"
                    ext = "png"
                elif file_format == "JPG":
                    # Ensure image is RGB for JPEG
                    rgb_image = image.convert("RGB")
                    rgb_image.save(buffer, format="JPEG")
                    mime_type = "image/jpeg"
                    ext = "jpg"
                else: # SVG
                    import qrcode.image.svg
                    factory = qrcode.image.svg.SvgImage
                    # We need to recreate the image as SVG because the 'image' variable is a PIL object
                    svg_image = qr.make_image(image_factory=factory)
                    buffer = io.BytesIO()
                    svg_image.save(buffer)
                    mime_type = "image/svg+xml"
                    ext = "svg"

                qr_image = buffer.getvalue()

                st.subheader("Generated QR Code")
                # Always show the PIL image as the preview
                st.image(image, width=300)

                st.download_button(
                    f"Download {file_format}",
                    data=qr_image,
                    file_name=f"qrcode.{ext}",
                    mime=mime_type,
                    use_container_width=True,
                )

with tab2:
    st.write("Upload a QR code image to decode its content.")

    decoded_file = st.file_uploader(
        "Upload QR Code Image",
        type=["png", "jpg", "jpeg"],
        key="decoder_upload"
    )

    if decoded_file is not None:
        decode_img = Image.open(decoded_file).convert("RGB")
        st.image(decode_img, width=250, caption="Uploaded QR Code")

        img_array = np.array(decode_img)
        img_bgr = cv2.cvtColor(img_array, cv2.COLOR_RGB2BGR)

        detector = cv2.QRCodeDetector()
        decoded_text, _, _ = detector.detectAndDecode(img_bgr)

        if decoded_text:
            st.success("✅ QR Code decoded successfully!")
            st.text_area("Decoded Content", value=decoded_text, height=100)

            if decoded_text.startswith("http://") or decoded_text.startswith("https://"):
                st.link_button("Open Link", url=decoded_text, use_container_width=True)
        else:
            st.error("Could not decode the QR code. Make sure the image is clear and contains a valid QR code.")
