# python == 3.8.0
import numpy as np
from VoiceManager import VoiceManager
import matplotlib.pyplot as plt
from typing import Tuple
from typing import Union
import librosa

def inverse(voice_manager: VoiceManager) -> VoiceManager:
    """
    Inverse the left channel and right channel
    """
    left_channel, right_channel = voice_manager.get_audio_array()
    sample_rate = voice_manager.rate

    left_channel_inverse = np.zeros_like(left_channel)
    right_channel_inverse = None
    for i in range(len(left_channel)):
        left_channel_inverse[i] = left_channel[len(left_channel) - i - 1]

    if right_channel is not None:
        right_channel_inverse = np.zeros_like(right_channel)
        for i in range(len(right_channel)):
            right_channel_inverse[i] = right_channel[len(right_channel) - i - 1]
    
    return VoiceManager(left_channel=left_channel_inverse, 
                        right_channel=right_channel_inverse, 
                        sample_rate=sample_rate)

def cut(voice_manager: VoiceManager, start_time: float, end_time: float) -> VoiceManager:
    """
    Cut the voice from start time to end time
    """
    left_channel, right_channel = voice_manager.get_audio_array()
    sample_rate = voice_manager.rate
    duration = voice_manager.duration

    if start_time < 0 or start_time > duration or end_time > duration:
        raise ValueError("Invalid start time or end time")
    if end_time == -1:
        end_time = duration

    start_index = int(start_time * sample_rate)
    end_index = int(end_time * sample_rate)

    left_channel_cut = left_channel[start_index:end_index]
    if right_channel is not None:
        right_channel_cut = right_channel[start_index:end_index]
    else:
        right_channel_cut = None

    return VoiceManager(left_channel=left_channel_cut, right_channel=right_channel_cut, sample_rate=sample_rate)

def FFT(voice_manager: VoiceManager, display: bool = False) -> Tuple[np.array, Union[np.array, None]]:
    """
    FFT the voice
    """
    left_channel, right_channel = voice_manager.get_audio_array()

    left_channel_FFT = np.fft.fft(left_channel)
    right_channel_FFT = None
    if right_channel is not None:
        right_channel_FFT = np.fft.fft(right_channel)

    if display:
        plt.figure(figsize=(12, 6))
        plt.plot(left_channel_FFT, linewidth=0.5, color='blue', alpha=0.7)
        plt.title('Left Channel FFT', fontsize=14, fontproperties='SimHei')
        plt.xlabel('Frequency (Hz)', fontsize=12, fontproperties='SimHei')
        plt.ylabel('Amplitude', fontsize=12, fontproperties='SimHei')
        plt.grid(True, alpha=0.3)
        plt.show()

        if right_channel is not None:
            plt.plot(right_channel_FFT, linewidth=0.5, color='red', alpha=0.7)
            plt.title('Right Channel FFT', fontsize=14, fontproperties='SimHei')
            plt.xlabel('Frequency (Hz)', fontsize=12, fontproperties='SimHei')
            plt.ylabel('Amplitude', fontsize=12, fontproperties='SimHei')
            plt.grid(True, alpha=0.3)
            plt.show()

    return left_channel_FFT, right_channel_FFT

def IFFT(FFT_array: np.array) -> np.array:
    """
    IFFT the FFT array
    """
    return np.fft.ifft(FFT_array)

def filter(voice_manager: VoiceManager, low_freq: float, high_freq: float) -> VoiceManager:
    """
    Filter the voice by low frequency and high frequency
    """
    sample_rate = voice_manager.rate
    left_channel_FFT, right_channel_FFT = FFT(voice_manager)

    if high_freq == -1:
        high_freq = len(left_channel_FFT)

    # 创建滤波淹掩膜
    filter_mask = np.zeros_like(left_channel_FFT, dtype=complex)
    filter_mask[low_freq:high_freq] = 1 + 0j

    # 应用滤波掩膜
    left_channel_FFT_new = left_channel_FFT * filter_mask
    left_channel = np.real(IFFT(left_channel_FFT_new)).astype(np.int16)

    if right_channel_FFT is not None:
        right_channel_FFT_new = right_channel_FFT * filter_mask    
        right_channel = np.real(IFFT(right_channel_FFT_new)).astype(np.int16)
    else:
        right_channel = None
    
    voice_manager = VoiceManager(left_channel=left_channel, right_channel=right_channel, sample_rate=sample_rate)
    left_channel_FFT, right_channel_FFT = FFT(voice_manager)

    return VoiceManager(left_channel=left_channel, right_channel=right_channel, sample_rate=sample_rate)

def add_tail(voice_manager: VoiceManager, tail_time: float) -> VoiceManager:
    """
    Add tail to the voice
    """
    sample_rate = voice_manager.rate
    left_channel, right_channel = voice_manager.get_audio_array()

    tail_length = int(tail_time * sample_rate)
    tail = np.zeros(tail_length).astype(np.int16)
    left_channel = np.concatenate([left_channel, tail])
    if right_channel is not None:
        right_channel = np.concatenate([right_channel, tail])

    return VoiceManager(left_channel=left_channel, right_channel=right_channel, sample_rate=sample_rate)

def add_head(voice_manager: VoiceManager, head_time: float) -> VoiceManager:
    """
    Add head to the voice
    """
    sample_rate = voice_manager.rate
    left_channel, right_channel = voice_manager.get_audio_array()

    head_length = int(head_time * sample_rate)
    head = np.zeros(head_length).astype(np.int16)
    left_channel = np.concatenate([head, left_channel])
    if right_channel is not None:
        right_channel = np.concatenate([head, right_channel])

    return VoiceManager(left_channel=left_channel, right_channel=right_channel, sample_rate=sample_rate)



def stretch(voice_manager: VoiceManager, target_duration: float) -> VoiceManager:
    """
    Slow down the audio to target duration (time stretch without pitch change)
    
    Args:
        voice_manager: VoiceManager object containing audio data
        target_duration: Target duration in seconds (must be greater than original duration)
    
    Returns:
        VoiceManager: New VoiceManager object with slowed down audio
    """
    original_duration = voice_manager.duration
    sample_rate = voice_manager.rate
    
    if target_duration <= 0:
        raise ValueError(f"Target duration ({target_duration}) must be positive")

    speed_factor = original_duration / target_duration
    left_channel, right_channel = voice_manager.get_audio_array()
    
    # Convert int16 to float32 and normalize to [-1.0, 1.0]
    left_channel_float = left_channel.astype(np.float32) / 32768.0
    left_channel_stretched = librosa.effects.time_stretch(left_channel_float, rate=speed_factor)
    # Convert back to int16
    left_channel_new = (left_channel_stretched * 32768.0).astype(np.int16)
    
    right_channel_new = None
    if right_channel is not None:
        right_channel_float = right_channel.astype(np.float32) / 32768.0
        right_channel_stretched = librosa.effects.time_stretch(right_channel_float, rate=speed_factor)
        right_channel_new = (right_channel_stretched * 32768.0).astype(np.int16)
    
    return VoiceManager(left_channel=left_channel_new, right_channel=right_channel_new, sample_rate=sample_rate)