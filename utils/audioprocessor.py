import yt_dlp
from pydub import AudioSegment
import os 

DOWNLOAD_DIR='downloads'
os.makedirs(DOWNLOAD_DIR,exist_ok=True)

def download_youtube_audio(url:str)-> str:
    output_path=os.path.join(DOWNLOAD_DIR,"%(title)s.%(ext)s")
    ydl_opts={
        "format": "bestaudio/best",
        "outtmpl": output_path,
        "ffmpeg_location": r"C:\Users\aashi\ffmpeg\ffmpeg-9.0.2-essentials_build\bin",
        "postprocessors":[{
            "key": "FFmpegExtractAudio",
            "preferredcodec":"wav",
            "preferredquality": "192",
        }
        ],
        "quiet":True,   #hides the console logs downloads it quietly without showing a lot on the console
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:              #creates a downloader object configured according to ydl_opts
        info=ydl.extract_info(url,download=True)         #creates a dictionary containing metadata about audio file
        filename=ydl.prepare_filename(info).replace(".webm",".wav").replace(".m4a",".wav")
    return filename



def convert_to_wav(input_path: str) -> str:
    '''Convert any audio/video file to WAV format using pydub'''

    output_path=os.path.splitext(input_path)[0]+"_converted.wav"
    audio=AudioSegment.from_file(input_path)
    audio=audio.set_channels(1).set_frame_rate(16000) #sweet spot for whisper is 16kHz
    audio.export(output_path,format="wav")
    return output_path


def chunk_audio(wav_path: str, chunk_minutes:int=5)-> list:
    audio=AudioSegment.from_wav(wav_path)
    chunk_ms=chunk_minutes*60*1000  #mins->sec->milisec

    chunks=[]

    for i,start in enumerate(range(0,len(audio),chunk_ms)):
        chunk=audio[start:start+chunk_ms]
        chunk_path=f"{wav_path}_chunk_{i}.wav"
        chunk.export(chunk_path,format="wav")

        chunks.append(chunk_path)
    return chunks


def process_input(source: str) -> list:
    if source.startswith(("http://", "https://")):
        print("Detected YouTube URL, Downloading audio...")
        wav_path = download_youtube_audio(source)

    elif os.path.isfile(source):
        print("Detected local file.")

        if source.lower().endswith(".wav"):
            wav_path = source
        else:
            print("Converting to WAV...")
            wav_path = convert_to_wav(source)

    else:
        raise FileNotFoundError(
            f"File not found: {source}\n"
            "Please check the file path and try again."
        )

    print("Chunking audio...")
    chunks = chunk_audio(wav_path)
    print(f"Audio ready - {len(chunks)} chunk(s) created.")
    return chunks




