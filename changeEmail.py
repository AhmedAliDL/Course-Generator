import streamlit as st
import EmailValidation as EV
import SendVerification as SV
from coursegeneration import GenerateCourse

GD = GenerateCourse()


def changeEmailPage():
    emailV = EV.EmailValidation()
    sendV = SV.SendEmail()
    email = st.text_input("Enter the new email")
    if st.button("Verify ✔️"):
        if not emailV.isValidEmail(email):
            GD.show_dialog("Not valid Email")
        elif st.session_state.userdoc['email'] != email:
            if emailV.isDublicated(email):
                GD.show_dialog("Email is already used")
            else:
                if sendV.is_Outlook(email):
                    st.session_state.verification_code = sendV.send_To_Outlook(email)
                else:
                    st.session_state.verification_code = sendV.send_To_Gmail(email)

                # todo
                st.session_state.userdoc['email'] = email
                st.session_state.email = email
                st.session_state.page = "emailver2"
                st.experimental_rerun()

        else:
            GD.show_dialog("the email can't be the same")

    if st.button('Home 🏠'):
        st.session_state.page = "user"
        st.rerun()
