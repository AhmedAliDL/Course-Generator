import wave
import contextlib
from typing import List, Union
from PIL import Image, ImageDraw, ImageFont
import cv2
import numpy as np
from moviepy.editor import AudioFileClip
from pydub import AudioSegment
from moviepy.editor import concatenate_videoclips
from subtitle import *


class CreateImage:
    @staticmethod
    def create_blank_slide_image(width, height, background_color=(255, 255, 255)):
        """
        Create a blank slide image with the specified width, height, and background color.

        Parameters:
        - width (int): The width of the slide image.
        - height (int): The height of the slide image.
        - background_color (tuple): The background color of the slide image in RGB format. Default is white.

        Returns:
        - Image: The blank slide image.
        """
        # Create a new blank image with the specified width, height, and background color
        slide_image = Image.new("RGB", (width, height), background_color)
        return slide_image

    @staticmethod
    def add_title(image, title_text, max_width, max_height, font_color=(0, 0, 0)):
        """
        Add a title to the slide image with dynamically adjusted font size to fit within the specified dimensions.

        Parameters:
        - image (Image): The image to add the title to.
        - title_text (str): The text of the title.
        - max_width (int): The maximum width available for the title.
        - max_height (int): The maximum height available for the title.
        - font_color (tuple): The font color of the title text in RGB format. Default is black.
        """
        # Initialize font size
        font_size = 70

        # Load a font
        font = ImageFont.truetype("Arial.ttf", font_size)

        # Create a drawing context
        draw = ImageDraw.Draw(image)

        # Get the bounding box of the text
        text_bbox = draw.textbbox((0, 0), title_text, font=font)

        # Calculate the width and height of the text
        text_width = text_bbox[2] - text_bbox[0]
        text_height = text_bbox[3] - text_bbox[1]

        # Decrease font size until it fits within the available space
        while text_width > max_width or text_height > max_height:
            font_size -= 1
            font = ImageFont.truetype("Arial.ttf", font_size)
            text_bbox = draw.textbbox((0, 0), title_text, font=font)
            text_width = text_bbox[2] - text_bbox[0]
            text_height = text_bbox[3] - text_bbox[1]

        # Calculate the position to center the title text
        x = (max_width - text_width) / 2
        y = (max_height - text_height) / 2

        # Draw the title text on the image with enhanced font size and color
        draw.text((x, y), title_text, font=font, fill=font_color)

    @staticmethod
    def split_text_into_lines(text, max_width, font, draw):
        """
        Split the text into multiple lines so that no word is split across two lines.

        Parameters:
        - text (str): The text to split.
        - max_width (int): The maximum width for each line.
        - font (ImageFont): The font used for the text.
        - draw (ImageDraw): The drawing context.

        Returns:
        - list: A list of strings, where each string represents a line of text.
        """
        lines = []
        words = text.split()
        current_line = ""
        for word in words:
            if draw.textbbox((0, 0), current_line + " " + word, font=font)[2] <= max_width:
                current_line += " " + word if current_line else word
            else:
                lines.append(current_line.strip())
                current_line = word
        if current_line:
            lines.append(current_line.strip())
        return lines

    @staticmethod
    def add_content(image, content_lines, max_width, max_height, font_size=35, font_color=(0, 0, 0)):
        """
        Add content to the slide image where each line begins with a bullet point and there is space between the lines.

        Parameters:
        - image (Image): The image to add the content to.
        - content_lines (list): A list of strings, where each string represents a line of content.
        - max_width (int): The maximum width available for the content.
        - max_height (int): The maximum height available for the content.
        - font_size (int): The initial font size of the content text. Default is 24.
        - font_color (tuple): The font color of the content text in RGB format. Default is black.
        """
        # Load a font
        font = ImageFont.truetype("Arial.ttf", font_size)

        # Create a drawing context
        draw = ImageDraw.Draw(image)

        # Initialize x-coordinate for drawing the content
        x = (image.width - max_width) / 2

        # Calculate the height of the title text to start content right after it
        title_height = draw.textbbox((0, 0), content_lines[0], font=font)[3] - \
                       draw.textbbox((0, 0), content_lines[0], font=font)[1]

        # Initialize y-coordinate for drawing the content
        y = (image.height + max_height - title_height) / 7  # Adjusted to slightly below the title

        # Adjust the starting y-coordinate to ensure the content fits within the specified maximum height
        total_text_height = sum(
            draw.textbbox((0, 0), line, font=font)[3] - draw.textbbox((0, 0), line, font=font)[1] for line in
            content_lines)
        if total_text_height > max_height:
            y -= (total_text_height - max_height) / 2

        # Set indent for content lines
        indent = 40

        # Iterate through each line of content
        for line in content_lines:
            # Add bullet point to the beginning of the line
            line_with_bullet = line

            # Split the line into multiple lines to avoid word splitting
            split_lines = CreateImage.split_text_into_lines(line_with_bullet, max_width - indent, font, draw)

            # Draw each line with adjusted font size, color, and indent for content
            for split_line in split_lines:
                # Adjust font size dynamically based on available space
                current_font_size = font_size
                while draw.textbbox((0, 0), split_line, font=font)[2] - draw.textbbox((0, 0), split_line, font=font)[
                    0] > max_width:
                    current_font_size -= 1
                    font = ImageFont.truetype("Arial.ttf", current_font_size)

                # Calculate the remaining space available
                remaining_space = max_height - (y + draw.textbbox((0, 0), split_line, font=font)[3] -
                                                draw.textbbox((0, 0), split_line, font=font)[1])

                # Stop adding lines if there is not enough space left
                if remaining_space < (
                        draw.textbbox((0, 0), split_line, font=font)[3] - draw.textbbox((0, 0), split_line, font=font)[
                    1]) * len(split_lines):
                    print("Reached the end of the image.")
                    return

                draw.text((x + indent, y), split_line, font=font, fill=font_color)

                # Move to the next line with space
                y += draw.textbbox((0, 0), split_line, font=font)[3] - draw.textbbox((0, 0), split_line, font=font)[1]
                y += 15  # Add space between lines

    @staticmethod
    def create_slides(slide_map: dict):
        """
        Create slides for each element in the slide_map.

        Parameters:
        - slide_map (dict): A dictionary mapping titles to their corresponding content.

        Returns:
        - list: A list of PIL Image objects representing the slides.
        """
        # Specify the width and height of the slide image
        width = 1024
        height = 768
        slides = []

        # Iterate over each element in the slide_map
        for title_text, content_lines in slide_map.items():
            # Specify the maximum dimensions available for the title and content
            max_title_width = width - 20
            max_title_height = height // 4  # Assuming 1/4 of the height for the title
            max_content_width = width - 20
            max_content_height = height // 1.2  # Assuming 1/1.2 of the height for the content

            # Create a blank slide image
            slide_image = CreateImage.create_blank_slide_image(width, height)

            # Add a title to the slide image with educational style
            CreateImage.add_title(slide_image, title_text, max_title_width, max_title_height,
                                  font_color=(30, 144, 255))  # Use a different color for title

            # Add content to the slide image with educational style
            CreateImage.add_content(slide_image, content_lines, max_content_width, max_content_height)

            # Append the slide image to the list
            slides.append(slide_image)

        return slides


