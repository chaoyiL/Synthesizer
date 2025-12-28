from VoiceManager import VoiceManager
import EFX
from VoicePlayer import VoicePlayer, mix_and_save_players
import AMP
import random
import numpy as np
import time

if __name__ == "__main__":

    env_voice = list[VoiceManager](
        [VoiceManager(wave_filename="./assets/bike_1.wav"), 
        VoiceManager(wave_filename="./assets/bike_2.wav"),
        VoiceManager(wave_filename="./assets/lib.wav"),
        VoiceManager(wave_filename="./assets/shop_1.wav"),
        VoiceManager(wave_filename="./assets/shop_2.wav"),
        VoiceManager(wave_filename="./assets/water.wav"),
        ])

    quick_voice = list[VoiceManager](
        [
        VoiceManager(wave_filename="./assets/clock.wav"),
        VoiceManager(wave_filename="./assets/elevator_short.wav"),
        VoiceManager(wave_filename="./assets/door.wav"),
        VoiceManager(wave_filename="./assets/light.wav"),
        VoiceManager(wave_filename="./assets/jump.wav"),
        ])

    drum_voice = list[VoiceManager]([
        VoiceManager(wave_filename="./assets/wechat_notice.wav"),
        VoiceManager(wave_filename="./assets/click_1.wav"),
        VoiceManager(wave_filename="./assets/click_2.wav"),
        VoiceManager(wave_filename="./assets/ball.wav"),
    ])

    drum_1 = EFX.add_tail(EFX.cut(drum_voice[0], 0.3, 1), 0.3)
    drum_2 = EFX.add_tail(EFX.cut(drum_voice[1], 0, 0.5), 0.5)

    
    loop = [drum_1, drum_2, drum_2, drum_2] # 1.5s
    section = loop*4 # 24s
    player = VoicePlayer(section, name="section")
    player.play()
    mix_and_save_players([player], "./repeat.wav")

    while player.is_playing():
        time.sleep(0.1)
        print("Playing...")

    player.stop()
    print("Done")


    # 创建播放器
    # voice_player_1 = VoicePlayer(voice_list, name="voice_player_1")
    # voice_player_1.play()
    # mix_and_save_players([voice_player_1], "./repeat.wav")

    # print("Main Thread Done")