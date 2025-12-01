import streamlit as st
import EmailValidation as Emv
import SendVerification as SV
import PasswordHash as Phash
import DataBase as db
from coursegeneration import GenerateCourse

GD = GenerateCourse()
EmInstance = Emv.EmailValidation()
SVinstance = SV.SendEmail()
PhashInstance = Phash.PasswordHashing()
dbInstance = db.Database()


def forgetPass():
    user_email = st.text_input("Enter your email address")

    if st.button("Submit ✔️"):
        if not EmInstance.isDublicated(user_email):
            GD.show_dialog("Please enter a valid  and registered email address")

        else:
            if SVinstance.is_Outlook(user_email):
                st.session_state.code = SVinstance.send_To_Outlook(user_email)
            else:
                st.session_state.code = SVinstance.send_To_Gmail(user_email)

            st.session_state.email = user_email
            st.success(f"code sent to {user_email} check it")
            st.session_state.page = "checkcode"
            st.rerun()
    if st.button('Login 🔑'):
        st.session_state.page = "login"
        st.rerun()
