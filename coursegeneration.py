# import libraries
import logging
import pickle
from tqdm import tqdm
from genchat import GenerateChat
from genbook import GenerateBook
from explain import Explain
from quesans import QuesAns
from tts import generate_audio_chunks
from createvideo import run
from htmlHandling import css, bot_template, user_template
from PowerPoint import CreatePresentation
import CdnStorage
from GoogleDriveApi import GDApi
import streamlit.components.v1 as components
from DataBase import Database as DB
import streamlit as st
from pptx.dml.color import RGBColor
from PowerPoint import Font
import fitz
import re
import os


class ExtractChapters:
    def __init__(self, uploaded_file):
        self.uploadedFile = uploaded_file

    def save_uploaded_file(self):
        """
               Save the uploaded PDF file to a temporary directory.

               Returns:
                   str: The file path of the saved PDF file.

               This method saves the uploaded PDF file to the 'pdfs' directory.
               """
        try:
            # Save the uploaded file to a temporary directory
            if not os.path.exists("pdfs"):
                os.makedirs("pdfs")
            file_path = f"pdfs/{self.uploadedFile.name}"
            with open(file_path, "wb") as f:
                f.write(self.uploadedFile.getbuffer())
            # Return the file path
            return file_path
        except Exception as e:
            print(f"An error occurred while saving the file: {e}")
            return None

    @staticmethod
    def fix_errors(chapter_data):
        """
                Fix any errors in the chapter data, such as incorrect page ranges.

                Args:
                    chapter_data (list): List of dictionaries containing chapter information.

                Returns:
                    list: List of dictionaries with corrected chapter data.

                This method corrects errors in the page ranges of chapters.
                """
        fixed_data = []
        previous_end_page = 0
        for i, chapter in enumerate(chapter_data):
            title = chapter['title']
            start_page = chapter['start_page']
            end_page = chapter['end_page']

            if end_page < start_page:
                # If end page is less than start page, fix the end page
                end_page = start_page

            if start_page < previous_end_page:
                # If start page is less than previous chapter's end page, fix the start page
                start_page = previous_end_page + 1

            if end_page < start_page:
                # Ensure end page is not less than start page after adjustments
                end_page = start_page

            # Special case for the last chapter to ensure it doesn't extend to the end of the document
            if i == len(chapter_data) - 1:
                if end_page > chapter_data[-1]['end_page']:
                    end_page = chapter_data[-1]['end_page']

            # Update previous_end_page for the next iteration
            previous_end_page = end_page

            fixed_data.append({
                'title': title,
                'start_page': start_page,
                'end_page': end_page
            })

        return fixed_data

    @staticmethod
    def remove_unnecessary_chapters(chapters):
        """
               Remove unnecessary chapters based on predefined skip titles.

               Args:
                   chapters (list): List of dictionaries containing chapter information.

               Returns:
                   list: List of dictionaries with unnecessary chapters removed.

               This method removes chapters with titles that are deemed unnecessary.
               """
        skip_titles = [
            "COVER", "COPYRIGHT", "PACKT PAGE", "CONTRIBUTORS", "TITLE PAGE",
            "TABLE OF CONTENTS", "PREFACE", "OTHER BOOKS YOU MAY ENJOY", "INDEX",
            "REFERENCES", "ACKNOWLEDGEMENTS", "ACRONYMS", "ABOUT THE AUTHOR",
            "CONTENTS", "NOTES", "BIOGRAPHY", "BIBLIOGRAPHY", "APPENDIX", "GLOSSARY",
            "BACKGROUND", "PROLOGUE", "APPENDIX", "CREDITS", "ABOUT THE REVIEWERS",
            "WWW", "CUSTOMER", "PDF", "ACKNOWLEDGMENTS", "FRONT MATTER", "BACK MATTER",
            "FRONT-MATTER", "BACK-MATTER", "FRONTMATTER", "BACKMATTER",
            "Cover", "Copyright", "Packt Page", "Contributors", "Title Page",
            "Table of Contents", "Preface", "Other Books You May Enjoy", "Index",
            "References", "Acknowledgements", "Acronyms", "About the Author",
            "Contents", "Notes", "Biography", "Bibliography", "Appendix", "Glossary",
            "Background", "Prologue", "Appendix", "Credits", "About the Reviewers",
            "Www", "Customer", "Pdf", "Acknowledgments", "Front Matter", "Back Matter",
            "Front-Matter", "Back-Matter", "Frontmatter", "Backmatter",
            "cover", "copyright", "packt page", "contributors", "title page",
            "table of contents", "preface", "other books you may enjoy", "index",
            "references", "acknowledgements", "acronyms", "about the author",
            "contents", "notes", "biography", "bibliography", "appendix", "glossary",
            "background", "prologue", "appendix", "credits", "about the reviewers",
            "www", "customer", "pdf", "acknowledgments", "front matter", "back matter",
            "front-matter", "back-matter", "frontmatter", "backmatter", "Colophon", "about this book"
        ]

        cleaned_chapters = []
        seen_start_pages = set()

        for chapter in chapters:
            title = chapter['title']
            start_page = chapter['start_page']

            if not any(skip_title in title for skip_title in skip_titles) and start_page not in seen_start_pages:
                cleaned_chapters.append(chapter)
                seen_start_pages.add(start_page)

        return cleaned_chapters

    def get_toc_and_process(self, filePath):
        """
            Extracts the Table of Contents (TOC) from a PDF file and processes it to obtain chapter information.

            Args:
                filePath (str): The file path of the PDF document.

            Returns:
                list: A list of dictionaries containing chapter information, including title, start page, and end page.

            """
        # Open the PDF file
        pdf_document = fitz.open(filePath)

        # Extract the Table of Contents (TOC)
        toc = pdf_document.get_toc()

        # Initialize the list to hold chapters with their start and end pages
        chapters = []

        # Iterate through the TOC entries
        for i, entry in enumerate(toc):
            level, title, start_page = entry

            # Remove page numbers from titles
            title = re.sub(r'\d+$', '', title).strip()

            # Only consider main chapters (usually level 1)
            if level == 1:
                # Determine the end page
                if i + 1 < len(toc):
                    # Find the next main chapter's start page
                    for j in range(i + 1, len(toc)):
                        if toc[j][0] == 1:
                            end_page = toc[j][2] - 1
                            break
                    else:
                        # If no more main chapters, set end page to last page of document
                        end_page = pdf_document.page_count - 1
                else:
                    # If it is the last chapter, the end page is the last page of the document
                    end_page = pdf_document.page_count - 1

                # Append the chapter information to the list
                chapters.append({
                    'title': title,
                    'start_page': start_page,
                    'end_page': end_page
                })

        # Call fix_errors and remove_unnecessary_chapters within this function
        chapters = self.fix_errors(chapters)
        chapters = self.remove_unnecessary_chapters(chapters)

        return chapters


