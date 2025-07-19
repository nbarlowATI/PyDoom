import io
import wave
import pygame as pg

from doomsettings import SAMPLE_RATE

class SoundEffect:

    def __init__(self, name, engine):
        byte_data = engine.wad_data.sound_effects[name]
        num_samples = byte_data[1] + (byte_data[2] << 8)
        self.raw_samples = byte_data[8:8 + num_samples]
        pg.mixer.init()
        self.wav_buffer = self.convert_to_wav()

    def convert_to_wav(self):
        # Convert to a WAV in memory
        wav_buffer = io.BytesIO()
        with wave.open(wav_buffer, 'wb') as wf:
            wf.setnchannels(1)
            wf.setsampwidth(1)  # 8-bit unsigned
            wf.setframerate(SAMPLE_RATE)
            wf.writeframes(self.raw_samples)

        wav_buffer.seek(0)
        return wav_buffer
    
    def play(self):
        wav_buffer = self.convert_to_wav()
        sound = pg.mixer.Sound(wav_buffer)
        sound.play()

