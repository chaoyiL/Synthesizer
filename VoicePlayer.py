import threading
import VoiceManager
import time
import pyaudio
import wave

# 全局变量用于跟踪读取位置
_audio_position = 0
_bytes_per_frame = None

class VoicePlayer:
    def __init__(self, voice_list: list[VoiceManager.VoiceManager]):
        self.voice_list = voice_list
        self.p = pyaudio.PyAudio()
        self.stream_list = [self.p.open(
            format=pyaudio.paInt16, 
            channels=voice.channels, rate=voice.rate, 
            output=True, stream_callback=voice.callback
        ) for voice in self.voice_list]

    def play(self):
        for stream in self.stream_list:
            stream.start_stream()
        total_duration = min([voice.duration for voice in self.voice_list])
        print(f"Total duration: {total_duration} seconds")
        time.sleep(total_duration)

    def stop(self):
        for stream in self.stream_list:
            stream.stop_stream()
            stream.close()
        self.p.terminate()

if __name__ == "__main__":

    voice_1 = VoiceManager.VoiceManager(wave_filename="./assets/water.wav")
    voice_2 = VoiceManager.VoiceManager(wave_filename="./assets/bike_1.wav")
    voice_3 = VoiceManager.VoiceManager(wave_filename="./assets/shop_1.wav")
    voice_4 = VoiceManager.VoiceManager(wave_filename="./assets/bike_2.wav")
    voice_list = [voice_1, voice_2, voice_3, voice_4]

    voice_player = VoicePlayer(voice_list)
    voice_player.play()

    voice_player.stop()
    print("Main Thread Done")