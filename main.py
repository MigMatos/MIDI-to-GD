import tkinter as tk
from tkinter import filedialog
from mido import MidiFile
from zlib import compress
from base64 import urlsafe_b64encode

def midi_to_gmd(midi_file_path, output_file_path):
    print("Loading MIDI...")
    midi = MidiFile(midi_file_path)
    lines = []
    time_per_tick = 600 / midi.ticks_per_beat
    initial_y_pos = 1005
    big_note_y = 0
    note_start_times = {}

    print("Generating objects...")
    for track in midi.tracks:
        current_time = 0
        for msg in track:
            if msg.type == 'note_on' and msg.velocity > 0:
                note_start_times[msg.note] = current_time
            elif msg.type == 'note_off' or (msg.type == 'note_on' and msg.velocity == 0):
                start_time = note_start_times.get(msg.note, current_time)
                duration = current_time - start_time
                scaleX, scaleY = 0.25, max(msg.time * 0.045, 0.1)
                xPos = 4 + (msg.note * 7.5)
                yPos = initial_y_pos + (start_time * time_per_tick) + ((30 * scaleY - 30) / 2)
                big_note_y = max(big_note_y, yPos)
                colorChannel = (msg.channel - 1) % 12 + 1
                soundChannel = msg.channel
                line = (f"1,890,2,{yPos:.2f},3,{xPos},57,0,21,{colorChannel},32,1.0,155,1,128,{scaleY:.2f},129,{scaleX:.2f},"
                        f"24,{soundChannel},25,{soundChannel};")
                lines.append(line)
            current_time += msg.time

    lines.append("1,899,2,-15,3,-15,155,1,36,1,7,48,8,48,9,48,10,0,35,1,23,1000;")
    colors = [
        (51, 102, 255), (255, 126, 51), (51, 255, 102), (255, 51, 129),
        (51, 255, 255), (228, 51, 255), (153, 255, 51), (75, 51, 255),
        (255, 204, 51), (51, 180, 255), (255, 51, 51), (51, 255, 177),
        (255, 51, 204), (78, 255, 51), (153, 51, 255), (231, 255, 51)
    ]
    lines.extend([f"1,899,2,-15,3,{(-15 * (i + 1)):.2f},7,{r},8,{g},9,{b},23,{i};" for i, (r, g, b) in enumerate(colors, start=1)])

    lvlstr = '\n'.join(lines)

    with open("var.txt", "r") as v:
        lvlstr = v.read() + lvlstr

    compressed_lvlstr = compress(lvlstr.encode())
    encoded_lvlstr = urlsafe_b64encode(compressed_lvlstr).decode()

    strin = '<?xml version="1.0"?><plist version="1.0" gjver="2.0"><dict><k>kCEK</k><i>4</i><k>k2</k><s>test</s><k>k4</k><s>'
    strlast = "</s><k>k5</k><s>ObeyGDBot</s><k>k101</k><s>0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0</s><k>k13</k><t /><k>k21</k><i>2</i><k>k16</k><i>1</i><k>k80</k><i>2</i><k>k50</k><i>45</i><k>k47</k><t /><k>kI1</k><r>0</r><k>kI2</k><r>156</r><k>kI3</k><r>1</r><k>kI6</k><d><k>0</k><s>0</s><k>1</k><s>0</s><k>2</k><s>0</s><k>3</k><s>0</s><k>4</k><s>0</s><k>5</k><s>0</s><k>6</k><s>0</s><k>7</k><s>0</s><k>8</k><s>0</s><k>9</k><s>0</s><k>10</k><s>0</s><k>11</k><s>0</s><k>12</k><s>0</s><k>13</k><s>0</s></d></dict></plist>"

    final = strin + encoded_lvlstr + strlast

    with open(output_file_path, 'wb') as fn:
        fn.write(final.encode())

    print("Finished")

def select_midi_file():
    root = tk.Tk()
    root.withdraw()
    file_path = filedialog.askopenfilename(filetypes=[("MIDI Files", "*.mid;*.midi")])
    return file_path

def select_output_location():
    root = tk.Tk()
    root.withdraw()
    file_path = filedialog.asksaveasfilename(defaultextension=".gmd", filetypes=[("GMD Files", "*.gmd")])
    return file_path

if __name__ == "__main__":
    midi_file_path = select_midi_file()
    if midi_file_path:
        output_file_path = select_output_location()
        if output_file_path:
            midi_to_gmd(midi_file_path, output_file_path)
        else:
            print("No output file selected.")
    else:
        print("No MIDI file selected.")
