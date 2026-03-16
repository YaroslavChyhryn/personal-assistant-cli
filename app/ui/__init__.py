from __future__ import annotations

import sys
from pathlib import Path

# Ensure the project root is on sys.path so that `app.*` imports work
# when Streamlit runs this file directly.
_PROJECT_ROOT = str(Path(__file__).resolve().parents[2])
if _PROJECT_ROOT not in sys.path:
    sys.path.insert(0, _PROJECT_ROOT)

import streamlit as st

from app.ui.calendar import render_calendar_page
from app.ui.contacts import render_contacts_page
from app.ui.helpers import show_pending_toast
from app.ui.notes import render_notes_page
from app.ui.services import setup


def main() -> None:
    setup()

    st.set_page_config(
        page_title="Personal Assistant",
        layout="wide",
    )

    show_pending_toast()

    pages = st.navigation(
        [
            st.Page(
                render_contacts_page,
                title="Contacts",
                icon=":material/contacts:",
            ),
            st.Page(
                render_notes_page,
                title="Notes",
                icon=":material/note:",
            ),
            st.Page(
                render_calendar_page,
                title="Calendar",
                icon=":material/calendar_month:",
            ),
        ]
    )
    pages.run()


if __name__ == "__main__":
    main()
