import whisper

class Transcribe:
    def __init__(self):
        self.model = whisper.load_model("tiny.en")

    def transcribe(self, path):
        audio = whisper.load_audio(path)
        #audio = whisper.pad_or_trim(audio)
        return self.model.transcribe(audio, append_punctuations="\"'.。,，!！?？:：”)]}、")["text"]
