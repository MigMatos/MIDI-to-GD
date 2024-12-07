from pretty_midi import PrettyMIDI
import os
from zlib import compress
from base64 import urlsafe_b64encode, b64encode
import tkinter as tk
from tkinter import filedialog

def gdNumber(number: float) -> str:
    return "{:.5e}".format(number) if number > 9999 else str(number)


def gdText(text: str) -> str:
    return b64encode(text.encode('utf-8')).decode('utf-8')


def gdtimeMod(tempo, init_tempo):
    return round(max(0.10, min(2.0, (tempo / init_tempo) * 1.0)), 2)


def midi_to_gmd(midi_file_path, output_file_path):
    filename = os.path.basename(midi_file_path)
    print("MIDI Selected:", filename)
    print("Loading MIDI with PrettyMIDI...")

    midi_data = PrettyMIDI(midi_file_path)
    seconds_midi = midi_data.get_end_time()

    print(f"Total length of MIDI: {seconds_midi:.2f} seconds")

    lines = []
    initial_y_pos = 1005
    total_notes = 0
    big_note_y = 0
    ticks_ingame_viewer = 600
    notes_active_per_second = [0] * (int(seconds_midi) + 1)
    i = 1
    print("Generating objects...")

    for instrument in midi_data.instruments:
        #print(instrument, i)
        if instrument.is_drum:
            continue  # Ignore drums
        i+=1
        
        for note in instrument.notes:
            
            total_notes += 1
            #print(total_notes)
            start_time = note.start
            duration = note.end - note.start
            for second in range(int(start_time), int(note.end) + 1):
                if second < len(notes_active_per_second):notes_active_per_second[second] += 1
            scaleX, scaleY = 0.25, max(duration*20, 0.05)

            # view inverted
            xPos = 960 - (note.pitch * 7.5)
            yPos = initial_y_pos + (start_time * ticks_ingame_viewer) + ((30 * scaleY - 30) / 2)
            
            # view settings in channels
            big_note_y = max(big_note_y, yPos)
            colorChannel = (i % 15) + 1

            line = (f"1,890,2,{yPos:.2f},3,{xPos:.2f},57,0,21,{colorChannel},32,1.0,155,1,128,{scaleY:.2f},129,{scaleX:.2f},"
                    f"24,{i},25,{i};")
            lines.append(line)

    ## Notes counter
    print("Adding counter....")
    #print(notes_active_per_second, sum(notes_active_per_second[1:]))
    for second, count in enumerate(notes_active_per_second):
        xpos_counter = (((big_note_y-initial_y_pos) / seconds_midi) * second) +  initial_y_pos
        ## Counter notes
        lines.append(f"1,1817,2,{xpos_counter:.2f},3,527.25,155,1,11,1,36,1,80,3,77,{int(count)},449,1;1,1916,2,-45,3,-195,155,1,36,1,85,2;")

    print("Adding tempo changes...")
    tempos = midi_data.get_tempo_changes()
    init_tempo = tempos[1][0] if tempos[1] else 120  # default BPM
    for time, tempo in zip(*tempos):
        posX = initial_y_pos + (time * ticks_ingame_viewer)
        timeMod = gdtimeMod(tempo, init_tempo)
        lines.append(f"1,1935,2,{posX:.2f},3,527.25,155,1,13,1,36,1,120,{timeMod},11,1;")

    # Total notes:
    lines.append(f"1,914,2,213.316,3,1914.82,57,3,155,4,21,25,128,0.25,129,0.25,31,{gdText('Total Notes: {}'.format(total_notes))};")

    # BG Color
    lines.append("1,899,2,-15,3,-15,155,1,36,1,7,48,8,48,9,48,10,0,35,1,23,1000;")

    # Move (LEGACY)
    lines.append(f"1,901,2,12.5,3,-73.75,155,1,36,1,51,1,57,10,28,{int(initial_y_pos + 30)},29,0,10,1.3,30,0,85,2;")

    # Timewarp (LEGACY)
    lines.append(f"1,1616,2,{initial_y_pos},3,527.25,51,10,580,0,11,1;")

    ## Text MIDI Name
    lines.append(f"1,914,2,213.316,3,1866.82,57,3,155,4,21,25,128,0.25,129,0.25,31,{gdText(filename)};")

    # Move to sync with MIDI
    final = int(big_note_y)
    lines.append(f"1,901,2,{initial_y_pos},3,527.25,155,1,36,1,51,1,57,10,11,1,28,{final},29,0,10,{seconds_midi:.4f},30,0,85,2;")

    colors = [
        (51, 102, 255), (255, 126, 51), (51, 255, 102), (255, 51, 129),
        (51, 255, 255), (228, 51, 255), (153, 255, 51), (75, 51, 255),
        (255, 204, 51), (51, 180, 255), (255, 51, 51), (51, 255, 177),
        (255, 51, 204), (78, 255, 51), (153, 51, 255), (231, 255, 51)
    ]
    lines.extend([f"1,899,2,-15,3,{(-15 * (i + 1)):.2f},7,{r},8,{g},9,{b},23,{i};" for i, (r, g, b) in enumerate(colors, start=1)])

    # add lines
    lvlstr = '\n'.join(lines)

    with open("var.txt", "r") as v:
        lvlstr = v.read() + lvlstr
    with open("ui.txt", "r") as v:
        lvlstr = v.read() + lvlstr

    compressed_lvlstr = compress(lvlstr.encode())
    encoded_lvlstr = urlsafe_b64encode(compressed_lvlstr).decode()

    strin = '<?xml version="1.0"?><plist version="1.0" gjver="2.0"><dict><k>kCEK</k><i>4</i><k>k2</k><s>test</s><k>k4</k><s>'
    strlast = "</s><k>k5</k><s>ObeyGDBot</s><k>k101</k><s>0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0</s><k>k13</k><t /><k>k21</k><i>2</i><k>k16</k><i>1</i><k>k80</k><i>2</i><k>k50</k><i>45</i><k>k47</k><t /><k>kI1</k><r>0</r><k>kI2</k><r>156</r><k>kI3</k><r>1</r><k>kI6</k><d><k>0</k><s>0</s><k>1</k><s>0</s><k>2</k><s>0</s><k>3</k><s>0</s><k>4</k><s>0</s><k>5</k><s>0</s><k>6</k><s>0</s><k>7</k><s>0</s><k>8</k><s>0</s><k>9</k><s>0</s><k>10</k><s>0</s><k>11</k><s>0</s><k>12</k><s>0</s><k>13</k><s>0</s></d></dict></plist>"
    final = strin + encoded_lvlstr + strlast


    with open(output_file_path, 'wb') as fn:

        fn.write(final.encode())

    print(f"Level data saved to {output_file_path}")

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