import streamlit as st

_LABEL_MAP = {
    ("http://", "https://"): "🔗 URL",
    ("WIFI:",): "📶 Wi-Fi Credentials",
    ("BEGIN:VCARD", "MECARD:"): "👤 Contact Card",
    ("mailto:",): "✉️ Email Address",
    ("tel:",): "📞 Phone Number",
    ("upi://",): "💳 UPI Payment",
    ("smsto:", "sms:"): "💬 SMS",
}


def _get_content_label(text):
    text = text.strip()

    for prefixes, label in _LABEL_MAP.items():
        if any(text.startswith(prefix) for prefix in prefixes):
            return label

    return "📄 Plain Text"


def render_decoded_result(decoded_text):
    st.success("✅ QR Code decoded successfully!")

    label = _get_content_label(decoded_text)
    st.caption(f"Detected type: {label}")

    st.code(decoded_text, language=None)
    
    if decoded_text.startswith(("http://", "https://")):
        st.link_button(
            "🌐 Open Link",
            url=decoded_text,
            use_container_width=True,
        )