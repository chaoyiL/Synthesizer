import numpy as np
from VoiceManager import VoiceManager
import EFX

# TODO: 需要改进
# def base_freq(voice_manager: VoiceManager) -> float:
#     """
#     Get the base frequency of the array
#     """
#     array = EFX.FFT(voice_manager)[0]
#     base_freq = 1000
#     while base_freq >= 1000:
#         base_freq = np.argmax(array)
#         array = np.delete(array, base_freq)

#     return base_freq

def tune_resample(voice_manager: VoiceManager, factor: float) -> VoiceManager:
    """
    Resample the voice manager by a factor
    """
    sample_rate_original = voice_manager.rate
    sample_rate_target = int(sample_rate_original * factor)

    voice_manager_new = VoiceManager(left_channel=voice_manager.left_channel, 
                                right_channel=voice_manager.right_channel, 
                                sample_rate=sample_rate_target)
    
    return voice_manager_new

# 原理有误
def tune_FFT(voice_manager: VoiceManager, factor: float) -> VoiceManager:
    """
    Tune the array by a factor
    """
    sample_rate = voice_manager.rate
    left_channel_FFT, right_channel_FFT = EFX.FFT(voice_manager)
    
    # 相位存在问题
    left_channel_FFT_tuned = np.zeros((int(len(left_channel_FFT) * factor),))
    for i in range(len(left_channel_FFT)):
        left_channel_FFT_tuned[int(i * factor)] = left_channel_FFT[i]
    left_channel_tuned = np.real(EFX.IFFT(left_channel_FFT_tuned)).astype(np.int16)

    if right_channel_FFT is not None:
        right_channel_FFT_tuned = np.zeros((int(len(right_channel_FFT) * factor),))
        for i in range(len(right_channel_FFT)):
            right_channel_FFT_tuned[int(i * factor)] = right_channel_FFT[i]
        right_channel_tuned = np.real(EFX.IFFT(right_channel_FFT_tuned)).astype(np.int16)
    else:
        right_channel_tuned = None

    voice_manager_new = VoiceManager(left_channel=left_channel_tuned, right_channel=right_channel_tuned, sample_rate=sample_rate)

    return voice_manager_new