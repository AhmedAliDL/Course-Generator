import streamlit as st
from DataBase import Database
from coursegeneration import GenerateCourse

GD = GenerateCourse()


def emailVerification():
    """
    This function handles the email verification process in a Streamlit application.

    It performs the following tasks:
    1. Displays a title for the email verification page.
    2. Accepts a verification code input from the user.
    3. Verifies the entered code against the session-stored verification code.
    4. If the code is correct, displays a success message and user details.
    5. If the code is incorrect, displays an error message.
    6. Inserts user details into the database upon successful verification.
    7. Changes the session page state to "login" upon successful verification.

    Steps:
    - Fetch the verification code stored in the session state.
    - Compare the input verification code with the stored one.
    - On a match, register the user by inserting their details into the database.
    - On a mismatch, prompt the user to try again.

    """
    db = Database()

    # Display the title for the email verification page.
    st.subheader("Email Verification")

    # Input field for the user to enter their verification code.
    user_code = st.text_input("Enter Verification Code")

    # Button to trigger the verification process.
    if st.button('verify'):
        # Check if the entered code matches the stored verification code.
        if user_code == st.session_state.verification_code:
            # If verification is successful, display success message and user details.
            st.success(f"Successfully registered as {st.session_state.name}.")
            st.write(f"Name: {st.session_state.name}")
            st.write(f"Email: {st.session_state.email}")
            st.write(f"Age: {st.session_state.age}")
            st.write(f"Gender: {st.session_state.gender}")

            # Prepare the user document for insertion into the database.
            userdoc = {
                "name": st.session_state.name,
                "email": st.session_state.email,
                "age": st.session_state.age,
                "gender": st.session_state.gender,
                'salt': st.session_state.salt,
                "password": st.session_state.password
            }

            # Insert the user document into the database.
            db.insertUser(userdoc)

            # Update the session state to navigate to the login page.
            st.session_state.page = "login"
        elif user_code:
            # If the entered code is incorrect, display an error message.
            GD.show_dialog("Incorrect verification code. Please try again.")
