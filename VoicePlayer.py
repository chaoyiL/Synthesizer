import threading
import VoiceManager
import time
import pyaudio
import wave
import numpy as np
import AMP
import EFX
import random

# 全局变量用于跟踪读取位置
_audio_position = 0
_bytes_per_frame = None

class VoicePlayer:
    '''非阻塞式地播放一个playlist'''
    def __init__(self, voice_list: list[VoiceManager.VoiceManager], name: str = None):
        self.voice_list = voice_list
        self.p = pyaudio.PyAudio()
        self.stream = None
        self.name = name

    def get_total_track(self):
        """获取拼接后的完整音轨"""
        total_track_array_left = np.concatenate(
            [voice.left_channel for voice in self.voice_list]
        )
        if any(voice.right_channel is None for voice in self.voice_list):
            total_track_array_right = np.concatenate(
                [
                    voice.right_channel
                    for voice in self.voice_list
                    if voice.right_channel is not None
                ]
            )
        else:
            total_track_array_right = None

        total_track = VoiceManager.VoiceManager(
            left_channel=total_track_array_left,
            right_channel=total_track_array_right,
            sample_rate=self.voice_list[0].rate,
            name=self.name,
        )
        return total_track

    def play(self):
        # 拼接全轨
        total_track_array_left = np.concatenate(
            [voice.left_channel for voice in self.voice_list]
        )
        if any(voice.right_channel is None for voice in self.voice_list):
            total_track_array_right = np.concatenate(
                [
                    voice.right_channel
                    for voice in self.voice_list
                    if voice.right_channel is not None
                ]
            )
        else:
            total_track_array_right = None

        total_track = VoiceManager.VoiceManager(
            left_channel=total_track_array_left,
            right_channel=total_track_array_right,
            sample_rate=self.voice_list[0].rate,
        )
        print(
            f"{self.name} Total track frames: {total_track.frames}, total rate: {total_track.rate} Hz, total duration: {total_track.duration}/{total_track.frames} seconds"
        )

        self.stream = self.p.open(
            format=pyaudio.paInt16,
            channels=total_track.channels,
            rate=total_track.rate,
            output=True,
            stream_callback=total_track.callback,
        )
        self.stream.start_stream()

    def stop(self):
        self.stream.stop_stream()
        self.stream.close()
        self.p.terminate()

    def is_playing(self) -> bool:
        return self.stream.is_active()

    def save_to_wav(self, filename: str):
        """将当前播放列表保存为WAV文件"""
        total_track = self.get_total_track()

        with wave.open(filename, "wb") as wf:
            wf.setnchannels(total_track.channels)
            wf.setsampwidth(total_track.sampwidth)
            wf.setframerate(total_track.rate)
            wf.writeframes(total_track.audio_data)

        print(f"已保存到: {filename}")


