"""SCR-002 — Role Selection.

Analyst selects their role (Author / Reviewer / Approver) on first load.
The selected role is stored in st.session_state["role"] and displayed in
the sidebar header throughout the session. All three screens are accessible
for all three roles in this sprint (no role-gating yet).
"""

import streamlit as st

_ROLES = ["Author", "Reviewer", "Approver"]

_ROLE_DESCRIPTIONS = {
    "Author": (
        "Creates and submits the architecture description for analysis. "
        "Initiates pipeline runs and supplies input data."
    ),
    "Reviewer": (
        "Reviews pipeline outputs and HITL gate artefacts. "
        "Approves or rejects trust boundary decisions and threat assessments."
    ),
    "Approver": (
        "Has final approval authority over the completed threat model and "
        "any associated release decisions."
    ),
}


def render() -> None:
    """Render SCR-002 Role Selection."""
    st.header("Role Selection")
    st.caption("SCR-002 — select your analyst role for this session")

    current_role = st.session_state.get("role", "")

    if current_role:
        st.success(f"Current role: **{current_role}**")
        st.write(_ROLE_DESCRIPTIONS.get(current_role, ""))
        st.divider()
        st.write("Change role:")

    selected = st.radio(
        "Select your role",
        options=_ROLES,
        index=_ROLES.index(current_role) if current_role in _ROLES else 0,
        key="role_radio",
    )

    st.markdown("---")
    st.markdown(f"**{selected}** — {_ROLE_DESCRIPTIONS[selected]}")

    if st.button("Confirm Role", type="primary", use_container_width=True):
        st.session_state["role"] = selected
        st.success(f"Role set to **{selected}**. Navigate using the sidebar.")
        st.rerun()
