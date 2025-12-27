import pyaudio
import wave
import matplotlib.pyplot as plt
import numpy as np

# 配置参数
CHUNK = 1024  # 每次读取的字节数
WAVE_FILENAME = "./assets/clock.wav"  # 要播放的音频文件路径

# 打开音频文件
wf = wave.open(WAVE_FILENAME, "rb")

# 获取音频文件参数
CHANNELS = wf.getnchannels()  # 声道数
RATE = wf.getframerate()  # 采样率
FRAMES = wf.getnframes()  # 总帧数
DURATION = FRAMES / RATE  # 音频时长（秒）

print(f"音频信息: 采样率={RATE}Hz, 声道数={CHANNELS}, 时长={DURATION:.2f}秒")

# 读取所有音频数据
audio_data = wf.readframes(FRAMES)
wf.close()

# 将字节数据转换为numpy数组
audio_array = np.frombuffer(audio_data, dtype=np.int16)  # 用于存储音频信息的数组

# ========== 音频波形可视化功能 ==========

# 如果是立体声，分离左右声道
if CHANNELS == 2:
    audio_array = audio_array.reshape(-1, 2)
    left_channel = audio_array[:, 0]
    right_channel = audio_array[:, 1]
else:
    left_channel = audio_array
    right_channel = None

# 创建时间轴
time_axis = np.linspace(0, DURATION, len(left_channel))

# 创建图形
plt.figure(figsize=(12, 6))

if CHANNELS == 2:
    # 立体声：显示两个声道
    plt.subplot(2, 1, 1)
    plt.plot(time_axis, left_channel, linewidth=0.5, color="blue", alpha=0.7)
    plt.title("左声道波形", fontsize=14, fontproperties="SimHei")
    plt.xlabel("时间 (秒)", fontsize=12, fontproperties="SimHei")
    plt.ylabel("振幅", fontsize=12, fontproperties="SimHei")
    plt.grid(True, alpha=0.3)

    plt.subplot(2, 1, 2)
    plt.plot(time_axis, right_channel, linewidth=0.5, color="red", alpha=0.7)
    plt.title("右声道波形", fontsize=14, fontproperties="SimHei")
    plt.xlabel("时间 (秒)", fontsize=12, fontproperties="SimHei")
    plt.ylabel("振幅", fontsize=12, fontproperties="SimHei")
    plt.grid(True, alpha=0.3)
else:
    # 单声道：只显示一个声道
    plt.plot(time_axis, left_channel, linewidth=0.5, color="blue", alpha=0.7)
    plt.title("音频波形", fontsize=14, fontproperties="SimHei")
    plt.xlabel("时间 (秒)", fontsize=12, fontproperties="SimHei")
    plt.ylabel("振幅", fontsize=12, fontproperties="SimHei")
    plt.grid(True, alpha=0.3)

plt.tight_layout()
plt.show()

print("波形可视化完成.")

# ========== 音频播放功能 ==========
# 重新打开音频文件用于播放
wf_play = wave.open(WAVE_FILENAME, "rb")

# 获取音频文件参数（用于播放）
FORMAT = pyaudio.paInt16  # 音频格式

# 创建 PyAudio 对象
p = pyaudio.PyAudio()

# 打开输出流
stream = p.open(
    format=FORMAT, channels=CHANNELS, rate=RATE, output=True, frames_per_buffer=CHUNK
)

print("开始播放音频...")

# 读取并播放音频数据
data = wf_play.readframes(CHUNK)
while data:
    stream.write(data)
    data = wf_play.readframes(CHUNK)

print("播放结束.")

# 停止并关闭流
stream.stop_stream()
stream.close()

# 释放 PyAudio 对象
p.terminate()

# 关闭文件
wf_play.close()
