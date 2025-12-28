from VoiceManager import VoiceManager
import EFX
from VoicePlayer import VoicePlayer
import AMP
import random
import numpy as np
import time

if __name__ == "__main__":

    voice_1 = VoiceManager(wave_filename="./assets/water.wav")
    voice_2 = VoiceManager(wave_filename="./assets/bike_1.wav")
    voice_3 = VoiceManager(wave_filename="./assets/shop_1.wav")
    voice_4 = VoiceManager(wave_filename="./assets/bike_2.wav")
    voice_5 = VoiceManager(wave_filename="./assets/wechat_notice.wav")
    voice_list = [voice_1, voice_2]
    voice_list_2 = [voice_3, voice_4]

    voice_list_3 = [None] * 30
    for i in range(30):
        change = random.randint(-100, 100)
        voice_list_3[i] = AMP.precise_tune(voice_5, target_pitch=440 + change)
        voice_list_3[i] = EFX.cut(voice_list_3[i], 0,0.8)
        voice_list_3[i] = EFX.stretch(voice_list_3[i], 1.5)
    
    voice_list_4 = [None] * 60
    for i in range(60):
        change = random.randint(-100, 100)
        voice_list_4[i] = AMP.precise_tune(voice_5, target_pitch=440 + change)
        voice_list_4[i] = EFX.cut(voice_list_4[i], 0,0.8)
        voice_list_4[i] = EFX.stretch(voice_list_4[i], 1)

    # 创建播放器 并播放
    voice_player_1 = VoicePlayer(voice_list, name="voice_player_1")
    voice_player_2 = VoicePlayer(voice_list_2, name="voice_player_2")
    voice_player_3 = VoicePlayer(voice_list_3, name="voice_player_3")
    voice_player_4 = VoicePlayer(voice_list_4, name="voice_player_4")
    voice_player_1.play()
    voice_player_2.play()
    voice_player_3.play()
    voice_player_4.play()

    while voice_player_1.is_playing() and voice_player_2.is_playing() and voice_player_3.is_playing() and voice_player_4.is_playing():
        time.sleep(0.1)

    voice_player_1.stop()
    voice_player_2.stop()
    voice_player_3.stop()
    voice_player_4.stop()
    print("Main Thread Done")