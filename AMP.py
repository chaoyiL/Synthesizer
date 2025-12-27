import numpy as np
from VoiceManager import VoiceManager
import EFX
import librosa
import torch
import torchaudio.functional as F

def get_pitch(voice_manager: VoiceManager) -> float:
    """
    检测单个音高（基频）
    
    Args:
        voice_manager: VoiceManager对象，包含音频数据
        
    Returns:
        float: 检测到的音高频率（Hz）
    """
    left_channel, right_channel = voice_manager.get_audio_array()
    left_channel = left_channel.astype(np.float32)
    
    # 使用librosa的pyin方法进行音高检测，更适合检测单个音高
    pitch, voiced_flag, voiced_probs = librosa.pyin(
        y=left_channel, 
        sr=voice_manager.rate,
        fmin=librosa.note_to_hz('C2'),  # 最低频率约65.41 Hz
        fmax=librosa.note_to_hz('C7')   # 最高频率约2093 Hz
    )
    
    # 返回有声音段的中位数音高，如果全部为NaN则返回NaN
    pitch_median = np.nanmedian(pitch[voiced_flag])
    
    # 如果中位数为NaN，尝试使用最大值
    if np.isnan(pitch_median):
        pitch_median = np.nanmax(pitch)
    
    return float(pitch_median) if not np.isnan(pitch_median) else 0.0

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

def precise_tune(voice_manager: VoiceManager, target_pitch: float, bins_per_octave: int = 12) -> VoiceManager:
    """
    将音频调成指定的目标音高
    
    Args:
        voice_manager: VoiceManager对象，包含音频数据
        target_pitch: 目标音高频率（Hz）
        bins_per_octave: 每八度的音阶数，默认12（半音）
        
    Returns:
        VoiceManager: 调音后的VoiceManager对象
        
    Raises:
        ValueError: 如果无法检测当前音高或目标音高无效
    """
    # 获取当前音高
    current_pitch = get_pitch(voice_manager)
    
    # 检查当前音高是否有效
    if current_pitch <= 0:
        raise ValueError(f"无法检测当前音高（检测结果为 {current_pitch} Hz），无法进行调音")
    
    # 检查目标音高是否有效
    if target_pitch <= 0:
        raise ValueError(f"目标音高无效（{target_pitch} Hz），必须大于0")
    
    # 计算需要调整的半音步数
    # 公式：steps = 12 * log2(目标频率 / 当前频率)
    steps = bins_per_octave * np.log2(target_pitch / current_pitch)
    
    # 使用tune函数进行调音
    return tune(voice_manager, steps, bins_per_octave)