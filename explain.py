import logging
import re
from nltk.tokenize import word_tokenize
from langchain.schema import HumanMessage, SystemMessage
from model import llm


class Explain:
    def __init__(self):
        self.logger = logging.getLogger(__name__)

    # get slide partition
    def slide_Partition(self, slide: str):
        """this function helping to find where is title and where are points
        of this title ,and checking there are outliers to remove it."""
        try:
            if slide == '':
                return

            title = ""
            if slide.find("Title:"):
                start_index = slide.find("Title:") + len("Title:")
                end_index = slide.find("\n", start_index)

                title = slide[start_index - 1:end_index].strip()
            else:
                pattern = r'\d+:(.*?)\n'

                match = re.search(pattern, slide)

                if match:
                    title = match.group(1).strip()
            content = slide.split("\n")
            con = []
            for line in content:
                if line != '' and not line.startswith("(Note") \
                        and not line.startswith("Note") and line.startswith('-') \
                        and not line.__contains__("Conclusion") \
                        and not line.__contains__("Title"):
                    con.append(line)
            return title, con

        except Exception as e:
            self.logger.error(f"An error occurred: {e}")
            return None

    # get processed slides
    def get_slides(self, lst: list):
        """this function take list of slides` points and then give it to
        slide_partition to receive processed points and then map it again
         to its title."""
        try:
            dic = {}
            for topic in lst:
                for slide in topic.split('Slide'):
                    if slide == '':
                        continue
                    title, content = self.slide_Partition(slide)
                    if title == '' or title.startswith('Conclusion') or title.startswith('Q&A')\
                            or title.startswith("References") or title.startswith('Thank') \
                            or title.startswith("Questions"):
                        continue
                    elif title.startswith(":"):
                        title = title[1:]
                    if content:
                        dic[title] = content
            return dic

        except Exception as e:
            self.logger.error(f"An error occurred: {e}")
            return None

    def gen_explain(self, point: str):
        """this function receive each point to generate the explanation of
        it by using llm(gpt3.5) with specific prompt and tokens."""
        try:

            explainer = llm([
                SystemMessage(
                    content=f"""Your task is to explain the points in an engaging and attractive manner in just max 
                    sentence of 2 without using any welcoming language. Your explanation should be captivating and 
                    interesting, drawing the audience's attention and keeping them engaged throughout the 
                    explanation. Please ensure that your explanation is clear, concise, and presented in a compelling 
                    way that captures the audience's interest. Avoid using any form of welcome language at the 
                    beginning of your explanation. <!--start-example1-input--> Definition: Mindfulness meditation is 
                    a practice that involves bringing one's attention to the present moment. 
                    <!--end-example1-input--> <!--start-example1-output--> Mindfulness meditation is a form of 
                    meditation that focuses on cultivating awareness of the present moment. It involves paying 
                    attention to your thoughts and feelings without judgment and without being overly reactive. The 
                    goal is to develop a heightened sense of awareness and presence in the current moment. 
                    <!--end-example1-output--> <!--start-input--> text explanation. <!--end-input--> 
                    <!--start-output-->"""),
                HumanMessage(content=point)
            ])

            return explainer.content

        except Exception as e:
            self.logger.error(f"An error occurred: {e}")
            return None

    # get explained points
    def exp_points(self, lectures: dict):
        """this function just map each slide`s point to gen_explain to
        generate explanation of this point and then map it to title of
        this slide, and it ignores of references."""
        try:
            explained_points = {}
            final_explained_points = {}
            for lec_num, slides in lectures.items():
                for title, content in slides.items():
                    tmp_exp = []
                    if title.find("References") == -1:
                        for point in content:  # get each point
                            tmp_exp.append(self.gen_explain(point))
                    explained_points[title] = tmp_exp
                final_explained_points[lec_num] = explained_points
                explained_points = {}

            return final_explained_points

        except Exception as e:
            self.logger.error(f"An error occurred: {e}")
            return None

    # removing unwanted text
    def removed_unwanted(self, data: dict):
        """this function just remove unwanted words that will appear
        in slide presentation or just said by voice`s model,ex:
        today,conclusion,etc.... ."""
        try:
            cleared_data = {}
            final_cleared_data = {}
            for lec_num, exp in data.items():
                for title, content in exp.items():
                    tmp_d = []
                    for point in content:
                        if point == '':
                            continue
                        point = re.sub("Conclusion", '', point)
                        if word_tokenize(point)[0] == "Today":
                            point = " ".join(point.split('.'))[1:]
                        tmp_d.append(point)
                    cleared_data[title] = tmp_d
                final_cleared_data[lec_num] = cleared_data
                cleared_data = {}
            return final_cleared_data

        except Exception as e:
            self.logger.error(f"An error occurred: {e}")
            return None
