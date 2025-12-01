import logging
from langchain.schema import HumanMessage, SystemMessage
from model import llm


class GenerateBook:
    def __init__(self):
        self.logger = logging.getLogger(__name__)

    # generating slide
    def gen_slide(self, text: str, title: str):
        """this function generate slides of book`s title by using
        llm(gpt3.5) by just passing book`s title and content of this
        title."""
        try:

            slides = llm(
                [
                    SystemMessage(
                        content=f"""Create a series of slides (pptx) based on the topic of chapter: {title}. Each 
                        slide should have a unique title and multi points that are derived from the provided text. Ensure 
                        that the presentation points are diverse and well-organized to effectively communicate the 
                        key aspects of the topic. The slides should be informative, engaging, and visually appealing, 
                        with each slide offering distinct and relevant information. Please aim to create a 
                        comprehensive presentation that effectively captures the essence of the topic and presents it 
                        in an engaging and easily understandable format. <!--start-example1-input--> Mindfulness 
                        meditation is a practice that has gained widespread popularity due to its numerous benefits 
                        for mental, emotional, and physical well-being. Rooted in ancient contemplative traditions, 
                        mindfulness meditation involves paying attention to the present moment with non-judgmental 
                        awareness. Here are some of the key benefits associated with mindfulness meditation:  Stress 
                        Reduction: One of the primary benefits of mindfulness meditation is its ability to reduce 
                        stress. By focusing on the present moment and cultivating a non-judgmental awareness, 
                        individuals can break the cycle of constant worry about the future or rumination about the 
                        past, leading to a reduction in stress levels.  Improved Mental Health: Mindfulness 
                        meditation has been shown to be effective in managing various mental health conditions, 
                        including anxiety, depression, and post-traumatic stress disorder (PTSD). Regular practice 
                        can help individuals develop a healthier relationship with their thoughts and emotions, 
                        promoting emotional regulation and resilience.  Enhanced Focus and Concentration: Mindfulness 
                        meditation involves training the mind to stay focused on a specific point of attention, 
                        such as the breath or bodily sensations. This practice has been linked to improvements in 
                        cognitive functions, including enhanced concentration, attention, and memory.  Better 
                        Emotional Regulation: Mindfulness encourages individuals to observe their thoughts and 
                        emotions without getting caught up in them. This non-reactive awareness fosters emotional 
                        regulation, helping individuals respond to challenging situations with greater calmness and 
                        objectivity. Increased Self-Awareness: Mindfulness meditation promotes self-awareness by 
                        encouraging individuals to observe their thoughts and behaviors without judgment. This 
                        heightened self-awareness can lead to a deeper understanding of oneself, one's values, 
                        and the motivations behind actions.  Improved Sleep Quality: Regular mindfulness practice has 
                        been associated with improved sleep quality. By calming the mind and reducing stress, 
                        individuals may find it easier to relax and achieve a restful night's sleep.  Enhanced 
                        Well-Being: Mindfulness meditation is linked to an overall sense of well-being. Practitioners 
                        often report greater life satisfaction, happiness, and a more positive outlook on life as a 
                        result of incorporating mindfulness into their daily routines.  Physical Health Benefits: 
                        Mindfulness meditation has been associated with various physical health benefits, 
                        including lower blood pressure, improved immune function, and reduced inflammation. The 
                        mind-body connection cultivated through mindfulness may contribute to these positive effects 
                        on physical health.  Greater Resilience: Mindfulness meditation helps individuals develop 
                        resilience by fostering an acceptance of life's inevitable challenges and uncertainties. This 
                        adaptive mindset can contribute to a more balanced and resilient approach to facing 
                        difficulties.  Enhanced Relationships: Mindfulness can improve interpersonal relationships by 
                        promoting active listening, empathy, and non-reactive communication. Being fully present in 
                        interactions fosters deeper connections with others. <!--end-example1-input--> 
                        <!--start-example1-output--> Title: The Benefits of Mindfulness Meditation  Slide 1: 
                        Introduction Definition: Mindfulness meditation is a practice that involves bringing one's 
                        attention to the present moment. Origin: Rooted in ancient Eastern traditions, it has gained 
                        popularity in the Western world for its numerous benefits. Slide 2: Reduced Stress  
                        Mindfulness meditation has been proven to reduce stress levels. Techniques, such as deep 
                        breathing and focused attention, help calm the nervous system. Slide 3: Improved Focus and 
                        Concentration  Regular practice enhances cognitive abilities. Studies show that mindfulness 
                        improves attention span and concentration. Slide 4: Emotional Well-being  Mindfulness helps 
                        regulate emotions. Individuals practicing mindfulness often report increased levels of 
                        happiness and overall well-being. Slide 5: Enhanced Self-Awareness  The practice encourages 
                        self-reflection and awareness of one's thoughts and feelings. Increased self-awareness leads 
                        to better decision-making and personal growth. Slide 6: Better Sleep  Mindfulness has been 
                        linked to improved sleep quality. Techniques like mindful breathing can help alleviate 
                        insomnia and promote restful sleep. Slide 7: Physical Health Benefits  Mindfulness is 
                        associated with various physical health benefits. Studies suggest it can lower blood 
                        pressure, boost the immune system, and reduce inflammation. Slide 8: Workplace Benefits  Many 
                        organizations are incorporating mindfulness programs for employees. Increased productivity, 
                        reduced absenteeism, and improved workplace satisfaction are reported outcomes. Slide 9: 
                        Getting Started with Mindfulness  Provide resources and tips for beginners. Mention apps, 
                        guided meditations, and simple exercises to incorporate mindfulness into daily life. Slide 
                        10: Conclusion  Summarize the key benefits of mindfulness meditation. Encourage the audience 
                        to explore and incorporate mindfulness into their lives. <!--end-example1-output--> 
                        <!--start-input--> slide generation <!--end-input--> <!--start-output-->"""),
                    HumanMessage(content=text)
                ])

            return slides.content

        except Exception as e:
            self.logger.error(f"An error occurred: {e}")
            return None

    # get slides
    def apply_Slide_Processing(self, data: dict):
        """this function just apply remove repeated at input data and then passing it to gen_slide function to generate slide,
        then return these slides"""
        try:
            # data = self.remove_Repeated(data)
            data1 = data.copy()
            lst = []
            for key, value in data1.items():
                if len(value.split()) <= 10_000:
                    points = self.gen_slide(value, key)
                    lst.append(points)
                else:
                    len_v = len(value.split())
                    i = 0
                    points = ""
                    while len_v:
                        points += self.gen_slide(value[10_000 * i:10_000 * (i + 1)], key)
                        len_v -= 10_000
                        i += 1
                    lst.append(points)

            return lst

        except Exception as e:
            print(f"An error occurred: {e}")
            return None
