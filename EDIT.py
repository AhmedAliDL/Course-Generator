import streamlit as st
import DataBase as DB
import PasswordHash as PH
from NameValidation import NameValidation
from coursegeneration import GenerateCourse

GD = GenerateCourse()
ph = PH.PasswordHashing()
db = DB.Database()


def enterPass():
    conpass = st.text_input("Enter your password :  ", type="password")
    if st.button("Submit ✔️"):
        hashed = ph.hash_password(conpass, st.session_state.userdoc['salt'])
        if hashed == st.session_state.userdoc['password']:
            st.session_state.page = "editpage"
            st.rerun()
        else:
            GD.show_dialog("Wrong password")
    if st.button('Home 🏠'):
        st.session_state.page = "user"
        st.rerun()


def editPage():
    NameV = NameValidation()
    # Phash = PH.PasswordHashing()

    name = st.text_input("Name", value=st.session_state.userdoc['name'])
    age = st.number_input("Age", min_value=15, max_value=100, value=st.session_state.userdoc['age'])
    options1 = ["Male", "Female", "Other"]
    if options1[1] == st.session_state.userdoc['gender']:
        options1[1], options1[0] = options1[0], options1[1]
    elif options1[2] == st.session_state.userdoc['gender']:
        options1[2], options1[0] = options1[0], options1[2]

    gender = st.selectbox("Gender", options=[options1[0], options1[1], options1[2]])

    if st.session_state.userdoc['name'] != name or st.session_state.userdoc['gender'] != gender or \
            st.session_state.userdoc['age'] != age:
        if st.button("Save changes"):

            if NameV.specialCharCheck(name):
                GD.show_dialog("Name should not has special characters or spaces")

            elif st.session_state.userdoc['name'] != name:
                if NameV.isDublicated(name):
                    GD.show_dialog("Name is already used")
                else:
                    st.session_state.userdoc['name'] = name

            db.updateName(st.session_state.id, name)
            db.updateGender(st.session_state.id, gender)
            db.updateAge(st.session_state.id, age)
            st.session_state.userdoc['name'] = name
            st.session_state.userdoc['gender'] = gender
            st.session_state.userdoc['age'] = age
            if st.balloons():
                st.success("Your changes have saved successfully")

    if st.button("Change Email ✉"):
        st.session_state.page = "changeemail"
        st.rerun()

    if st.button('Change password 🛡️'):
        st.session_state.page = "chngpass"
        st.rerun()

    if st.button('Home 🏠'):
        st.session_state.page = "user"
        st.rerun()


def changePass():
    password = st.text_input("Enter the new password", type="password")
    conpassword = st.text_input("Confirmed password", type="password")
    PhashInstance = PH.PasswordHashing()
    if st.button("Reset password 🛡️"):
        if len(password) < 8:
            GD.show_dialog("Password Length should be greater than 8 characters")
        elif password == conpassword:

            salt = st.session_state.userdoc['salt']
            HashedPass = PhashInstance.hash_password(salt=salt, password=password)
            if HashedPass == st.session_state.userdoc['password']:
                GD.show_dialog("This is the current password")
            else:
                st.session_state.salt = salt
                st.session_state.password = HashedPass
                st.session_state.userdoc['salt'] = salt
                st.session_state.userdoc['password'] = HashedPass
                db.updatePass(st.session_state.userdoc['email'], HashedPass)
                db.updateSalt(st.session_state.userdoc['email'], salt)
                st.write("Successfully Changed")
                st.session_state.page = "login"
                st.rerun()

        else:
            GD.show_dialog("Password and confirmed password not matched")

    if st.button('Home 🏠'):
        st.session_state.page = "user"
        st.rerun()
