import VoiceManager
import EFX

if __name__ == "__main__":
    voice_ori = VoiceManager.VoiceManager(wave_filename="./assets/wechat_notice.wav")
    left_channel, right_channel = voice_ori.get_audio_array()
    # voice_1 = EFX.cut(voice_ori, 0.7, -1)
    # voice_1 = EFX.add_tail(voice_ori, 0.1)
    voice_ori.play_audio()

    voice_2 = EFX.strech(voice_ori, 2)
    voice_2.play_audio()

    voice_3 = EFX.strech(voice_ori, 0.8)
    voice_3.play_audio()