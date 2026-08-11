from faster_whisper import WhisperModel

def transcribe_chunk(video_path: str, model_size: str = "small") -> list:
    model = WhisperModel(model_size, device="cuda", compute_type="float16")
    segments, info = model.transcribe(video_path, beam_size=5)

    results = []
    for segment in segments:
        results.append({
            "start": segment.start,
            "end": segment.end,
            "text": segment.text
        })

    return results

if __name__ == "__main__":
    import sys

    test_file = sys.argv[1]
    data = transcribe_chunk(test_file)

    for item in data:
        print(f"[{item['start']:.2f}s -> {item['end']:.2f}s]{item['text']}")
