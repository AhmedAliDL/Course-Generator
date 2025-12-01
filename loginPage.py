import streamlit as st
from DataBase import Database
from EmailValidation import EmailValidation
from PasswordHash import PasswordHashing
from coursegeneration import GenerateCourse

GD = GenerateCourse()


def login():
    """
        Implements the user login functionality.

        It allows users to login using their email or name along with a password.
        The function interacts with the database to validate the user's credentials.

        Steps:
        1. Instantiates Database, EmailValidation, and PasswordHashing classes.
        2. Takes user input for email or name and password.
        3. Validates the email or name provided by the user.
        4. Retrieves the user ID from the database based on the provided email or name.
        5. If the user is found in the database, retrieves the user document using the user ID.
        6. Verifies the provided password against the hashed password stored in the database.
        7. If the password matches, logs in the user and sets the session state to 'user'.
        8. If the login fails, displays appropriate error messages.

        Returns:
        - None
        """
    db = Database()
    EV = EmailValidation()
    phash = PasswordHashing()

    email_or_name = st.text_input("Email or name")
    password = st.text_input("Password", type="password")
    st.session_state.id = '-1'
    if st.button("Login 🔑"):

        if EV.isValidEmail(email_or_name):

            id = db.getIdbyEmail(email_or_name)
            if id == '-1':
                GD.show_dialog('User not found!')
            else:
                st.session_state.id = id
        else:

            id = db.getIdByName(email_or_name)

            if id == '-1':
                GD.show_dialog('User not found!')
            else:
                st.session_state.id = id

        if st.session_state.id != '-1':
            st.session_state.userdoc = db.getUser(st.session_state.id)
            salt = st.session_state.userdoc['salt']
            if phash.hash_password(salt=salt, password=password) == st.session_state.userdoc['password']:
                name = st.session_state.userdoc['name']
                st.success(f"Logged in as {name}.")
                st.session_state.page = "user"
                st.rerun()

            else:
                GD.show_dialog('Password  not correct !')

    if st.button('register 📋'):
        st.session_state.page = "registration"
        st.rerun()

    if st.button('Forget Password 🤦‍♂️'):
        st.session_state.page = "forgetpass"
        st.rerun()
