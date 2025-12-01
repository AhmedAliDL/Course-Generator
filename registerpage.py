import streamlit as st
from SendVerification import SendEmail
from NameValidation import NameValidation
from EmailValidation import EmailValidation
from PasswordHash import PasswordHashing
from coursegeneration import GenerateCourse

GD = GenerateCourse()


def register():
    """
        Implements user registration functionality.

        It allows users to register by providing their name, email, age, gender, and password.
        The function performs various validations on the user input, such as checking for special characters
        in the name, validating the email format, ensuring password length, and matching confirmed password.
        If all validations pass, the function stores the registration data in session state and sends a verification
        code to the user's email address. The verification code is sent based on the email domain (Gmail or Outlook).
        After sending the verification code, the function redirects the user to the verification page.

        Returns:
        - None
        """
    NameV = NameValidation()
    EmailV = EmailValidation()
    SV = SendEmail()
    Phash = PasswordHashing()

    name = st.text_input("Name")
    email = st.text_input("Email")
    age = st.number_input("Age", min_value=15, max_value=100)
    gender = st.selectbox("Gender", ["Male", "Female", "Other"])
    password = st.text_input("Password", type="password")
    confirmed_password = st.text_input("Confirm Password", type="password", )

    if st.button("Register 📋"):

        if NameV.specialCharCheck(name):
            GD.show_dialog("Name should not has special characters or spaces")

        elif NameV.isDublicated(name):
            GD.show_dialog("Name is already used")

        elif not EmailV.isValidEmail(email):
            GD.show_dialog("email not in the common format")

        elif EmailV.isDublicated(email):
            GD.show_dialog("Email is already used")

        elif len(password) < 8:
            GD.show_dialog("Password Length should be greater than 8 characters")

        elif password != confirmed_password:
            GD.show_dialog("Password and confirmed password not matched")

        else:
            # Store registration data in session state
            st.session_state.name = name
            st.session_state.email = email
            st.session_state.age = age
            st.session_state.gender = gender
            st.session_state.password = password

            salt = Phash.generate_salt()
            st.session_state.salt = salt
            HashedPass = Phash.hash_password(salt=salt, password=st.session_state.password)
            st.session_state.password = HashedPass

            # Send verification code
            verification_code = 0
            if SV.is_Gmail(email):
                verification_code = SV.send_To_Gmail(email)

            elif SV.is_Outlook(email):
                verification_code = SV.send_To_Outlook(email)

            else:
                st.warning('Check your email spam')
                verification_code = SV.send_To_Gmail(email)

            st.session_state.verification_code = verification_code
            st.session_state.page = "verification"
            st.experimental_rerun()

    if st.button('Login 🔑'):
        st.session_state.page = 'login'
        st.experimental_rerun()
