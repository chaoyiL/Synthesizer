import threading
import VoiceManager
import time
import pyaudio
import wave
import numpy as np

# 全局变量用于跟踪读取位置
_audio_position = 0
_bytes_per_frame = None

class VoicePlayer:
    '''非阻塞式地播放一个playlist'''
    def __init__(self, voice_list: list[VoiceManager.VoiceManager]):
        self.voice_list = voice_list
        self.p = pyaudio.PyAudio()
        self.stream = None
        self.total_duration = sum([voice.duration for voice in self.voice_list])

    def play(self):
        print(f"Total duration: {self.total_duration} seconds")

        # 拼接全轨
        total_track_array_left = np.concatenate([voice.left_channel for voice in self.voice_list])
        total_track_array_right = np.concatenate([voice.right_channel for voice in self.voice_list if voice.right_channel is not None])
        total_track = VoiceManager.VoiceManager(left_channel=total_track_array_left, right_channel=total_track_array_right, sample_rate=self.voice_list[0].rate)

        self.stream = self.p.open(
            format=pyaudio.paInt16, 
            channels=total_track.channels, rate=total_track.rate, 
            output=True, stream_callback=total_track.callback
        )
        self.stream.start_stream()

    def stop(self):
        self.stream.stop_stream()
        self.stream.close()
        self.p.terminate()

    def is_playing(self) -> bool:
        return self.stream.is_active()

if __name__ == "__main__":

    voice_1 = VoiceManager.VoiceManager(wave_filename="./assets/water.wav")
    voice_2 = VoiceManager.VoiceManager(wave_filename="./assets/bike_1.wav")
    voice_3 = VoiceManager.VoiceManager(wave_filename="./assets/shop_1.wav")
    voice_4 = VoiceManager.VoiceManager(wave_filename="./assets/bike_2.wav")
    voice_list = [voice_1, voice_2]
    voice_list_2 = [voice_3, voice_4]

    voice_player_1 = VoicePlayer(voice_list)
    voice_player_2 = VoicePlayer(voice_list_2)
    voice_player_1.play()
    voice_player_2.play()

    while voice_player_1.is_playing() and voice_player_2.is_playing():
        time.sleep(0.1)

    voice_player_1.stop()
    voice_player_2.stop()
    print("Main Thread Done")