# python == 3.8.0
import VoiceManager
import EFX
import AMP
import numpy as np

if __name__ == "__main__":
    voice_ori = VoiceManager.VoiceManager(wave_filename="./assets/clock.wav")
    left_channel, right_channel = voice_ori.get_audio_array()
    # voice_1 = EFX.cut(voice_ori, 0.7, -1)
    # voice_1 = EFX.add_tail(voice_ori, 0.1)
    voice_ori.play_audio()

    voice_2 = EFX.strech(voice_ori, 30)
    voice_2.play_audio()

    voice_3 = EFX.strech(voice_ori, voice_ori.duration/2)
    voice_3.play_audio()