class CreateVideo:
    @staticmethod
    def images_to_videos(image_list, audio_durations: list, output_dir="video"):
        """
        Create videos from a list of PIL images, with each image displayed for a duration
        corresponding to the provided audio durations. Each image will have its own video.

        Args:
            image_list (list): List of PIL images.
            audio_durations (list): List of audio durations in seconds corresponding to each image.
            output_dir (str): Directory to save the generated videos.

        Returns:
            list: List of video paths.
        """
        videos_paths = []
        try:
            # Create the output directory if it doesn't exist
            os.makedirs(output_dir, exist_ok=True)

            # Iterate over images in the list
            for idx, img in enumerate(image_list):
                duration = audio_durations[idx]
                num_frames = int(duration)  # Number of frames based on audio duration

                # Convert PIL image to numpy array
                img_np = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)

                # Create video path
                video_path = os.path.join(output_dir, f"video_{idx}.mp4")
                videos_paths.append(video_path)

                # Create video writer
                fourcc = cv2.VideoWriter_fourcc(*'mp4v')
                out = cv2.VideoWriter(video_path, fourcc, 30, (img_np.shape[1], img_np.shape[0]))

                # Write frames to video
                for _ in range(num_frames):
                    out.write(img_np)

                # Release video writer
                out.release()

        except Exception as e:
            print(f"Error occurred: {e}")

        return videos_paths

    @staticmethod
    def combine_videos_with_audios(video_files, audio_files, output_dir):
        """
        Combine video files with corresponding audio files and save the resulting videos with audio.

        Args:
            video_files (list): List of paths to input video files.
            audio_files (list): List of paths to input audio files.
            output_dir (str): Path to the directory where the combined videos will be saved.

        Returns:
            list: List of paths to the combined videos.
        """
        combined_video_paths = []
        try:
            # Ensure the output directory exists; if not, create it
            if not os.path.exists(output_dir):
                os.makedirs(output_dir)

            # Iterate over the video and audio files
            for video_path, audio_path in zip(video_files, audio_files):
                try:
                    # Load the video file
                    video_clip = VideoFileClip(video_path)

                    # Load the audio file
                    audio_clip = AudioFileClip(audio_path)

                    # Set the audio of the video to the loaded audio clip
                    video_clip_with_audio = video_clip.set_audio(audio_clip)

                    # Define the output file path
                    output_file = os.path.join(output_dir,
                                               f"{os.path.splitext(os.path.basename(video_path))[0]}_with_audio.mp4")

                    # Write the video file with the new audio
                    video_clip_with_audio.write_videofile(output_file, codec="libx264", audio_codec="aac", threads=4)

                    combined_video_paths.append(output_file)
                    print(f"Combined {video_path} with {audio_path} successfully.")
                except Exception as e:
                    print(f"Error combining {video_path} with {audio_path}: {e}")
                finally:
                    # Close the clips to release resources
                    if 'video_clip' in locals():
                        video_clip.close()
                    if 'audio_clip' in locals():
                        audio_clip.close()
        except Exception as e:
            print(f"An error occurred: {e}")

        return combined_video_paths

    @staticmethod
    def concatenate_videos(video_list, output_file):
        clips = [VideoFileClip(video) for video in video_list]
        final_clip = concatenate_videoclips(clips)
        final_clip.write_videofile(output_file, codec='libx264')

    @staticmethod
    def calculate_audio_durations(audio_list: List[str]) -> List[Union[float, None]]:
        """
        Calculate the durations of audio files.

        Args:
            audio_list (List[str]): List of audio file paths.

        Returns:
            List[Union[float, None]]: List of audio durations in seconds. None for files with errors.
        """
        durations = []
        for audio in audio_list:
            try:
                with contextlib.closing(wave.open(audio, 'r')) as f:
                    frames = f.getnframes()
                    rate = f.getframerate()
                    duration = frames / float(rate)
                    durations.append(duration)
            except Exception as e:
                print(f"Error processing {audio}: {e}")
                durations.append(None)  # Append None for files with errors
        return durations

    @staticmethod
    def merge_audio(audio_paths):
        merged_audio = AudioSegment.empty()
        for path in audio_paths:
            audio = AudioSegment.from_wav(path)
            merged_audio += audio
        return merged_audio

    @staticmethod
    def merge_all_audio(dictionary):
        merged_paths = []
        for title, paths in dictionary.items():
            title = title.replace("?", "")
            merged_audio = CreateVideo.merge_audio(paths)
            merged_path = f"audio/{title}_merged.wav"
            merged_audio.export(merged_path, format="wav")
            merged_paths.append(merged_path)
        return merged_paths

    @staticmethod
    def create_starting_slide_image(text, image_size=(800, 600), font_size=36):
        """
        Create a plank slide image with text in the middle.

        Parameters:
        - text (str): The text to display on the plank slide.
        - image_size (tuple): The size of the plank slide image (width, height).
        - font_size (int): The font size of the text.

        Returns:
        - Image: The starting slide image.
        """
        # Create a blank image with a plank-like background color
        starting_slide_image = Image.new("RGB", image_size, (255, 255, 255))

        # Load a font
        font = ImageFont.truetype("arial.ttf", font_size)

        # Create a drawing context
        draw = ImageDraw.Draw(starting_slide_image)

        # Calculate text size and position
        text_bbox = draw.textbbox((0, 0), text, font=font)
        text_width = text_bbox[2] - text_bbox[0]
        text_height = text_bbox[3] - text_bbox[1]
        text_x = (image_size[0] - text_width) // 2
        text_y = (image_size[1] - text_height) // 2

        # Draw the text on the image
        draw.text((text_x, text_y), text, fill=(0, 0, 0), font=font)

        return starting_slide_image


