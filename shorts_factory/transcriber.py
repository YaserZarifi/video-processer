from faster_whisper import WhisperModel


# Enligh Transcription

# def transcribe_chunk(video_path: str, model_size: str = "small") -> list:
#     model = WhisperModel(model_size, device="cuda", compute_type="float16")
#     segments, info = model.transcribe(video_path, beam_size=5, word_timestamps=True)

# Persian Transcription
def transcribe_chunk(video_path: str, model_size: str = "medium") -> list:
    model = WhisperModel(
        model_size,
        device="cuda",
        compute_type="float16"
    )

    segments, info = model.transcribe(
        video_path,
        language="fa",
        task="transcribe",
        beam_size=5,
        word_timestamps=True
    )

    results = []
    max_words = 4

    for segment in segments:
        if not segment.words:
            continue

        current_words = []
        chunk_start = None

        for word in segment.words:
            if chunk_start is None:
                chunk_start = word.start

            current_words.append(word.word.strip())

            if len(current_words) >= max_words:
                results.append({
                    "start": chunk_start,
                    "end": word.end,
                    "text": " ".join(current_words)
                })

                current_words = []
                chunk_start = None

        if current_words:
            results.append({
                "start": chunk_start,
                "end": segment.words[-1].end,
                "text": " ".join(current_words)
            })

    return results


if __name__ == "__main__":
    import sys

    test_file = sys.argv[1]
    data = transcribe_chunk(test_file)

    for item in data:
        print(f"[{item['start']:.2f}s -> {item['end']:.2f}s]{item['text']}")
