from __future__ import annotations

from typing import TypedDict

import streamlit as st

from app.ui.helpers import format_phone, toast, validate_phone
from app.ui.services import get_services


class _ContactDisplay(TypedDict):
    id: int
    name: str
    phones: list[str]
    birthday: str


# ---------------------------------------------------------------------------
# Delete confirmation dialog
# ---------------------------------------------------------------------------


@st.dialog("Delete Contact")
def _confirm_delete_contact(contact_id: int, contact_name: str) -> None:
    st.write(f"Are you sure you want to delete **{contact_name}**?")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Yes, delete", type="primary"):
            try:
                with get_services() as (svc, *_r):
                    svc.delete_contact(contact_id)
                toast("success", f"Contact '{contact_name}' deleted.")
                st.rerun()
            except Exception as exc:
                toast("error", str(exc))
                st.rerun()
    with col2:
        if st.button("Cancel"):
            st.rerun()


# ---------------------------------------------------------------------------
# Inline action forms
# ---------------------------------------------------------------------------


def _add_phone_form(contact_id: int, contact_name: str) -> None:
    new_phone = st.text_input(
        "Phone (10 digits)",
        key=f"ap_phone_{contact_id}",
        max_chars=10,
    )
    if st.button("Add", key=f"ap_submit_{contact_id}", type="primary"):
        err = validate_phone(new_phone)
        if err:
            toast("error", err)
            return
        try:
            with get_services() as (svc, *_r):
                svc.add_phone(contact_name, new_phone.strip())
            toast("success", f"Phone added to '{contact_name}'.")
            st.rerun()
        except (ValueError, KeyError) as exc:
            toast("error", str(exc))


def _change_phone_form(
    contact_id: int,
    contact_name: str,
    old_phone: str,
) -> None:
    st.text(f"Current: {old_phone}")
    new_p = st.text_input(
        "New phone (10 digits)",
        key=f"cp_new_{contact_id}_{old_phone}",
        max_chars=10,
    )
    if st.button("Change", key=f"cp_submit_{contact_id}_{old_phone}", type="primary"):
        err = validate_phone(new_p)
        if err:
            toast("error", err)
            return
        try:
            with get_services() as (svc, *_r):
                svc.change_phone(contact_name, old_phone, new_p.strip())
            toast("success", f"Phone updated for '{contact_name}'.")
            st.rerun()
        except (ValueError, KeyError) as exc:
            toast("error", str(exc))


def _set_birthday_form(contact_id: int, contact_name: str) -> None:
    bday_val = st.date_input("Birthday", value=None, key=f"sb_date_{contact_id}")
    if st.button("Set", key=f"sb_submit_{contact_id}", type="primary"):
        if not bday_val:
            toast("error", "Please select a date.")
            return
        try:
            bday_str = bday_val.strftime("%d.%m.%Y")
            with get_services() as (svc, *_r):
                svc.set_birthday(contact_name, bday_str)
            toast("success", f"Birthday set for '{contact_name}'.")
            st.rerun()
        except (ValueError, KeyError) as exc:
            toast("error", str(exc))


# ---------------------------------------------------------------------------
# Contacts page
# ---------------------------------------------------------------------------


def render_contacts_page() -> None:
    st.header("Contacts")

    tab_list, tab_create = st.tabs(
        [":material/contacts: All Contacts", ":material/person_add: Create Contact"],
    )

    # -- All Contacts -------------------------------------------------------
    with tab_list:
        query = st.text_input(
            "Search by name",
            key="contacts_search",
            placeholder="Type a name…",
        )

        with get_services() as (contacts_svc, *_rest):
            all_contacts = contacts_svc.list_contacts()
            if query:
                contacts_data = contacts_svc.search_contacts(query)
            else:
                contacts_data = all_contacts

            display_data: list[_ContactDisplay] = [
                {
                    "id": c.id,  # type: ignore[typeddict-item]
                    "name": c.name,
                    "phones": [p.value for p in c.phones],
                    "birthday": (c.birthday.strftime("%d.%m.%Y") if c.birthday else ""),
                }
                for c in contacts_data
            ]
            total = len(all_contacts)

        # Metrics
        if query:
            m1, m2 = st.columns(2)
            m1.metric("Total Contacts", total)
            m2.metric("Search Results", len(display_data))
        else:
            st.metric("Total Contacts", total)

        if not display_data:
            st.info("No contacts found.")
        else:
            for item in display_data:
                with st.container(border=True):
                    # Header: name + delete
                    col_name, col_del = st.columns([10, 1])
                    with col_name:
                        st.subheader(item["name"])
                    with col_del:
                        if st.button(
                            ":material/delete:",
                            key=f"del_contact_{item['id']}",
                            help="Delete contact",
                        ):
                            _confirm_delete_contact(item["id"], item["name"])

                    # Phones — each displayed individually with edit/delete
                    st.caption("Phones")
                    if item["phones"]:
                        for phone_val in item["phones"]:
                            ph_disp, ph_edit, ph_del = st.columns([8, 1, 1])
                            with ph_disp:
                                st.markdown(
                                    f":material/phone: **{format_phone(phone_val)}**",
                                )
                            with ph_edit:
                                with st.popover(
                                    ":material/edit:",
                                    key=f"edit_ph_{item['id']}_{phone_val}",
                                    help="Change this phone",
                                ):
                                    _change_phone_form(
                                        item["id"],
                                        item["name"],
                                        phone_val,
                                    )
                            with ph_del:
                                if st.button(
                                    ":material/remove:",
                                    key=f"rm_ph_{item['id']}_{phone_val}",
                                    help="Remove this phone",
                                ):
                                    try:
                                        with get_services() as (svc, *_r):
                                            svc.remove_phone(
                                                item["name"],
                                                phone_val,
                                            )
                                        toast("success", "Phone removed.")
                                        st.rerun()
                                    except (ValueError, KeyError) as exc:
                                        toast("error", str(exc))
                    else:
                        st.write("—")

                    # Birthday
                    st.caption("Birthday")
                    st.write(item["birthday"] or "—")

                    # Actions: add phone + set birthday
                    act1, act2, _spacer = st.columns([2, 2, 6])
                    with act1:
                        with st.popover(":material/add_call: Add Phone"):
                            _add_phone_form(item["id"], item["name"])
                    with act2:
                        with st.popover(":material/cake: Set Birthday"):
                            _set_birthday_form(item["id"], item["name"])

    # -- Create Contact -----------------------------------------------------
    with tab_create:
        with st.form("create_contact"):
            name = st.text_input("Name")
            phone = st.text_input("Phone (10 digits)", max_chars=10)
            birthday = st.date_input("Birthday (optional)", value=None)
            submitted = st.form_submit_button("Create", type="primary")

        if submitted:
            if not name:
                toast("error", "Name is required.")
            elif (phone_err := validate_phone(phone)) is not None:
                toast("error", phone_err)
            else:
                bday_str = birthday.strftime("%d.%m.%Y") if birthday else None
                try:
                    with get_services() as (svc, *_r):
                        svc.create_contact(name, phone.strip(), bday_str)
                    toast("success", f"Contact '{name}' created!")
                    st.rerun()
                except (ValueError, KeyError) as exc:
                    toast("error", str(exc))
