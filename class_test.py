# python == 3.8.0
import VoiceManager
import EFX
import AMP
import numpy as np

if __name__ == "__main__":
    voice_1_ori = VoiceManager.VoiceManager(wave_filename="./assets/wechat_notice.wav")
    left_channel, right_channel = voice_1_ori.get_audio_array()
    voice_1 = EFX.cut(voice_1_ori, 0.71, -1)
    voice_1 = EFX.add_head(voice_1, 0.3)
    voice_1.play_audio()

    voice_2 = VoiceManager.VoiceManager(left_channel=left_channel, sample_rate=60000)
    voice_2 = EFX.cut(voice_2, 0.57, -1)
    voice_2 = EFX.add_head(voice_2, 0.3)
    voice_2.play_audio()
    
    factor = 1.1
    voice_3 = AMP.tune_resample(voice_1, factor)
    voice_3.play_audio()

    voice_4 = AMP.tune(voice_1_ori, 3)
    voice_4.play_audio()