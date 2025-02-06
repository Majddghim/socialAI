import yt_dlp
import assemblyai as aai
import os


class AssemblyAI:
    def __init__(self):
        aai.settings.api_key = ""

    def transcribe(self, audio_file):
        if not os.path.exists(audio_file):
            raise FileNotFoundError(f"Audio file not found: {audio_file}")

        transcriber = aai.Transcriber()
        transcript = transcriber.transcribe(audio_file)
        return transcript.text if transcript else None

    def download_youtube_audio(self, youtube_url, output_path="audio.mp3"):
        """Downloads audio from a YouTube video."""
        ydl_opts = {
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
            'outtmpl': output_path[:-4],  # Ensures it does not add .mp3 twice
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([youtube_url])

        # Handle possible renaming issue
        if os.path.exists(output_path):
            return output_path
        elif os.path.exists(output_path + ".mp3"):
            return output_path + ".mp3"
        else:
            raise FileNotFoundError("Downloaded audio file not found.")


if __name__ == "__main__":
    youtube_url = "https://www.youtube.com/watch?v=mBFf-aYoV6Q"

    # Create an instance of AssemblyAI
    assembly_ai = AssemblyAI()

    # Step 1: Download YouTube audio
    audio_file = assembly_ai.download_youtube_audio(youtube_url)

    # Step 2: Transcribe the downloaded file
    transcript = assembly_ai.transcribe(audio_file)

    # Step 3: Print the result
    print("Transcript:", transcript)
