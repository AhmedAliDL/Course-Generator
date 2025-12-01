import logging
from registerpage import register
from EmailverPage import emailVerification
from loginPage import login
from UserPage import userPage
import streamlit as st
import forgetpassPage as fpp
import checkcodePage as ccp
import resetpassPage as rpp
import EDIT as ed
import changeEmail as ce
import EmailVer2 as EV2

logger = logging.getLogger(__name__)

# change page icon and more
st.set_page_config(
    page_title="Course Generator",
    page_icon="📖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# remove made with streamlit and hamburger
st.markdown("""
<style>
.css-fblp2m.ex0cdmw0
{
  visibility:hidden;
}
.css-nncgp3.egzxvld1
{
 visibility:hidden;
}
.st-emotion-cache-1wbqy5l.e17vllj40
{
 visibility:hidden;
}
<style/>
""", unsafe_allow_html=True)


def main():
    """this main function to handle and design streamlit of this project
    to just handle every method."""
    try:

        cols1 = st.columns(2)

        cols1[1].markdown(""" 
                <div class="circle-image">
             <img src="https://th.bing.com/th?id=OSK.HEROocjiR_aWsPqAy8aUEsEhA9rA-6-pQaXH-d4uzWT36IA&w=472&h=280&c=1&rs=2&o=6&dpr=1.3&pid=SANGAM" alt="My Rectangular Image">
                     </div>            
                                <style>
                                  .circle-image {
                                      width: 500px;
                                      height: 300px;
                                      border-radius: 50%;
                                      overflow: hidden;
                                      box-shadow: 0 0 5px rgba(0, 0, 0, 0.3);
                                      
                                  }
    
                                  .circle-image img {
                                      width: 100%;
                                      height: 100%;
                                      object-fit: cover;
                                      
                                  }
                                  
                                </style>
                                                """, unsafe_allow_html=True)
        cols2 = st.columns(2)
        cols2[0].title("Course Generator")

        if "page" not in st.session_state or st.session_state.page == "login":
            login()
        elif st.session_state.page == "verification":
            emailVerification()
        elif st.session_state.page == "registration":
            register()
        elif st.session_state.page == "user":
            userPage()
        elif st.session_state.page == "forgetpass":
            fpp.forgetPass()
        elif st.session_state.page == "checkcode":
            ccp.checkCode()
        elif st.session_state.page == "resetpass":
            rpp.resetPass()
        elif st.session_state.page == "enterpass":
            ed.enterPass()
        elif st.session_state.page == "editpage":
            ed.editPage()
        elif st.session_state.page == "changeemail":
            ce.changeEmailPage()
        elif st.session_state.page == "emailver2":
            EV2.emailVerification()
        elif st.session_state.page == "returnhome":
            EV2.returntomain()
        elif st.session_state.page == "chngpass":
            ed.changePass()

    except Exception as e:
        logger.error(f"An error occurred: {e}")
        return None


if __name__ == "__main__":
    main()
