import streamlit as st
from coursegeneration import GenerateCourse

GD = GenerateCourse()


def checkCode():
    Ecode = st.text_input("enter the code: ")
    if st.button("Submit ✔️"):
        if Ecode == st.session_state.code:

            st.session_state.page = "resetpass"
            st.experimental_rerun()

        else:
            GD.show_dialog("the code is wrong")
