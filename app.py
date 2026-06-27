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

if "generated_history" not in st.session_state:
    st.session_state.generated_history = []

if "decoded_history" not in st.session_state:
    st.session_state.decoded_history = []

if "last_generated" not in st.session_state:
    st.session_state.last_generated = None


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
                ).convert("RGB")

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

            st.session_state.generated_history.append({
                "text": text.strip(),
                "image_bytes": qr_image,
            })

            st.session_state.last_generated = {
                "text": text.strip(),
                "image_bytes": qr_image,
            }

    if st.session_state.last_generated:
        st.subheader("Generated QR Code")
        st.image(st.session_state.last_generated["image_bytes"], width=300)
        st.download_button(
            "Download PNG",
            data=st.session_state.last_generated["image_bytes"],
            file_name="qrcode.png",
            mime="image/png",
            use_container_width=True,
        )

    if st.session_state.generated_history:
        st.divider()
        st.subheader("🕒 Generation History")

        col_clear, _ = st.columns([1, 3])
        with col_clear:
            if st.button("Clear History", key="clear_gen_history"):
                st.session_state.generated_history = []
                st.rerun()

        for index, entry in enumerate(reversed(st.session_state.generated_history)):
            entry_index = len(st.session_state.generated_history) - 1 - index
            with st.expander(f"#{entry_index + 1} — {entry['text'][:60]}{'…' if len(entry['text']) > 60 else ''}"):
                st.image(entry["image_bytes"], width=200)
                st.caption(f"Content: {entry['text']}")
                st.download_button(
                    "Download PNG",
                    data=entry["image_bytes"],
                    file_name=f"qrcode_{entry_index + 1}.png",
                    mime="image/png",
                    key=f"download_gen_{entry_index}",
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

        def try_decode(image):
            detector = cv2.QRCodeDetector()
            text, _, _ = detector.detectAndDecode(image)
            return text

        def preprocess_variants(bgr_image):
            """Return preprocessed image variants to attempt decoding on."""
            gray = cv2.cvtColor(bgr_image, cv2.COLOR_BGR2GRAY)
            variants = [bgr_image, gray]
            adaptive = cv2.adaptiveThreshold(
                gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                cv2.THRESH_BINARY, 51, 10
            )
            variants.append(adaptive)
            variants.append(cv2.bitwise_not(adaptive))
            _, otsu = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
            variants.append(otsu)
            variants.append(cv2.bitwise_not(otsu))
            h, w = gray.shape
            upscaled = cv2.resize(gray, (w * 2, h * 2), interpolation=cv2.INTER_CUBIC)
            variants.append(upscaled)
            return variants

        decoded_text = ""
        for variant in preprocess_variants(img_bgr):
            decoded_text = try_decode(variant)
            if decoded_text:
                break

        if decoded_text:
            st.success("✅ QR Code decoded successfully!")
            st.text_area("Decoded Content", value=decoded_text, height=100)

            if decoded_text.startswith("http://") or decoded_text.startswith("https://"):
                st.link_button("Open Link", url=decoded_text, use_container_width=True)

            if not st.session_state.decoded_history or st.session_state.decoded_history[-1]["decoded_text"] != decoded_text:
                st.session_state.decoded_history.append({
                    "filename": decoded_file.name,
                    "decoded_text": decoded_text,
                })
        else:
            st.error("Could not decode the QR code. Make sure the image is clear and contains a valid QR code.")

    if st.session_state.decoded_history:
        st.divider()
        st.subheader("🕒 Decode History")

        col_clear2, _ = st.columns([1, 3])
        with col_clear2:
            if st.button("Clear History", key="clear_dec_history"):
                st.session_state.decoded_history = []
                st.rerun()

        for index, entry in enumerate(reversed(st.session_state.decoded_history)):
            entry_index = len(st.session_state.decoded_history) - 1 - index
            with st.expander(f"#{entry_index + 1} — {entry['filename']}"):
                st.caption(f"File: {entry['filename']}")
                st.text_area(
                    "Decoded Content",
                    value=entry["decoded_text"],
                    height=80,
                    key=f"history_dec_{entry_index}",
                )
                if entry["decoded_text"].startswith("http://") or entry["decoded_text"].startswith("https://"):
                    st.link_button("Open Link", url=entry["decoded_text"], key=f"link_dec_{entry_index}")