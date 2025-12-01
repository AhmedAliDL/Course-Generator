import streamlit as st
import EmailValidation as Emv
import SendVerification as SV
import PasswordHash as Phash
import DataBase as db

EmInstance = Emv.EmailValidation()
SVinstance = SV.SendEmail()
PhashInstance = Phash.PasswordHashing()
dbInstance = db.Database()


def resetPass():
    password = st.text_input("Enter the new password", type="password")
    conpassword = st.text_input("Confirmed password", type="password")

    if st.button("Reset password"):
        if len(password) < 8:
            st.error("Password Length should be greater than 8 characters")
        elif password == conpassword:
            salt = PhashInstance.generate_salt()
            HashedPass = PhashInstance.hash_password(salt=salt, password=password)
            st.session_state.salt = salt
            st.session_state.password = HashedPass
            userid = dbInstance.getIdbyEmail(st.session_state.email)
            userdata = dbInstance.getUser(userid)
            st.session_state.name = userdata['name']
            st.session_state.email = userdata['email']
            st.session_state.age = userdata['age']
            st.session_state.gender = userdata['gender']
            dbInstance.updatePass(st.session_state.email, HashedPass)
            dbInstance.updateSalt(st.session_state.email, salt)
            st.session_state.page = "login"
            st.experimental_rerun()
        else:
            st.error("Password and confirmed password not matched")
