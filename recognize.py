import os
import json
import glob
from typing import Dict, Optional
import whisper_timestamped as whisper

from utils import extract_speaker_name

def recognize(input_dir: str, names: Dict[str, str], fast: bool = False, slow: bool = False, model_type: Optional[str] = None, device: str = "cuda", audio_ext: str = "ogg"):
    model_type = "tiny" if fast else (model_type if model_type else ("medium" if slow else "small"))
    model = whisper.load_model(model_type, device=device)

    print()
    print("--------------------")
    print("RECOGNIZE")
    print("--------------------")
    print()
    
    files = glob.glob(os.path.join(input_dir, '*.' + audio_ext))

    if not files:
        print(f" No {audio_ext} files were found at {input_dir}.")
        print()
        return

    print(f" {len(files)} {audio_ext} files found at {input_dir}.")
    for audio_file in files:
        print(f" - {audio_file}...")
        speaker = extract_speaker_name(audio_file, audio_ext)
        if speaker in names and (names[speaker] is None or names[speaker] == ''):
            print(f"  Skipping {audio_file} because '{speaker}' is specified as blank.")
            print()
            continue
        else:
            audio = whisper.load_audio(os.path.join(input_dir, audio_file))
            if fast:
                results = whisper.transcribe(
    model, audio,
    detect_disfluencies=True,
    vad="auditok",
    temperature=0.0,
    beam_size=8, best_of=1,
    condition_on_previous_text=False,
    no_speech_threshold=0.355,
    logprob_threshold=-0.6,
    compression_ratio_threshold=1.2,
)
            elif slow:
                results = whisper.transcribe(
    model, audio,
    vad="silero",
    detect_disfluencies=True, language="en",
    temperature=0.0, beam_size=8, best_of=1, patience=1.5,
    condition_on_previous_text=False,
    no_speech_threshold=0.28,       # admit quieter speech / tails
    logprob_threshold=-1.05,         # accept lower-confidence faint words
    compression_ratio_threshold=1.20 # STRICT anti-repeat guard
)
            else:
                results = whisper.transcribe(
    model, audio,
    detect_disfluencies=True,
    vad="auditok",
    temperature=0.0,
    beam_size=8, best_of=1,
    condition_on_previous_text=False,
    no_speech_threshold=0.55,
    logprob_threshold=-0.6,
    compression_ratio_threshold=1.2,
)

            json_file = os.path.join(input_dir, audio_file + '.words.json')
            with open(json_file, 'w') as f:
                f.write(json.dumps(results, ensure_ascii = False))
            print(f"  Saved to {json_file}")
            print()
    print("--------------------")
