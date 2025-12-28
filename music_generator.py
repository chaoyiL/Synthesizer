import math
from decimal import Decimal, getcontext
from midiutil import MIDIFile
import numpy as np

# ==============================================================================
# 1. 数据定义 (翻译自 In[2], In[6], In[12])
# ==============================================================================

# pa: 用于生成点缀性琶音的音符序列
# Mathematica: Table[{"C"<>ToString[i], ...}, {i,3,8}]
pa_src = [
    # C Major chords
    [note for i in range(3, 9) for note in [f"C{i}", f"E{i}", f"G{i}"]],
    # A Minor chords
    [note for i in range(3, 9) for note in [f"A{i-1}", f"C{i}", f"E{i}"]],
    # F Major chords
    [note for i in range(3, 9) for note in [f"F{i-1}", f"A{i-1}", f"C{i}"]],
    # G Major chords
    [note for i in range(3, 9) for note in [f"G{i-1}", f"B{i-1}", f"D{i}"]],
]

# Mathematica: pa = pa[[All,1;;16]];
pa_src = [seq[:16] for seq in pa_src]

# Mathematica: Flatten[Table[{pa[[i]],Reverse[pa[[i]]]}, ...]]
pa = []
for seq in pa_src:
    pa.append(seq)
    pa.append(seq[::-1])  # [::-1] is Python's way to reverse a list

# c: 用于伴奏的和弦音符列表 (较低音区)
c = [
    ["C3", "C4", "E4", "G4", "C5", "E5", "G5"],  # C Major
    ["A2", "A3", "C4", "E4", "A4", "C5", "E5"],  # A Minor
    ["F2", "F3", "A3", "C4", "F4", "A4", "C5"],  # F Major
    ["G2", "G3", "B3", "D4", "G4", "B4", "D5"],  # G Major
]

# cs: 用于主旋律的和弦音符列表 (较高音区)
cs = [
    ["G4", "C5", "E5", "G5", "C6", "E6", "G6"],  # C Major
    ["E4", "A4", "C5", "E5", "A5", "C6", "E6"],  # A Minor
    ["C4", "F4", "A4", "C5", "F5", "A5", "C6"],  # F Major
    ["D4", "G4", "B4", "D5", "G5", "B5", "D6"],  # G Major
]


# ==============================================================================
# 2. 辅助函数
# ==============================================================================


def note_to_midi_pitch(note_name):
    """将音符名称 (如 "C4") 转换为 MIDI 音高值 (如 60)"""
    pitch_map = {"C": 0, "D": 2, "E": 4, "F": 5, "G": 7, "A": 9, "B": 11}
    accidental_map = {"#": 1, "b": -1}

    note = note_name[0].upper()
    octave = int(note_name[-1])

    pitch = pitch_map[note]

    if len(note_name) > 2:
        accidental = note_name[1]
        if accidental in accidental_map:
            pitch += accidental_map[accidental]

    return 12 * (octave + 1) + pitch


def get_digits(number, num_digits):
    """
    获取一个数字的前 n 位小数。等效于 Mathematica 的 RealDigits。
    我们使用 decimal 模块来处理高精度。
    """
    getcontext().prec = num_digits + 5  # 设置足够的精度
    d = Decimal(number)
    s = str(d).replace(".", "")
    # 如果是 pi, e 等，它们会以 "31415..." 的形式出现
    # 如果是 sqrt(2)，它会是 "14142..."
    # 我们需要确保只取小数点后的数字，但代码逻辑似乎用了整数部分
    # Mathematica 的 RealDigits[[1]] 返回一个数字列表。
    # 为了匹配 Mathematica 的行为，我们返回一个整数列表。
    # Mathematica `RealDigits[Pi, 10, 5]` -> {{3, 1, 4, 1, 5}, 1}
    # 我们需要这个 {3, 1, 4, 1, 5} 部分
    return [int(digit) for digit in s[:num_digits]]


# ==============================================================================
# 3. 音乐生成逻辑 (翻译自 In[9] Accomp 和 In[11] Gen)
# ==============================================================================