def mix_and_save_players(voice_players: list[VoicePlayer], output_filename: str):
    """
    将多个 VoicePlayer 的音频混合并保存为单个WAV文件

    参数:
        voice_players: VoicePlayer 对象列表
        output_filename: 输出文件名
    """
    if not voice_players:
        raise ValueError("voice_players 列表不能为空")

    # 获取所有音轨
    all_tracks = [player.get_total_track() for player in voice_players]

    # 确定最大长度和采样率
    max_frames = max(track.frames for track in all_tracks)
    sample_rate = all_tracks[0].rate

    # 确定输出声道数（所有音轨都支持立体声才用立体声）
    has_stereo = any(track.channels == 2 for track in all_tracks)
    channels = 2 if has_stereo else 1

    print(f"混合 {len(voice_players)} 个音轨...")
    print(f"最大帧数: {max_frames}, 采样率: {sample_rate}Hz, 声道: {channels}")

    # 初始化混合数组
    mixed_left = np.zeros(max_frames, dtype=np.int32)
    mixed_right = np.zeros(max_frames, dtype=np.int32)

    # 混合所有音轨
    for i, track in enumerate(all_tracks):
        # 将左声道添加到混合中
        mixed_left[: track.frames] += track.left_channel.astype(np.int32)

        # 处理右声道
        if track.right_channel is not None:
            # 单声道音轨：右声道也用左声道
            right_channel = track.right_channel
        else:
            # 单声道音轨：右声道也用左声道
            right_channel = track.left_channel

        mixed_right[: track.frames] += right_channel.astype(np.int32)

        print(f"  音轨 {i+1}: {track.frames} 帧, {track.channels} 声道")

    # 归一化处理（防止溢出）
    max_amplitude = max(np.max(np.abs(mixed_left)), np.max(np.abs(mixed_right)))
    if max_amplitude > 0:
        # 计算缩放因子，使最大振幅不超过 int16 的范围
        scale_factor = (2**15 - 1) / max_amplitude
        mixed_left = (mixed_left * scale_factor).astype(np.int16)
        mixed_right = (mixed_right * scale_factor).astype(np.int16)

    # 根据声道数合并数据
    if channels == 2:
        # 立体声：交错左右声道
        mixed_array = np.column_stack((mixed_left, mixed_right)).flatten()
    else:
        # 单声道：只使用左声道
        mixed_array = mixed_left

    # 保存为WAV文件
    with wave.open(output_filename, "wb") as wf:
        wf.setnchannels(channels)
        wf.setsampwidth(2)  # int16 = 2 bytes
        wf.setframerate(sample_rate)
        wf.writeframes(mixed_array.tobytes())

    duration = max_frames / sample_rate
    print("混合完成！")
    print(f"输出文件: {output_filename}")
    print(f"时长: {duration:.2f} 秒")
    print(f"峰值振幅: {max_amplitude}")


