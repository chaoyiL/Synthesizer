import numpy as np
from VoiceManager import VoiceManager
import EFX
import librosa

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

def tune(voice_manager: VoiceManager, steps: float, bins_per_octave: int = 12) -> VoiceManager:
    wav_data_left = voice_manager.left_channel
    if voice_manager.right_channel is not None: 
        wav_data_right = voice_manager.right_channel
    else:
        wav_data_right = None

    wav_data_left = wav_data_left.astype(np.float32)
    if wav_data_right is not None:
        wav_data_right = wav_data_right.astype(np.float32)

    wav_data_tuned_left = librosa.effects.pitch_shift(wav_data_left, sr=voice_manager.rate, n_steps=steps, bins_per_octave=bins_per_octave)
    if wav_data_right is not None:
        wav_data_tuned_right = librosa.effects.pitch_shift(wav_data_right, sr=voice_manager.rate, n_steps=steps, bins_per_octave=bins_per_octave)
    else:
        wav_data_tuned_right = None
    
    wav_data_tuned_left = wav_data_tuned_left.astype(np.int16)
    if wav_data_tuned_right is not None:
        wav_data_tuned_right = wav_data_tuned_right.astype(np.int16)

    voice_manager_new = VoiceManager(left_channel=wav_data_tuned_left, right_channel=wav_data_tuned_right, sample_rate=voice_manager.rate)
    return voice_manager_new