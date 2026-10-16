
from pathlib import Path
from dotenv import load_dotenv

from core.transcriber import transcribe_all

load_dotenv()

audio_path = Path("downloads/7 AI Terms You Need to Know： Agents, RAG, ASI & More.wav")

chunks = [
    Path(f"{audio_path}_chunk_{i}.wav")
    for i in range(3)
]

# Check that all three chunks exist before starting
for chunk in chunks:
    if not chunk.exists():
        raise FileNotFoundError(f"Audio chunk not found: {chunk}")

transcript = transcribe_all(
    [str(chunk) for chunk in chunks],
    language="english"
)

output_path = Path("meeting_transcript.txt")
output_path.write_text(transcript, encoding="utf-8")

print("\nTranscription saved successfully!")
print(f"File: {output_path.resolve()}")
print(f"Characters: {len(transcript)}")
print("\nPreview:")
print(transcript[:1000])