def add_accomp(midi_file, start_measure, num_measures, slshli, moveli):
    """
    向 MIDI 文件添加伴奏部分。等效于 Mathematica 的 Accomp。

    在 Mathematica 代码中，时间单位似乎是“节拍”，其中每个“小节” s 包含 8 个节拍。
    我们将遵循这个约定。Tempo 设为 120 bpm, 4/4 拍，那么一个小节是 4 拍。
    所以 Mathematica 的一个 "measure" (8 拍) 等于两个标准 4/4 小节。
    """
    track_violin = 0
    track_piano = 1
    channel = 0
    vol = 90  # MIDI 音量范围 0-127

    # s: Mathematica 中的小节索引 (0-indexed)
    for s_offset in range(num_measures):
        s = start_measure + s_offset

        # 添加小提琴低音 (Violin Bassline)
        # 每个音符持续 2 拍
        for n in range(4):  # n 是和弦索引 C, Am, F, G
            pitch = note_to_midi_pitch(c[n][0])
            time = 8 * s + 2 * n  # 开始时间
            duration = 2  # 持续时间
            midi_file.addNote(track_violin, channel, pitch, time, duration, vol)

        # 添加钢琴和弦 (Piano Chords)
        # 每个和弦持续 2 拍，被分成 4 个半拍的和弦音
        for n in range(4):  # 和弦索引
            for m in range(1, 5):  # m 是半拍索引 (1, 2, 3, 4)
                # 选择和弦音符 (根音或转位)
                # Mathematica: If[MemberQ[moveli,m], c[[n,3;;5]], c[[n,1;;4]]]
                # 3;;5 -> Python slice [2:5]
                # 1;;4 -> Python slice [0:4]
                if m in moveli:
                    chord_notes = c[n][2:5]
                else:
                    chord_notes = c[n][0:4]

                pitches = [note_to_midi_pitch(note) for note in chord_notes]

                # 处理切分节奏 (slshli)
                # Mathematica: sl[..., MemberQ[slshli,m]]
                base_time = 8 * s + 2 * n + (m - 1) * 0.5

                if m in slshli:
                    # 分成两个 1/4 拍的音符
                    duration = 0.25
                    for pitch in pitches:
                        midi_file.addNote(
                            track_piano, channel, pitch, base_time, duration, vol
                        )
                    for pitch in pitches:
                        midi_file.addNote(
                            track_piano, channel, pitch, base_time + 0.25, duration, vol
                        )
                else:
                    # 单个 1/2 拍的音符
                    duration = 0.5
                    for pitch in pitches:
                        midi_file.addNote(
                            track_piano, channel, pitch, base_time, duration, vol
                        )