if __name__ == "__main__":


    def demo1():
        voice_1 = VoiceManager.VoiceManager(wave_filename="./assets/water.wav")
        voice_2 = VoiceManager.VoiceManager(wave_filename="./assets/bike_1.wav")
        voice_3 = VoiceManager.VoiceManager(wave_filename="./assets/shop_1.wav")
        voice_4 = VoiceManager.VoiceManager(wave_filename="./assets/bike_2.wav")
        voice_list = [voice_1, voice_2]
        voice_list_2 = [voice_3, voice_4]

        voice_player_1 = VoicePlayer(voice_list, name="voice_player_1")
        voice_player_2 = VoicePlayer(voice_list_2, name="voice_player_2")

        # 同时播放两个播放器
        voice_player_1.play()
        voice_player_2.play()

        # 将两个播放器混合并保存为WAV文件
        mix_and_save_players(
            [voice_player_1, voice_player_2], "./assets/oputput/mixed_output.wav"
        )

        # 等待播放完成
        while voice_player_1.is_playing() and voice_player_2.is_playing():
            time.sleep(0.1)

        voice_player_1.stop()
        voice_player_2.stop()
        print("Main Thread Done")

    def demo2():
        """
        根据无理数的小数点特征选择音频进行组合,生成符合总时长的音频

        参数:
            total_duration: WAV总时长(秒)
            irrational_number: 无理数作为种子
        """
        import os
        import EFX
        from pathlib import Path

        ASSETS_DIR = Path(__file__).parent / "assets"

        def generate_audio_from_irrational(total_duration: float, irrational_number: float):
            """
            根据无理数生成音频组合

            Args:
                total_duration: 目标总时长(秒)
                irrational_number: 无理数(如 π, e, √2 等)
            """
            # 获取所有可用的音频文件
            audio_files = sorted([f for f in os.listdir(ASSETS_DIR) if f.endswith('.wav')])

            # 将无理数转换为小数字符串(取前100位小数)
            decimal_str = f"{abs(irrational_number):.100f}".replace('.', '')[1:100]

            print(f"无理数种子: {irrational_number}")
            print(f"小数部分(前100位): {decimal_str}")

            # 加载所有音频并记录时长
            audio_info = {}
            for audio_file in audio_files:
                vm = VoiceManager.VoiceManager(wave_filename=os.path.join(ASSETS_DIR, audio_file))
                audio_info[audio_file] = vm.duration
                print(f"  {audio_file}: {vm.duration:.2f}秒")

            # 根据无理数的小数特征选择音频
            selected_voices = []
            remaining_duration = total_duration

            # 使用小数位来选择音频文件和播放次数
            for i in range(0, len(decimal_str), 2):
                if remaining_duration <= 0:
                    break

                # 每两位小数组成一个数字(00-99)
                pair_index = decimal_str[i:i+2]
                if len(pair_index) < 2:
                    continue

                num = int(pair_index)

                # 使用数字来选择音频文件索引
                audio_index = num % len(audio_files)
                audio_file = audio_files[audio_index]

                # 计算这个音频应该播放的时长(根据数字大小决定)
                # 数字越大,播放时长占比越大
                duration_factor = (num + 1) / 100.0
                target_voice_duration = min(remaining_duration * duration_factor, remaining_duration)

                # 加载音频
                voice = VoiceManager.VoiceManager(wave_filename=os.path.join(ASSETS_DIR, audio_file))

                # 如果需要调整时长
                if voice.duration < target_voice_duration:
                    # 拉伸音频
                    voice = EFX.strech(voice, target_voice_duration)
                    print(f"  选择: {audio_file} ({voice.duration:.2f}s -> 拉伸到 {target_voice_duration:.2f}s)")
                elif voice.duration > target_voice_duration:
                    # 截取音频
                    voice = EFX.cut(voice, 0, target_voice_duration)
                    print(f"  选择: {audio_file} ({voice.duration:.2f}s -> 截取到 {target_voice_duration:.2f}s)")
                else:
                    print(f"  选择: {audio_file} ({voice.duration:.2f}s)")

                selected_voices.append(voice)
                remaining_duration -= voice.duration

            # 如果还有剩余时长,用第一个音频循环填充
            if remaining_duration > 0.1:
                first_voice = selected_voices[0]
                if remaining_duration > first_voice.duration:
                    # 拉伸
                    fill_voice = EFX.strech(first_voice, remaining_duration)
                    print(f"  填充: {first_voice.name if hasattr(first_voice, 'name') else 'first'} (拉伸到 {remaining_duration:.2f}s)")
                else:
                    # 截取
                    fill_voice = EFX.cut(first_voice, 0, remaining_duration)
                    print(f"  填充: {first_voice.name if hasattr(first_voice, 'name') else 'first'} (截取到 {remaining_duration:.2f}s)")
                selected_voices.append(fill_voice)

            # 计算实际总时长
            actual_duration = sum(voice.duration for voice in selected_voices)
            print(f"\n目标时长: {total_duration:.2f}秒, 实际时长: {actual_duration:.2f}秒")

            return selected_voices

        # 示例使用
        total_duration = 20.0  # 总时长10秒
        irrational_number = 3.14159265358979323846  # 使用π作为种子

        print("="*60)
        print("Demo 2: 基于无理数种子的音频生成")
        print("="*60)

        # 生成音频组合
        voice_list = generate_audio_from_irrational(total_duration, irrational_number)

        # 创建播放器
        voice_player = VoicePlayer(voice_list, name="irrational_player")

        # 播放
        voice_player.play()

        # 保存为WAV文件
        output_filename = "./assets/output/irrational_mixed.wav"
        os.makedirs(os.path.dirname(output_filename), exist_ok=True)
        voice_player.save_to_wav(output_filename)

        # 等待播放完成
        while voice_player.is_playing():
            time.sleep(0.1)

        voice_player.stop()
        print("Demo 2 完成")

    demo2()