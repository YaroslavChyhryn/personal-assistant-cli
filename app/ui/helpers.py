from __future__ import annotations

import streamlit as st

_TOAST_ICONS = {
    "success": ":material/check_circle:",
    "error": ":material/error:",
    "warning": ":material/warning:",
}


def toast(msg_type: str, text: str) -> None:
    """Queue a toast message that survives st.rerun()."""
    st.session_state["_pending_toast"] = (msg_type, text)


def show_pending_toast() -> None:
    """Display and clear any queued toast message."""
    pending = st.session_state.pop("_pending_toast", None)
    if pending:
        msg_type, text = pending
        st.toast(text, icon=_TOAST_ICONS.get(msg_type))


def format_phone(value: str) -> str:
    """Format 10-digit phone as (XXX) XXX-XX-XX."""
    if len(value) == 10 and value.isdigit():
        return f"({value[:3]}) {value[3:6]}-{value[6:8]}-{value[8:]}"
    return value


def validate_phone(value: str) -> str | None:
    """Return an error message if phone is invalid, or None if OK."""
    stripped = value.strip()
    if not stripped:
        return "Phone is required."
    if not stripped.isdigit() or len(stripped) != 10:
        return "Phone must contain exactly 10 digits."
    return None