class GenerateCourse:
    def __init__(self):
        """
              Initializes the GenerateCourse class.

              This class provides methods for generating course content from books or user input.

              """
        self.logger = logging.getLogger(__name__)
        self.model_by_chat = GenerateChat()
        self.model_by_book = GenerateBook()
        self.explain = Explain()
        self.question_ans = QuesAns()
        self.createPresentation = CreatePresentation()
        self.db = DB()

        self.api_key = "531c7b1e-4273-4f19-ba0ae37b89a9-51e3-4932"
        self.storage_name = "grad5"
        self.storage_instance = CdnStorage.Storage(api_key=self.api_key, storage_zone=self.storage_name)
        self.gbapi = GDApi()

    # applying functions
    def apply_book_fuc(self, input_data: dict):
        """
        Applies book processing methods to generate slides and explanations.

        Args:
            input_data (dict): The input data containing book information.

        Returns:
            tuple: A tuple containing generated slides and explained slides.

        """
        try:
            slides = self.model_by_book.apply_Slide_Processing(input_data)
            slides_res = {}
            for i in range(len(slides)):
                slid_list = [slides[i]]
                final_slides = self.explain.get_slides(slid_list)
                slides_res[f"Lecture {i + 1}"] = final_slides
            short_slides = {}
            for lec, slides in slides_res.items():
                cnt = 0
                tmp_container = {}
                for title, content in slides.items():
                    tmp_container[title] = content
                    cnt += 1
                    if cnt == 2:
                        break
                short_slides[lec] = tmp_container
            st.session_state["short_slides_ub"] = short_slides
            explained_slides = self.explain.exp_points(short_slides)
            final_explained_slides = self.explain.removed_unwanted(explained_slides)

            return slides_res, final_explained_slides

        except Exception as e:
            self.logger.error(f"An error occurred: {e}")
            return None

    # apply slides and explanation
    def apply_chat_func(self, lectures):
        """
        Applies user-specific course processing methods.

        Args:
            lectures (list): A list of lectures.

        Returns:
            tuple: A tuple containing generated slides and explained slides.

        """
        try:
            slides = self.model_by_chat.apply_gen_slide_lec(lectures)
            slides_res = {}
            for i in range(len(slides)):
                final_slides = self.explain.get_slides(slides[i])
                slides_res[f"Lecture {i + 1}"] = final_slides
            short_slides = {}
            for lec, slides in slides_res.items():
                cnt = 0
                tmp_container = {}
                for title, content in slides.items():
                    tmp_container[title] = content
                    cnt += 1
                    if cnt == 2:
                        break
                short_slides[lec] = tmp_container
            st.session_state["short_slides"] = short_slides
            explained_slides = self.explain.exp_points(short_slides)
            final_explained_slides = self.explain.removed_unwanted(explained_slides)
            return slides_res, final_explained_slides

        except Exception as e:
            self.logger.error(f"An error occurred: {e}")
            return None

    # generate slides based on books
    @staticmethod
    def gen_details(slides: dict):
        """
               Generates details for slides.

               Args:
                   slides (dict): A dictionary containing slide information.

               Returns:
                   dict: A dictionary containing detailed slide information.

               """
        exp_slides: dict = {}
        final_exp_slides: dict = {}
        if "conv" not in st.session_state:
            with open(r"conversation.pkl", "rb") as file:
                st.session_state.conv = pickle.load(file)
            print("done")
        for lec, lec_slides in tqdm(slides.items()):
            for title, content in tqdm(lec_slides.items()):
                if title.startswith("Conclusion") or title.startswith("Q&A") or title.startswith("Thank") or \
                        title.startswith("Resour") or title.startswith("Refere") or title.startswith("Question") \
                        or title.startswith("Discuss"):
                    continue
                answers: str = ""
                for ques in content:
                    response = st.session_state.conv({'question': ques})
                    ans = response['answer']
                    if ans.startswith("Yes") or ans.startswith("No"):
                        answers += " ".join(ans.split(',')[1:]) + "\n"
                        continue
                    if not ans.startswith("Hello") and not ans.endswith("?") and not ans.startswith("I ") \
                            and not ans.startswith("I'm") and not ans.startswith("Sorry"):
                        answers += ans + "\n"

                    else:
                        answers += ques + "\n"
                if len(answers) > 20:
                    exp_slides[title] = answers
            del st.session_state.conv
            with open(r"conversation.pkl", "rb") as file:
                st.session_state.conv = pickle.load(file)
            final_exp_slides[lec] = exp_slides
            exp_slides = {}
        if "conv" in st.session_state:
            del st.session_state.conv
        return final_exp_slides

    @st.experimental_dialog("Error")
    def show_dialog(self, text):
        """
               Shows an error dialog.

               Args:
                   text (str): The error message to display.

               """
        st.error(text)

    def getNameAndLink(self, link):
        """
               Extracts the name and link from a given link.

               Args:
                   link (str): The link to extract information from.

               Returns:
                   tuple: A tuple containing the extracted name and link.

               """
        try:
            split_link = link.split('\\')
            lnk = split_link[-1]
            name = '\\'.join(split_link[:-1])
            return lnk, name

        except Exception as e:
            self.logger.error(f"An error occurred: {e}")
            return None

    # processing uploaded file
    def book_processes(self, data):
        """
        Processes uploaded files to generate course content.

        Args:
            data (dict): The data containing information about the uploaded file.

        Returns:
            tuple: A tuple containing text chunks, slides, and explained slides.

        """
        try:

            slides, explained_slides = self.apply_book_fuc(data)
            slides_txt = ""
            for _, slide in explained_slides.items():
                for title, content in slide.items():
                    slides_txt += f"{title}\n{content}\n"

            text_chunks_explained = self.question_ans.get_text_chunks(slides_txt)

            return text_chunks_explained, slides, \
                explained_slides

        except Exception as e:
            self.logger.error(f"An error occurred: {e}")
            return None

    # extracting course
    def type_processes(self, lectures):
        """
        Processes user input to generate course content.

        Args:
            lectures (list): A list of lectures.

        Returns:
            tuple: A tuple containing text chunks, slides, and explained slides.

        """
        try:
            # , explained_slides
            slides, explained_slides = self.apply_chat_func(lectures)

            slides_txt = ""
            for _, slide in slides.items():
                for title, content in slide.items():
                    slides_txt += f"{title}\n{content}\n"

            text_chunks_explained = self.question_ans.get_text_chunks(slides_txt)

            return text_chunks_explained, slides, \
                explained_slides

        except Exception as e:
            self.logger.error(f"An error occurred: {e}")
            return None

    # Function to handle user input and generate responses
    def handle_userinput(self, user_question: str, upload_bk):
        """
        Handles user input to retrieve answers.

        Args:
            user_question (str): The question asked by the user.
            upload_bk (bool): A boolean indicating if the question is uploaded with a book.

        """
        try:
            if upload_bk:
                response = st.session_state.conversation_ub({'question': user_question})
                st.session_state.chat_history_ub = response['chat_history']

                for i, message in enumerate(st.session_state.chat_history_ub):
                    if i % 2 == 0:
                        st.sidebar.write(user_template.replace(
                            "{{MSG}}", message.content), unsafe_allow_html=True)
                    else:
                        st.sidebar.write(bot_template.replace(
                            "{{MSG}}", message.content), unsafe_allow_html=True)
            else:
                response = st.session_state.conversation_tc({'question': user_question})
                st.session_state.chat_history_tc = response['chat_history']

                for i, message in enumerate(st.session_state.chat_history_tc):
                    if i % 2 == 0:
                        st.sidebar.write(user_template.replace(
                            "{{MSG}}", message.content), unsafe_allow_html=True)
                    else:
                        st.sidebar.write(bot_template.replace(
                            "{{MSG}}", message.content), unsafe_allow_html=True)
        except Exception as e:
            self.logger.error(f"An error occurred: {e}")
            return None

    # lecturer bot
    def question_answering(self, status=False):
        """
        Starts the lecturer bot.

        Args:
            status (bool): A boolean indicating if the bot is active.

        """
        try:
            # Chatbot
            st.sidebar.write(css, unsafe_allow_html=True)
            user_question = st.sidebar.text_input("Ask a question:")
            if user_question:
                self.handle_userinput(user_question, status)
            pass

        except Exception as e:
            self.logger.error(f"An error occurred: {e}")
            return None

    # call functions to generate course by book
    def upload_book_call(self):
        """
        Initiates the process for generating course content from uploaded books.
        """

        with st.spinner("uploading..."):
            uploaded_file = st.file_uploader("Upload your book", type=["pdf"])
            file_name = uploaded_file.name.split('.')[0].replace(" ", "_")

            extractChap = ExtractChapters(uploaded_file)
            pathFile = extractChap.save_uploaded_file()
            # Try get_chapters method first
            chapters = extractChap.get_toc_and_process(pathFile)

            selected_chapters = []
            if chapters:
                # get keys
                chapterTitle = []
                for data in chapters:
                    chapterTitle.append(data['title'])

                selected_chapters = st.multiselect("Select chapters", chapterTitle)

            if not chapters:
                self.show_dialog("Book is needed to have hyperlinks of chapters or book has wrong hyperlinks.")

        generate = st.button("Generate")
        if generate and chapters:
            chapterStartEnd = {}
            data = {}

            if selected_chapters:
                for chapter in chapters:
                    if chapter['title'] in selected_chapters:
                        chapterStartEnd[chapter['title']] = [chapter['start_page'], chapter['end_page']]

                for title, Range in chapterStartEnd.items():

                    start = Range[0] - 1
                    end = Range[1]
                    text = ""
                    with fitz.open(pathFile) as doc:
                        for page in doc.pages(start, end):
                            text += page.get_text()
                    data[title] = text
            with st.spinner("generate slides and explanation..."):
                st.session_state['en_txt_ub'], en_slides_ub, st.session_state[
                    'en_explain_ub'] = self.book_processes(
                    data=data)
                exp_ub = GenerateCourse.gen_details(en_slides_ub)
                final_exp_ub = {}
                for lec, slides in exp_ub.items():
                    slide_exp_ub = self.model_by_book.apply_Slide_Processing(slides)
                    final_slide_exp_ub = self.explain.get_slides(slide_exp_ub)
                    final_exp_ub[lec] = final_slide_exp_ub
                st.session_state['en_slide_ub'] = final_exp_ub

            with st.spinner("initial vectorstore..."):
                vector_store = self.question_ans.get_vectorstore(st.session_state["en_txt_ub"])
                # create conversation chain with the OpenAI API key
                st.session_state.conversation_ub = self.question_ans.get_conversation_chain(
                    vector_store)

            with st.spinner("generate audio..."):
                audio_paths = {}
                for lec, slides in st.session_state['en_explain_ub'].items():
                    audio_paths[lec] = generate_audio_chunks(slides)
                st.session_state.audio_paths_ub = audio_paths
            with st.spinner("create video..."):
                st.session_state.video_path_ub = run(
                    st.session_state['short_slides_ub'],
                    st.session_state.audio_paths_ub,
                    name=file_name
                )
        if st.session_state.video_path_ub:

            if "pres_link_ub" not in st.session_state:
                st.session_state.pres_link_ub = ""
            # Ensure the "images" directory exists
            os.makedirs("images", exist_ok=True)
            optimizedPres = {}
            for lec, lec_content in st.session_state['en_slide_ub'].items():
                data = {}
                for title, content in lec_content.items():
                    title = title.replace("?", "").replace("*", "")
                    tmp_text = []
                    for text in content:
                        nResult = '•' + text[1:]
                        tmp_text.append(nResult)
                    data[title] = tmp_text
                optimizedPres[lec] = data
            template_backgrounds = {
                "Default": "default.png",
                "Dark": "dark.png",
                "Fancy": "Fancy.png",
                "History": "history.png",
                "Modern": "modern.jpg",
                "White": "white.png",
            }

            template_options = list(template_backgrounds.keys())
            template = st.selectbox("Choose a template", options=template_options)

            if template != "Default" and template in template_backgrounds:
                st.subheader("Background Image Preview")
                if template_backgrounds[template] is not None:
                    st.image(template_backgrounds[template], caption=f"Template: {template}", use_column_width=True)
                else:
                    st.write(f"No background image found for template: {template}")

            background_image_path = None
            if template == "Default":
                background_image = st.file_uploader("Upload Background Image (PNG or JPG)",
                                                    type=["png", "jpg", "jfif"])
                if background_image is not None:
                    background_image_path = f"uploaded_image.{background_image.type.split('/')[1]}"
                    with open(background_image_path, "wb") as f:
                        f.write(background_image.read())
                    st.subheader("Uploaded Background Image Preview")
                    st.image(background_image, caption="Uploaded Background Image", use_column_width=True)
            else:
                background_image_path = template_backgrounds.get(template)

            title_font_size = st.slider("Title Font Size", min_value=20, max_value=30, value=20)
            content_font_size = st.slider("Content Font Size", min_value=15, max_value=22, value=18)

            font_options = ["Arial", "Calibri", "Times New Roman", "Verdana", "Courier New", "Georgia", "Tahoma",
                            "Comic Sans MS",
                            "Impact", "Trebuchet MS"]
            font_name = st.selectbox("Choose Font preview", options=font_options)

            preview_image = Font.generate_font_preview(font_name, content_font_size)
            st.image(preview_image, caption=f"Font Preview - {font_name}", use_column_width=True)

            title_color_str = st.color_picker("Choose Title Color", "#000000")
            content_color_str = st.color_picker("Choose Content Color", "#000000")

            title_color = RGBColor(*tuple(int(title_color_str[i:i + 2], 16) for i in (1, 3, 5)))
            content_color = RGBColor(*tuple(int(content_color_str[i:i + 2], 16) for i in (1, 3, 5)))
            if st.button("Create Presentation"):

                self.createPresentation.create_presentation(optimizedPres, title_font_size, content_font_size,
                                                            title_color, content_color, font_name,
                                                            background_image_path, file_name)

                link = st.session_state.video_path_ub
                lnk, name1 = self.getNameAndLink(link)
                extension = lnk[-3:]
                path = f"<videos>/<{st.session_state.file_name}>.{extension}"
                self.storage_instance.PutFile(file_name=st.session_state.file_path, storage_path=path,
                                              local_upload_file_path=name1)
                cdn_link = f'https://{self.storage_name}.b-cdn.net/videos/' + \
                           st.session_state.file_name + '.' + extension

                self.db.insertVideo(st.session_state.id, st.session_state.file_name, cdn_link)

                if os.path.exists(st.session_state.file_path):
                    st.session_state.pres_link_ub = self.gbapi.upload(file_path=st.session_state.file_path)
                pres_name = "presentation_" + st.session_state.file_name
                self.db.insertPowerPoint(st.session_state.id, pres_name, st.session_state.pres_link_ub)
                st.rerun()

            if st.session_state.pres_link_ub:
                st.subheader("Created Video")
                st.video(st.session_state.video_path_ub)
                st.subheader("Created PowerPoint")
                components.iframe(
                    st.session_state.pres_link_ub,
                    height=1000)

        if st.session_state.conversation_ub:
            st.sidebar.subheader("Lecturer")
            self.question_answering(status=True)

    # call functions to generate course by chat
    def type_course_call(self):
        """
                Initiates the process for generating course content based on user input.

        """

        course_name = st.text_input("Enter course name:")

        lec_num = st.number_input("Enter number of lectures:",
                                  min_value=1,
                                  max_value=5)

        if "lectures" not in st.session_state:
            st.session_state.lectures = None
        generate = st.button("Generate Lectures")
        if generate and course_name != "":
            st.session_state.lectures = self.model_by_chat.gen_lectures(lec_num=lec_num, course_name=course_name)
            st.rerun()
        if st.session_state.lectures:
            # let user edit topics
            for idx, (lec, titles) in enumerate(st.session_state.lectures.items()):
                text = "\n".join(titles)
                st.text_area(label=f"Lecture {idx + 1}", value=text, height=150, key=f"{lec}")
            for lec, _ in st.session_state.lectures.items():
                st.session_state.lectures[lec] = st.session_state[f"{lec}"].split("\n")
        edited = st.button("Generate Course")
        if edited and st.session_state.lectures:
            with st.spinner("generate slides and explanation..."):
                st.session_state['en_txt_tc'], en_slides_tc, st.session_state[
                    'en_explain_tc'] = self.type_processes(lectures=st.session_state.lectures)

                exp_tc = GenerateCourse.gen_details(en_slides_tc)

                final_exp_tc = {}
                for lec, slides in tqdm(exp_tc.items()):
                    slide_exp_tc = self.model_by_book.apply_Slide_Processing(slides)
                    final_exp_tc[lec] = self.explain.get_slides(slide_exp_tc)

                st.session_state['en_slide_tc'] = final_exp_tc

            with st.spinner("initial vectorstore..."):
                vector_store = self.question_ans.get_vectorstore(st.session_state["en_txt_tc"])
                # create conversation chain with the OpenAI API key
                st.session_state.conversation_tc = self.question_ans.get_conversation_chain(
                    vector_store)

            with st.spinner("generate audio..."):
                audio_paths = {}
                for lec, slides in st.session_state['en_explain_tc'].items():
                    audio_paths[lec] = generate_audio_chunks(slides)
                st.session_state.audio_paths_tc = audio_paths

            with st.spinner("create video..."):
                st.session_state.video_path_tc = run(
                    st.session_state['short_slides'],
                    st.session_state.audio_paths_tc,
                    name=course_name
                )
        if st.session_state.video_path_tc:

            if "pres_link_tc" not in st.session_state:
                st.session_state.pres_link_tc = ""
            # Ensure the "images" directory exists
            os.makedirs("images", exist_ok=True)
            optimizedPres = {}
            for lec, lec_content in st.session_state['en_slide_tc'].items():
                data = {}
                for title, content in lec_content.items():
                    title = title.replace("?", "").replace("*", "")
                    tmp_text = []
                    for text in content:
                        nResult = '•' + text[1:]
                        tmp_text.append(nResult)
                    data[title] = tmp_text
                optimizedPres[lec] = data
            template_backgrounds = {
                "Default": "default.png",
                "Dark": "dark.png",
                "Fancy": "Fancy.png",
                "History": "history.png",
                "Modern": "modern.jpg",
                "White": "white.png",
            }

            template_options = list(template_backgrounds.keys())
            template = st.selectbox("Choose a template", options=template_options)

            if template != "Default" and template in template_backgrounds:
                st.subheader("Background Image Preview")
                if template_backgrounds[template] is not None:
                    st.image(template_backgrounds[template], caption=f"Template: {template}", use_column_width=True)
                else:
                    st.write(f"No background image found for template: {template}")

            background_image_path = None
            if template == "Default":
                background_image = st.file_uploader("Upload Background Image (PNG or JPG)",
                                                    type=["png", "jpg", "jfif"])
                if background_image is not None:
                    background_image_path = f"uploaded_image.{background_image.type.split('/')[1]}"
                    with open(background_image_path, "wb") as f:
                        f.write(background_image.read())
                    st.subheader("Uploaded Background Image Preview")
                    st.image(background_image, caption="Uploaded Background Image", use_column_width=True)
            else:
                background_image_path = template_backgrounds.get(template)

            title_font_size = st.slider("Title Font Size", min_value=20, max_value=30, value=20)
            content_font_size = st.slider("Content Font Size", min_value=15, max_value=22, value=18)

            font_options = ["Arial", "Calibri", "Times New Roman", "Verdana", "Courier New", "Georgia", "Tahoma",
                            "Comic Sans MS",
                            "Impact", "Trebuchet MS"]
            font_name = st.selectbox("Choose Font preview", options=font_options)

            preview_image = Font.generate_font_preview(font_name, content_font_size)
            st.image(preview_image, caption=f"Font Preview - {font_name}", use_column_width=True)

            title_color_str = st.color_picker("Choose Title Color", "#000000")
            content_color_str = st.color_picker("Choose Content Color", "#000000")

            title_color = RGBColor(*tuple(int(title_color_str[i:i + 2], 16) for i in (1, 3, 5)))
            content_color = RGBColor(*tuple(int(content_color_str[i:i + 2], 16) for i in (1, 3, 5)))

            if st.button("Create Presentation"):
                name = course_name.replace(" ", "_")

                self.createPresentation.create_presentation(optimizedPres, title_font_size, content_font_size,
                                                            title_color, content_color, font_name,
                                                            background_image_path,
                                                            name)
                link = st.session_state.video_path_tc
                lnk, name1 = self.getNameAndLink(link)
                extension = lnk[-3:]
                path = f"<videos>/<{st.session_state.file_name}>.{extension}"
                self.storage_instance.PutFile(file_name=st.session_state.file_path, storage_path=path,
                                              local_upload_file_path=name1)
                cdn_link = f'https://{self.storage_name}.b-cdn.net/videos/' + \
                           st.session_state.file_name + '.' + extension

                self.db.insertVideo(st.session_state.id, st.session_state.file_name, cdn_link)

                if os.path.exists(st.session_state.file_path):
                    st.session_state.pres_link_tc = self.gbapi.upload(
                        file_path=st.session_state.file_path)
                pres_name = "presentation_" + st.session_state.file_name
                self.db.insertPowerPoint(st.session_state.id, pres_name, st.session_state.pres_link_tc)
                st.rerun()

            if st.session_state.pres_link_tc:
                st.subheader("Created Video")
                st.video(st.session_state.video_path_tc)
                st.subheader("Created PowerPoint")
                components.iframe(
                    st.session_state.pres_link_tc,
                    height=1000)

        if st.session_state.conversation_tc:
            st.sidebar.title("Lecturer")
            self.question_answering()