def run(slide_map: dict, audios_map: dict, name: str):
    """
        Generates and concatenates videos for a series of lectures based on slide and audio data.

        Args:
            slide_map (dict): A dictionary mapping lecture numbers to their corresponding slide content.
            audios_map (dict): A dictionary mapping lecture numbers to lists of audio paths.
            name (str): The name of the video series.

        Returns:
            str: The file path of the final concatenated video.


        """
    paths: list = []
    idx = 1
    for lec_num, _ in slide_map.items():
        start_im = CreateVideo.create_starting_slide_image(f'Lecture {idx}')
        idx += 1
        start_vid = CreateVideo.images_to_videos([start_im], [175], "start")
        slides = CreateImage.create_slides(slide_map[lec_num])
        audio_list = CreateVideo.merge_all_audio(audios_map[lec_num])
        subtitles = transcribe_audio(audio_list)
        audio_durations_list = CreateVideo.calculate_audio_durations(audio_list)
        videos = CreateVideo.images_to_videos(slides, audio_durations_list)
        combined_paths = CreateVideo.combine_videos_with_audios(videos, audio_list, "video")
        transcribeVideo = TranscribeVideo()
        video_paths = transcribeVideo.add_subtitles_to_videos(combined_paths, subtitles)
        path = f'video/final_{name}_{lec_num}.mp4'
        CreateVideo.concatenate_videos(video_paths, path)
        video1 = VideoFileClip(start_vid[0])
        video2 = VideoFileClip(path)
        resized_video1 = video1.resize((1024, 786))
        resized_video2 = video2.resize((1024, 786))
        videos = [resized_video1, resized_video2]
        final_video = concatenate_videoclips(videos, method="compose")
        new_path = f'video/final_edited_{name}_{lec_num}.mp4'
        final_video.write_videofile(new_path)
        paths.append(new_path)
    final_path = f"video/final_{name}.mp4"
    CreateVideo.concatenate_videos(paths, final_path)

    return final_path
