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


def parse_wifi_qr(text):
    if not text.startswith("WIFI:"):
        return None
    content = text[5:]

    wifi = {}
    for part in content.split(";"):
        if ":" in part:
            key, value = part.split(":", 1)
            wifi[key] = value

    return {
        "SSID": wifi.get("S", ""),
        "Password": wifi.get("P", ""),
        "Security": wifi.get("T", "Unknown"),
        "Hidden": wifi.get("H", "false"),
    }


def render_decoded_result(decoded_text):
    st.success("✅ QR Code decoded successfully!")
    label = _get_content_label(decoded_text)
    st.caption(f"Detected type: {label}")
    if decoded_text.startswith(("http://", "https://")):
        st.subheader("🔗 Website")

        st.text_input(
            "URL",
            decoded_text,
            disabled=True,
        )

        st.link_button(
            "🌐 Open Website",
            decoded_text,
            use_container_width=True,
        )
        return

    wifi = parse_wifi_qr(decoded_text)
    if wifi:
        st.subheader("📶 Wi-Fi Details")
        col1, col2 = st.columns(2)
        with col1:
            st.metric("SSID", wifi["SSID"])
        with col2:
            st.metric("Security", wifi["Security"])
        st.text_input(
            "Password",
            wifi["Password"],
            disabled=True,
        )
        st.write(
            "**Hidden Network:**",
            "Yes" if wifi["Hidden"].lower() == "true" else "No",
        )
        with st.expander("Raw QR Content"):
            st.code(decoded_text)
        return

    if decoded_text.startswith("mailto:"):
        email = decoded_text.replace("mailto:", "", 1)
        st.subheader("✉️ Email")
        st.text_input(
            "Email Address",
            email,
            disabled=True,
        )
        return

    if decoded_text.startswith("tel:"):
        phone = decoded_text.replace("tel:", "", 1)
        st.subheader("📞 Phone")
        st.text_input(
            "Phone Number",
            phone,
            disabled=True,
        )

        return

    if decoded_text.startswith("upi://"):
        st.subheader("💳 UPI Payment")
        st.code(decoded_text)
        return

    if decoded_text.startswith(("sms:", "smsto:")):
        st.subheader("💬 SMS")
        st.code(decoded_text)
        return

    if decoded_text.startswith(("BEGIN:VCARD", "MECARD:")):
        st.subheader("👤 Contact Card")
        st.code(decoded_text)
        return

    st.subheader("📄 Text")