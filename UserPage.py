import streamlit as st
from coursegeneration import GenerateCourse
import DataBase as DB
import streamlit.components.v1 as components
from streamlit_option_menu import option_menu

generator = GenerateCourse()


def userPage():
    """
        Renders the main user interface for the course generation application in Streamlit.

        This function displays a user interface with the following features:
        - Logout button to clear session state and return to the login page.
        - Task selection dropdown to choose between 'UploadBook' and 'TypeCourse'.
        - Initializes session state variables based on the selected task.
        - Calls appropriate functions from the 'interact' module based on the selected task.

        Parameters:
        - None

        Returns:
        - None
        """

    col = st.columns(9)

    st.markdown(
        """
    <style>
    button {
        height: auto;
        padding-top: 10px !important;
        padding-bottom: 10px !important;
        padding-left: 5px !important;
        padding-right: 5px !important;
    }
    </style>
    """,
        unsafe_allow_html=True,
    )
    editcol = st.columns(9)
    if editcol[8].button("Profile 📋"):
        st.session_state.page = "enterpass"
        st.rerun()

    # check for showing video or presentation or both
    def show(selectedName=None, presSelectedName=None, videoDic=None, presDic=None):
        if selectedName:
            vidResults = videoDic[selectedName]
            st.video(vidResults)

        if presSelectedName:
            presResults = presDic[presSelectedName]
            components.iframe(
                presResults,
                height=1000)

    if col[8].button('Log Out ╰┈➤🚪'):
        st.session_state.clear()
        st.session_state.page = "login"
        st.rerun()

    task = option_menu(
        menu_title=None,
        options=["CourseGenerator", "UploadBook", "TypeCourse"],
        icons=["book-half", "cloud-arrow-up-fill", "pen"],
        orientation="horizontal",
    )
    # select box for videos and presentations
    st.session_state['video_names_list'] = []
    st.session_state['pres_names_list'] = []
    db = DB.Database()
    video_Dic = db.getVideos(st.session_state.id)
    pres_Dic = db.getPowerPoint(st.session_state.id)
    for p in video_Dic.keys():
        st.session_state['video_names_list'].append(p)

    for p in pres_Dic.keys():
        st.session_state['pres_names_list'].append(p)

    st.sidebar.subheader("Your Videos")
    selected_Names = st.sidebar.multiselect('Select Video:', st.session_state['video_names_list'])

    if st.sidebar.button("Delete selected video 🗑️") and selected_Names:
        for selected_Name in selected_Names:
            st.session_state['video_names_list'].remove(selected_Name)
            db.deleteVideo(st.session_state.id, selected_Name)
        st.rerun()

    if st.sidebar.button("Show selected video 📽️") and selected_Names:
        for selected_Name in selected_Names:
            show(selectedName=selected_Name, videoDic=video_Dic)
    st.sidebar.subheader("Your PowerPoints")
    pres_selected_Names = st.sidebar.multiselect('Select Presentation:', st.session_state['pres_names_list'])

    if st.sidebar.button("Delete selected PowerPoint 🗑️") and pres_selected_Names:
        for pres_selected_Name in pres_selected_Names:
            st.session_state.pres_names_list.remove(pres_selected_Name)
            db.deletePowerPoint(st.session_state.id, pres_selected_Name)
        st.rerun()

    if st.sidebar.button("Show selected PowerPoint 📽️") and pres_selected_Names:
        for pres_selected_Name in pres_selected_Names:
            show(presSelectedName=pres_selected_Name, presDic=pres_Dic)

    # Initialize session state variables
    if "video_path_ub" not in st.session_state or task == "TypeCourse":

        st.session_state.video_path_ub = None
        st.session_state['en_txt_ub'] = None
        st.session_state['en_slide_ub'] = None
        st.session_state['en_explain_ub'] = None
        st.session_state.audio_paths_ub = None
        st.session_state.conversation_ub = None
        st.session_state.chat_history_ub = None
        st.session_state["short_slides_ub"] = None

    if "video_path_tc" not in st.session_state or task == "UploadBook":

        st.session_state.video_path_tc = None
        st.session_state['en_txt_tc'] = None
        st.session_state['en_slide_tc'] = None
        st.session_state['en_explain_tc'] = None
        st.session_state.audio_paths_tc = None
        st.session_state.conversation_tc = None
        st.session_state.chat_history_tc = None
        st.session_state["short_slides"] = None
    # File uploader for the user to upload a dictionary file
    if task == "UploadBook":

        if "video_path_tc" in st.session_state:
            del [st.session_state.video_path_tc,
                 st.session_state['en_txt_tc'],
                 st.session_state['en_slide_tc'],
                 st.session_state['en_explain_tc'],
                 st.session_state.audio_paths_tc,
                 st.session_state.conversation_tc,
                 st.session_state.chat_history_tc,
                 st.session_state["short_slides"]]

        generator.upload_book_call()

    elif task == "TypeCourse":

        if "video_path_ub" in st.session_state:
            del [st.session_state.video_path_ub,
                 st.session_state['en_txt_ub'],
                 st.session_state['en_slide_ub'],
                 st.session_state['en_explain_ub'],
                 st.session_state.audio_paths_ub,
                 st.session_state.conversation_ub,
                 st.session_state.chat_history_ub,
                 st.session_state["short_slides_ub"]]

        generator.type_course_call()
