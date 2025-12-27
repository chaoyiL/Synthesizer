# python == 3.8.0
import VoiceManager
import EFX

if __name__ == "__main__":
    voice_1 = VoiceManager.VoiceManager(wave_filename="./assets/wechat_notice.wav")
    left_channel, right_channel = voice_1.get_audio_array()
    # voice_1.play_audio()

    voice_2 = VoiceManager.VoiceManager(left_channel=left_channel, sample_rate=60000)
    voice_2.play_audio()
    # voice_2.visualize_audio()
    EFX.FFT(voice_2, display=True)

    voice_3 = EFX.filter(voice_2, 10000, -1)
    voice_3.play_audio()
    # voice_3.visualize_audio()
    EFX.FFT(voice_3, display=True)