import os


from transformers import pipeline
from datasets import load_dataset
import torch
import soundfile as sf


def split_text_into_lines(text, max_width=400):
    """
       Splits the input text into lines of a specified maximum width.

       This function breaks a long string of text into multiple lines,
       ensuring that each line does not exceed a specified maximum width in terms of character count.
       It helps in preparing text for display or further processing, such as generating audio segments.

       Parameters:
       - text (str): The input text to be split into lines.
       - max_width (int): The maximum width (number of characters) for each line. Defaults to 400 characters.

       Returns:
       - list of str: A list of strings where each string is a line that fits within the specified width.
       """
    lines = []
    words = text.split()
    current_line = ""
    for word in words:
        if len(word + current_line) <= max_width:
            current_line += " " + word if current_line else word
        else:
            lines.append(current_line.strip())
            current_line = word
    if current_line:
        lines.append(current_line.strip())
    return lines


def generate_audio_chunks(output):
    """
        Generates audio files from text sections using a text-to-speech (TTS) pipeline.
        This function converts text into speech and saves each speech segment as an audio file.
        It uses a pre-trained TTS model and speaker embeddings to synthesize high-quality speech audio.
        Parameters:
        - output (dict): A dictionary where the keys are section titles and the values are lists of text paragraphs
                         to be converted into speech.
        Returns:
        - dict: A dictionary where the keys are the sanitized section titles and the values are lists of file paths
                to the generated audio files corresponding to each text paragraph.
        """
    # Load dataset containing speaker embeddings
    embeddings_dataset = load_dataset("Matthijs/cmu-arctic-xvectors", split="validation")

    # Example speaker embedding (replace with your own if needed)
    speaker_embedding = torch.tensor(embeddings_dataset[7200]["xvector"]).unsqueeze(0)
    # Initialize the text-to-speech pipeline
    synthesiser = pipeline("text-to-speech", "microsoft/speecht5_tts", device="cuda")
    audio_paths = {}
    # Split the input text into smaller chunks
    for section_title, ls_text in output.items():
        title = section_title.replace(" ", "_")
        title = title.replace("?", "").replace("*", "")
        paths = []
        for j, text in enumerate(ls_text):
            chunks = split_text_into_lines(text)
            # Generate audio for each chunk and save it as a separate file
            for i, chunk in enumerate(chunks):
                path = f"audio/{title}_speech_chunk_{j}_{i + 1}.wav"
                if not os.path.exists(path):
                    # Synthesize speech for the chunk
                    speech_chunk = synthesiser(chunk, forward_params={"speaker_embeddings": speaker_embedding})
                    # Save the audio to a WAV file
                    sf.write(path, speech_chunk["audio"],
                             samplerate=speech_chunk["sampling_rate"])
                    # Export the audio to a WAV file

                if os.path.exists(path):
                    paths.append(path)
        audio_paths[title] = paths

    return audio_paths

