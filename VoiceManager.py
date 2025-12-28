import pyaudio
import wave
import matplotlib.pyplot as plt
import numpy as np
import threading
from typing import Tuple
from typing import Union

class VoiceManager():
    def __init__(
        self,
        name: str = None,
        wave_filename: Union[str, None] = None,
        left_channel: Union[np.array, None] = None,
        right_channel: Union[np.array, None] = None,
        sample_rate: Union[int, None] = None,
    ):
        default_sample_rate = 48000  # default sample rate
        self.wf = None
        self.name = name

        # basic info of wave
        self.channels = None
        self.rate = sample_rate
        self.frames = None
        self.duration = None
        
        self.sampwidth = None

        # what we want to eventually get and use
        self.audio_data = None
        self.audio_array = None
        self.left_channel = None
        self.right_channel = None

        # for non-blocking audio playback
        self._play_thread = None
        self._pyaudio_instance = None
        self._audio_stream = None
        self._is_playing = False

        # create voice from wave file
        if wave_filename is not None and left_channel is None and right_channel is None:
            self.wf = wave.open(wave_filename, "rb")

            if sample_rate is None:
                self.rate = self.wf.getframerate()  # 采样率
            else:
                self.rate = sample_rate

            self.channels = self.wf.getnchannels()  # 声道数
            self.frames = self.wf.getnframes()  # 总帧数
            self.duration = self.frames / self.rate  # 音频时长（秒）
            self.sampwidth = self.wf.getsampwidth()

            self.audio_data = self.wf.readframes(self.frames)  # 读取所有音频数据
            self.audio_array = np.frombuffer(
                self.audio_data, dtype=np.int16
            )  # 将字节数据转换为numpy数组

            if self.channels == 2:
                self.audio_array = self.audio_array.reshape(-1, 2)
                self.left_channel = self.audio_array[:, 0]
                self.right_channel = self.audio_array[:, 1]
            else:
                self.left_channel = self.audio_array
                self.right_channel = None

        elif left_channel is not None:
            self.left_channel = left_channel
            self.right_channel = right_channel

            if sample_rate is None:
                self.rate = default_sample_rate
            else:
                self.rate = sample_rate

            if right_channel is not None:
                self.audio_array = np.concatenate([left_channel.reshape(-1, 1), right_channel.reshape(-1, 1)], axis=1)
                self.channels = 2
            else:
                self.audio_array = left_channel
                self.channels = 1

            self.frames = len(self.audio_array)
            self.duration = self.frames / self.rate
            self.audio_data = self.audio_array.tobytes()
            self.sampwidth = 2 # 统一为 Int16

        else:
            raise ValueError("Invalid input")
        
        self._audio_position = 0
        self._bytes_per_frame = self.sampwidth * self.channels


    def get_audio_array(self) -> Tuple[np.array, Union[np.array, None]]:
        """
        Get the audio array
        """
        return self.left_channel, self.right_channel

    def play_audio(self):
        """
        Play the audio (blocking)
        """
        p = pyaudio.PyAudio()
        stream = p.open(
            format=pyaudio.paInt16, 
            channels=self.channels, rate=self.rate, 
            output=True)
        stream.write(self.audio_data) 
        stream.stop_stream()
        stream.close()
        p.terminate()

    def callback(self, in_data, frame_count, time_info, status):

        # 计算需要读取的字节数
        bytes_to_read = frame_count * self._bytes_per_frame

        if self._audio_position == 0:
            print(f"{self.name} start playing")
        
        # 检查是否还有数据可读
        if self._audio_position >= len(self.audio_data):
            return (b'', pyaudio.paComplete)
        
        # 读取数据
        end_position = min(self._audio_position + bytes_to_read, len(self.audio_data))
        data = self.audio_data[self._audio_position:end_position]
        self._audio_position = end_position
        
        # 如果数据不足一帧，返回空数据并完成
        if len(data) < bytes_to_read:
            return (data, pyaudio.paComplete)
        
        return (data, pyaudio.paContinue)
    
    def visualize_audio(self):
        """
        Visualize the audio
        """
        plt.figure(figsize=(12, 6))
        # 创建时间轴
        time_axis = np.linspace(0, self.duration, len(self.left_channel))

        # 创建图形
        if self.channels == 2:
            # 立体声：显示两个声道
            plt.subplot(2, 1, 1)
            plt.plot(
                time_axis, self.left_channel, linewidth=0.5, color="blue", alpha=0.7
            )
            plt.title("左声道波形", fontsize=14, fontproperties="SimHei")
            plt.xlabel("时间 (秒)", fontsize=12, fontproperties="SimHei")
            plt.ylabel("振幅", fontsize=12, fontproperties="SimHei")
            plt.grid(True, alpha=0.3)

            plt.subplot(2, 1, 2)
            plt.plot(
                time_axis, self.right_channel, linewidth=0.5, color="red", alpha=0.7
            )
            plt.title("右声道波形", fontsize=14, fontproperties="SimHei")
            plt.xlabel("时间 (秒)", fontsize=12, fontproperties="SimHei")
            plt.ylabel("振幅", fontsize=12, fontproperties="SimHei")
            plt.grid(True, alpha=0.3)
        else:
            # 单声道：只显示一个声道
            plt.plot(
                time_axis, self.left_channel, linewidth=0.5, color="blue", alpha=0.7
            )
            plt.title("音频波形", fontsize=14, fontproperties="SimHei")
            plt.xlabel("时间 (秒)", fontsize=12, fontproperties="SimHei")
            plt.ylabel("振幅", fontsize=12, fontproperties="SimHei")
            plt.grid(True, alpha=0.3)

        plt.tight_layout()
        plt.show()

        print("波形可视化完成.")