def gen_music(number, num_measures, output_filename):
    """
    主生成函数。等效于 Mathematica 的 Gen。
    """
    print(f"Generating music for {output_filename} based on {number}...")

    # 1. 从数字生成控制序列
    # Mathematica: g = RealDigits[num, 10, 8*(st+1)][[1]]
    # 我们需要足够的数字来覆盖所有索引访问：
    # - mainli: 最大索引 8*num_measures
    # - 主旋律 g_idx: 最大索引约为 7 + floor((32*(num_measures-1)-1)/32) * 8
    # 为了安全，我们生成更多数字
    num_digits_needed = max(8 * (num_measures + 1), 32 * num_measures)
    g = get_digits(number, num_digits_needed)
    print(f"Generated {len(g)} digits for processing")

    # mainli: 控制主旋律的节奏 (奇偶小节疏密交错)
    # Mathematica indices are 1-based, Python are 0-based.
    mainli = []
    for s in range(1, num_measures + 1):
        if s % 2 != 0:  # 奇数小节
            # M: 8s-6;;8s-1 -> P: [8s-7 : 8s-1]
            mainli.append(g[8 * s - 7 : 8 * s - 1])
        else:  # 偶数小节
            # M: 8s-10;;8s -> P: [8s-11 : 8s]
            mainli.append(g[8 * s - 11 : 8 * s])

    # slshli, moveli: 控制伴奏的节奏和转位
    # M: Mod[g[[no]],4,1] -> P: (g[no-1] % 4) + 1
    slshli = [[(g[no - 1] % 4) + 1] for no in range(1, num_measures + 1)]
    # M: Mod[g[[no+1;;no+2]],4,1] -> P: [(d % 4) + 1 for d in g[no:no+2]]
    moveli = [[(d % 4) + 1 for d in g[no : no + 2]] for no in range(num_measures)]

    # 2. 初始化 MIDI 对象
    num_tracks = 4
    midi_file = MIDIFile(num_tracks)

    # 定义轨道和乐器
    # Track 0: Violin (bass)
    # Track 1: Piano (accomp)
    # Track 2: Piano/Flute (melody)
    # Track 3: Piano (embellishment)

    tempo = 120  # bpm
    midi_file.addTempo(0, 0, tempo)
    midi_file.addTempo(1, 0, tempo)
    midi_file.addTempo(2, 0, tempo)
    midi_file.addTempo(3, 0, tempo)

    # MIDI Program Numbers (see General MIDI standard)
    VIOLIN = 41
    ACOUSTIC_GRAND_PIANO = 1
    FLUTE = 74

    midi_file.addProgramChange(0, 0, 0, VIOLIN)
    midi_file.addProgramChange(1, 0, 0, ACOUSTIC_GRAND_PIANO)
    # Track 2's instrument will change during generation
    midi_file.addProgramChange(3, 0, 0, ACOUSTIC_GRAND_PIANO)

    # 3. 生成音乐内容

    # 生成伴奏
    # M: Table[Accomp[no,2,slshli[[no]],moveli[[no]]],{no,1,st}]
    # 伴奏似乎是每两小节使用相同的节奏/转位模式
    for no in range(0, num_measures, 2):
        if no < len(slshli) and no < len(moveli):
            add_accomp(midi_file, no, 2, slshli[no], moveli[no])

    # 生成主旋律
    melody_vol = 110
    # M: Table[If[...], {i, 1, 32*(st-1)}]
    for i in range(1, 32 * (num_measures - 1) + 1):
        # 计算节奏和位置
        # M: Ceiling[i/(8*4)] -> P: math.ceil(i/32)
        measure_idx_1based = math.ceil(i / 32)
        measure_idx_0based = measure_idx_1based - 1

        # M: Mod[i,8,1] -> P: (i-1) % 8 + 1
        rhythm_pos = (i - 1) % 8 + 1

        # M: Mod[Ceiling[i/8],4] == 3
        quarter_beat_of_measure = math.ceil(i / 8) % 4

        # 检查是否应该播放音符
        play_note = False
        if rhythm_pos in mainli[measure_idx_0based] or quarter_beat_of_measure == 3:
            play_note = True

        if play_note:
            # 确定乐器
            # M: If[OddQ[Floor[i/32-0.01]],"Piano","Flute"]
            is_odd_measure = math.floor((i - 1) / 32) % 2 != 0
            instrument = ACOUSTIC_GRAND_PIANO if is_odd_measure else FLUTE
            # We need to add a program change event at the start of the measure
            measure_start_time = measure_idx_0based * 8
            midi_file.addProgramChange(2, 0, measure_start_time, instrument)

            # 确定音高
            # M: cs[[Mod[Ceiling[i/8],4,1], ...]]
            chord_idx = (math.ceil(i / 8) - 1) % 4

            # M: Mod[g[[Mod[i,8,1]+Floor[i/32]*8]],6]+2
            g_idx = ((i - 1) % 8) + math.floor((i - 1) / 32) * 8
            # In M, indices are 1-based. `+2` means indices 2..7.
            # In Python, this means indices 1..6.
            if g_idx >= len(g):
                print(f"Warning: g_idx={g_idx} exceeds g length={len(g)} at i={i}")
                g_idx = g_idx % len(g)  # 循环使用
            note_in_chord_idx = (g[g_idx] % 6) + 1

            note_name = cs[chord_idx][note_in_chord_idx]
            pitch = note_to_midi_pitch(note_name)

            # M: {8+(i-1)/4, 8+i/4} -> start_time = 8 + (i-1)/4, duration = 1/4
            time = 8 + (i - 1) * 0.25
            duration = 0.25
            midi_file.addNote(2, 0, pitch, time, duration, melody_vol)

    # 生成点缀音 (Embellishment)
    # M: Table[..., {n,1,Floor[st/4]}]
    embellishment_vol = 80
    for n in range(1, math.floor(num_measures / 4) + 1):
        # M: {32n+(i-1)/16, 32n+i/16} -> start = 32n + (i-1)/16
        for i in range(len(pa)):
            notes_to_play = pa[i]
            pitches = [note_to_midi_pitch(note) for note in notes_to_play]

            # Mathematica 播放的是一个和弦，但时间非常短，形成琶音效果
            # 我们在这里也把它作为一个和弦来添加
            time = 32 * n + (i - 1) / 16.0
            duration = 1 / 16.0
            for pitch in pitches:
                midi_file.addNote(3, 0, pitch, time, duration, embellishment_vol)

    # 4. 写入文件
    with open(output_filename, "wb") as output_file:
        midi_file.writeFile(output_file)
    print(f"Successfully wrote MIDI file to {output_filename}")


# ==============================================================================
# 4. 主程序执行 (翻译自 In[13])
# ==============================================================================

if __name__ == "__main__":
    # 使用 numpy 获取高精度常量
    pi = np.pi
    e = np.e
    sqrt2 = np.sqrt(2)

    num_measures = 8  # Mathematica code uses st=8

    # 生成基于 Pi 的音乐
    gen_music(pi, num_measures, "pi.mid")

    # 生成基于 E 的音乐
    gen_music(e, num_measures, "e.mid")

    # 生成基于 Sqrt(2) 的音乐
    gen_music(sqrt2, num_measures, "sqrt2.mid")
