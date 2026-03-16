from __future__ import annotations

import pandas as pd
import streamlit as st

from app.ui.helpers import format_phone
from app.ui.services import get_services


def render_calendar_page() -> None:
    st.header("Upcoming Birthdays")

    days = st.slider("Days ahead", min_value=1, max_value=365, value=7)

    with get_services() as (_cs, _ns, cal_svc):
        contacts = cal_svc.get_upcoming_birthdays(days)
        display_data = [
            {
                "Name": c.name,
                "Birthday": c.birthday.strftime("%d.%m.%Y") if c.birthday else "",
                "Phones": ", ".join(format_phone(p.value) for p in c.phones),
            }
            for c in contacts
        ]

    if not display_data:
        st.info(f"No birthdays in the next {days} day(s).")
    else:
        st.metric("Upcoming Birthdays", len(display_data))

        df = pd.DataFrame(display_data)
        st.dataframe(
            df,
            column_config={
                "Name": st.column_config.TextColumn("Name", width="medium"),
                "Birthday": st.column_config.TextColumn("Birthday", width="small"),
                "Phones": st.column_config.TextColumn("Phones", width="medium"),
            },
            use_container_width=True,
            hide_index=True,
        )
