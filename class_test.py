# python == 3.8.0
import VoiceManager
import EFX

if __name__ == "__main__":
    voice_1 = VoiceManager.VoiceManager(wave_filename="./assets/clock.wav")
    left_channel, right_channel = voice_1.get_audio_array()
    # voice_1.play_audio()

    voice_2 = VoiceManager.VoiceManager(left_channel=left_channel, sample_rate=60000)
    voice_2 = EFX.cut(voice_2, 0, 3)
    voice_2.play_audio()
    voice_2.visualize_audio()

    voice_2_left_FFT, _ = EFX.FFT(voice_2, display=True)