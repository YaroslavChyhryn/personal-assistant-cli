from __future__ import annotations

from typing import TypedDict

import streamlit as st

from app.ui.helpers import toast
from app.ui.services import get_services

BADGE_COLORS: list[str] = ["blue", "green", "violet", "orange", "gray"]


class _NoteDisplay(TypedDict):
    id: int
    title: str
    body: str
    tags: list[str]


# ---------------------------------------------------------------------------
# Delete confirmation dialog
# ---------------------------------------------------------------------------


@st.dialog("Delete Note")
def _confirm_delete_note(note_id: int, note_title: str) -> None:
    st.write(f"Are you sure you want to delete **{note_title}**?")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Yes, delete", type="primary"):
            try:
                with get_services() as (_c, svc, _cal):
                    svc.delete_note(note_id)
                toast("success", f"Note '{note_title}' deleted.")
                st.rerun()
            except Exception as exc:
                toast("error", str(exc))
                st.rerun()
    with col2:
        if st.button("Cancel"):
            st.rerun()


# ---------------------------------------------------------------------------
# Inline tag forms
# ---------------------------------------------------------------------------


def _add_tags_form(note_id: int) -> None:
    tags_raw = st.text_input("Tags (comma-separated)", key=f"add_tags_{note_id}")
    if st.button("Add", key=f"add_tags_submit_{note_id}", type="primary"):
        tag_names = [t.strip() for t in tags_raw.split(",") if t.strip()]
        if not tag_names:
            toast("error", "Enter at least one tag.")
            return
        try:
            with get_services() as (_c, notes_svc, _cal):
                notes_svc.add_tags(note_id, tag_names)
            toast("success", "Tags added!")
            st.rerun()
        except (ValueError, KeyError) as exc:
            toast("error", str(exc))


def _remove_tag_form(note_id: int, tags: list[str]) -> None:
    tag_to_remove = st.selectbox("Select tag to remove", tags, key=f"rm_tag_{note_id}")
    if st.button("Remove", key=f"rm_tag_submit_{note_id}", type="primary"):
        if not tag_to_remove:
            return
        try:
            with get_services() as (_c, notes_svc, _cal):
                notes_svc.remove_tag(note_id, tag_to_remove)
            toast("success", f"Tag '{tag_to_remove}' removed!")
            st.rerun()
        except (ValueError, KeyError) as exc:
            toast("error", str(exc))


# ---------------------------------------------------------------------------
# Notes page
# ---------------------------------------------------------------------------


def render_notes_page() -> None:
    st.header("Notes")

    tab_list, tab_create = st.tabs(
        [":material/note: All Notes", ":material/note_add: Create Note"],
    )

    # -- All Notes ----------------------------------------------------------
    with tab_list:
        col1, col2 = st.columns(2)
        with col1:
            text_query = st.text_input(
                "Search by text",
                key="notes_text_search",
                placeholder="Title or body…",
            )
        with col2:
            tag_query = st.text_input(
                "Search by tag",
                key="notes_tag_search",
                placeholder="Tag name…",
            )

        with get_services() as (_cs, notes_svc, _cal):
            all_notes = notes_svc.list_notes()
            if tag_query:
                filtered = notes_svc.search_by_tag(tag_query)
            elif text_query:
                filtered = notes_svc.search_notes(text_query)
            else:
                filtered = all_notes

            display_data: list[_NoteDisplay] = [
                {
                    "id": n.id,  # type: ignore[typeddict-item]
                    "title": n.title,
                    "body": n.body,
                    "tags": [t.name for t in n.tags],
                }
                for n in filtered
            ]
            total = len(all_notes)

        # Metrics
        if text_query or tag_query:
            m1, m2 = st.columns(2)
            m1.metric("Total Notes", total)
            m2.metric("Search Results", len(display_data))
        else:
            st.metric("Total Notes", total)

        if not display_data:
            st.info("No notes found.")
        else:
            for item in display_data:
                with st.container(border=True):
                    col_title, col_del = st.columns([10, 1])
                    with col_title:
                        st.subheader(item["title"])
                    with col_del:
                        if st.button(
                            ":material/delete:",
                            key=f"del_note_{item['id']}",
                            help="Delete note",
                        ):
                            _confirm_delete_note(item["id"], item["title"])

                    if item["body"]:
                        st.write(item["body"])

                    if item["tags"]:
                        for i, tag in enumerate(item["tags"]):
                            st.badge(
                                tag,
                                icon=":material/label:",
                                color=BADGE_COLORS[i % len(BADGE_COLORS)],  # type: ignore[arg-type]
                            )

                    # Tag management actions
                    tag_col1, tag_col2, _tag_spacer = st.columns([2, 2, 6])
                    with tag_col1:
                        with st.popover(":material/new_label: Add Tags"):
                            _add_tags_form(item["id"])
                    with tag_col2:
                        if item["tags"]:
                            with st.popover(":material/label_off: Remove Tag"):
                                _remove_tag_form(item["id"], item["tags"])

    # -- Create Note --------------------------------------------------------
    with tab_create:
        with st.form("create_note"):
            title = st.text_input("Title")
            body = st.text_area("Body", value="")
            tags_raw = st.text_input("Tags (comma-separated)", value="")
            submitted = st.form_submit_button("Create", type="primary")

        if submitted:
            if not title:
                toast("error", "Title is required.")
            else:
                try:
                    tag_names = [t.strip() for t in tags_raw.split(",") if t.strip()]
                    with get_services() as (_c, notes_svc, _cal):
                        notes_svc.create_note(title, body, tags=tag_names or None)
                    toast("success", f"Note '{title}' created!")
                    st.rerun()
                except (ValueError, KeyError) as exc:
                    toast("error", str(exc))
