from moviepy.editor import VideoFileClip, CompositeVideoClip, TextClip
import pysrt
import os
from pathlib import Path


def transcribe_audio(audio_files_list, output_directory="Transcriptions"):
    """
    Transcribes a list of audio files into SRT format using Whisper AI.

    Args:
        audio_files_list (list): List of paths to audio files to be transcribed.
        output_directory (str): Directory where the transcription files will be saved. Defaults to "Transcriptions".

    Returns:
        list: List of paths to the generated transcription files (.srt format).

    Raises:
        Exception: If there is an error during the transcription process for an audio file.
    """

    def transcribe_single_audio(audioFile, outputDirectory):
        """
        Transcribes a single audio file using Whisper AI.

        Args:
            audioFile (str): Path to the audio file.
            outputDirectory (str): Directory where the transcription file will be saved.

        Returns:
            Path: Path to the generated transcription file (.srt format).
        """
        output_format = "srt"
        language = "English"

        command = f"whisper {audioFile} --language {language} --output_format {output_format} --task transcribe " \
                  f"--output_dir {outputDirectory} --device cuda"
        os.system(command)

        # Get basename and change extension to .srt
        basename = os.path.splitext(os.path.basename(audioFile))[0]
        transcriptionFile = Path(outputDirectory) / f"{basename}.{output_format}"

        return transcriptionFile

    transcriptions_list = []

    for audio_file in audio_files_list:
        try:
            transcription_file = transcribe_single_audio(audio_file, output_directory)
            transcriptions_list.append(transcription_file)
        except Exception as e:
            print(f"Error transcribing {audio_file}: {e}")
    return transcriptions_list


class TranscribeVideo:
    @staticmethod
    def create_subtitle_clips(subtitles, videosize, fontsize=24, font='Arial', color='black'):
        """
        Creates subtitle text clips for a video from SRT subtitles.

        Args:
            subtitles (list): List of subtitle entries (pysrt.SubRipItem).
            videosize (tuple): Size of the video as (width, height).
            fontsize (int): Font size for the subtitles. Defaults to 24.
            font (str): Font type for the subtitles. Defaults to 'Arial'.
            color (str): Font color for the subtitles. Defaults to 'black'.

        Returns:
            list: List of TextClip objects representing the subtitle text clips.

        Notes:
            - The position of the subtitles is fixed to 4/5 of the video height from the top.
        """

        def time_to_seconds(time_obj):
            """
            Converts a pysrt time object to seconds.

            Args:
                time_obj (pysrt.SubRipTime): Time object to convert.

            Returns:
                float: Time in seconds.
            """
            return time_obj.hours * 3600 + time_obj.minutes * 60 + time_obj.seconds + time_obj.milliseconds / 1000

        subtitle_clips = []

        for subtitle in subtitles:
            start_time = time_to_seconds(subtitle.start)
            end_time = time_to_seconds(subtitle.end)
            duration = end_time - start_time

            video_width, video_height = videosize

            text_clip = TextClip(subtitle.text, fontsize=fontsize, font=font, color=color,
                                 size=(video_width * 3 / 4, None),
                                 method='caption').set_start(start_time).set_duration(duration)
            subtitle_x_position = 'center'
            subtitle_y_position = video_height * 4 / 5

            text_position = (subtitle_x_position, subtitle_y_position)
            subtitle_clips.append(text_clip.set_position(text_position))

        return subtitle_clips

    def add_subtitles_to_video(self, video_file, srt_file, output_file):
        """
        Adds subtitles to a video file from an SRT file.

        Args:
            video_file (str): Path to the video file.
            srt_file (str): Path to the SRT file containing subtitles.
            output_file (str): Path where the output video with subtitles will be saved.

        Returns:
            str: Path to the output video file with subtitles.

        Notes:
            - The video file and SRT file must be in sync for subtitles to match correctly.
        """
        video = VideoFileClip(video_file)
        subtitles = pysrt.open(srt_file)
        subtitle_clips = self.create_subtitle_clips(subtitles, video.size)
        final_video = CompositeVideoClip([video] + subtitle_clips)
        final_video.write_videofile(output_file)
        return output_file

    def add_subtitles_to_videos(self, video_files, srt_files):
        """
        Adds subtitles to multiple video files from their corresponding SRT files.

        Args:
            video_files (list): List of paths to video files.
            srt_files (list): List of paths to SRT files corresponding to the video files.

        Returns:
            list: List of paths to the output video files with subtitles.

        Notes:
            - Each video file in `video_files` must have a corresponding SRT file in `srt_files`.
            - The output videos will be saved with '_subtitled' appended to their original filenames.
        """
        subtitled_videos = []
        for video_file, srt_file in zip(video_files, srt_files):
            output_file = video_file.replace('.mp4', '_subtitled.mp4')
            subtitled_video = self.add_subtitles_to_video(video_file, srt_file, output_file)
            subtitled_videos.append(subtitled_video)

        return subtitled_videos
