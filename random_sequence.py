from VoiceManager import VoiceManager
import EFX
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
        VoiceManager(wave_filename="./assets/wechat_notice.wav"),
        VoiceManager(wave_filename="./assets/elevator.wav"),
        VoiceManager(wave_filename="./assets/door.wav"),
        VoiceManager(wave_filename="./assets/light.wav"),
        VoiceManager(wave_filename="./assets/jump.wav"),
        ])

    drum_voice = list[VoiceManager]([
        VoiceManager(wave_filename="./assets/click_1.wav"),
        VoiceManager(wave_filename="./assets/click_2.wav"),
        VoiceManager(wave_filename="./assets/ball.wav"),
    ])

