import tkinter as tk
from tkinter import filedialog
from mido import MidiFile
from zlib import compress
from base64 import urlsafe_b64encode,b64encode
import os

def gdNumber(number:float) -> str:return "{:.5e}".format(number) if number > 9999 else str(number)
def gdText(text:str) -> str: return b64encode(text.encode('utf-8')).decode('utf-8')
def gdtimeMod(tempo, init_tempo):return round(max(0.10, min(2.0, (tempo / init_tempo) * 1.0)), 2)
def getTimeforMove(length_midi, ticks): return round(length_midi*ticks)



def midi_to_gmd(midi_file_path, output_file_path):
    filename = os.path.basename(midi_file_path)
    print("MIDI Selected: ", filename)
    print("Loading MIDI...")
    
    midi = MidiFile(midi_file_path)
    seconds_midi = midi.length

    print(midi.length)

    lines = []
    tempos = []
    ticks_ingame_viewer = 600
    time_per_tick = ticks_ingame_viewer / midi.ticks_per_beat
    ticks_per_beat_var = midi.ticks_per_beat

    print(time_per_tick)
    print(ticks_per_beat_var)

    initial_y_pos = 1005
    total_notes = 0
    big_note_y = 0
    note_start_times = {}
    total_ticks = 0
    start_time = 0
    init_tempo = 0
    start_time_tempo = 0
    notes = 0
    notes_in_seconds = [0] * int(midi.length)

    print("Generating objects...")
    for track in midi.tracks:
        track_ticks = 0
        current_time = 0


        for msg in track:
            track_ticks += msg.time
            if msg.type == 'note_on' or msg.type == 'note_off':total_notes += 1
            if msg.type == 'note_on' and msg.velocity > 0:
                note_start_times[msg.note] = current_time
            elif msg.type == 'note_off' or (msg.type == 'note_on' and msg.velocity == 0):
                start_time = note_start_times.get(msg.note, current_time)

                
                try:notes_in_seconds[int((start_time/ticks_per_beat_var)/2)] += 1
                except:print("Error asing notes x sec")
                duration = current_time - start_time
                scaleX, scaleY = 0.25, max(msg.time * 0.045, max((duration/time_per_tick), 0.05))
                xPos = (4 + (msg.note * -7.5)+960) #invert Notes view
                yPos = initial_y_pos + (start_time * time_per_tick) + ((30 * scaleY - 30) / 2)
                big_note_y = max(big_note_y, yPos)
                colorChannel = (msg.channel - 1) % 15 + 1
                soundChannel = msg.channel
                line = (f"1,890,2,{yPos:.2f},3,{xPos},57,0,21,{colorChannel},32,1.0,155,1,128,{scaleY:.2f},129,{scaleX:.2f},"
                        f"24,{soundChannel},25,{soundChannel};")
                lines.append(line)
            elif msg.type == 'set_tempo':
                bpm = 60_000_000 / (msg.tempo * ticks_per_beat_var)
                modTime = bpm * 10
                start_time_tempo+=msg.time 
                print("Tempo start:", start_time_tempo)
                posX = initial_y_pos + (start_time_tempo * time_per_tick)

                if(init_tempo == 0):
                    init_tempo = modTime
                    lines.append(f"1,1616,2,{posX},3,527.25,51,10,580,0,11,1;")
                    tempos.append(f"1,901,2,{posX},3,527.25,155,1,36,1,51,1,57,10,11,1,28,REPLACE_TXT,29,0,10,{seconds_midi:.4f},30,0,85,2;")
                print("Mod time:", modTime, " in X:", posX)
                print(start_time)

                ## Timewarp
                timeMod = gdtimeMod(modTime,init_tempo)
                lines.append(f"1,1935,2,{posX},3,527.25,155,1,13,1,36,1,120,{timeMod},11,1;")

                
            current_time += msg.time
        total_ticks += track_ticks


    for tempo in tempos:
        final = int(big_note_y+initial_y_pos)
        lines.append(tempo.replace("REPLACE_TXT", str( (final) ) ) )
    XSum = ((big_note_y-initial_y_pos) / seconds_midi)
    for pos, notes_count in enumerate(notes_in_seconds, start=1):
        xpos_counter = (XSum * pos) +  initial_y_pos
        ## Counter notes
        lines.append(f"1,1817,2,{xpos_counter:.2f},3,527.25,155,1,11,1,36,1,80,3,77,{int(notes_count)},449,1;1,1916,2,-45,3,-195,155,1,36,1,85,2;")
        
    ## Background Color
    lines.append("1,899,2,-15,3,-15,155,1,36,1,7,48,8,48,9,48,10,0,35,1,23,1000;")
    ## Move
    lines.append(f"1,901,2,12.5,3,-73.75,155,1,36,1,51,1,57,10,28,{str(int(initial_y_pos+30))},29,0,10,1.3,30,0,85,2;")
    ## Text MIDI Name
    lines.append(f"1,914,2,213.316,3,1866.82,57,3,155,4,21,25,128,0.25,129,0.25,31,{gdText(filename)};")
    ## Text Notes
    lines.append(f"1,914,2,213.316,3,1914.82,57,3,155,4,21,25,128,0.25,129,0.25,31,{gdText('Total Notes: {}'.format(int(total_notes/2)))};")



    colors = [
        (51, 102, 255), (255, 126, 51), (51, 255, 102), (255, 51, 129),
        (51, 255, 255), (228, 51, 255), (153, 255, 51), (75, 51, 255),
        (255, 204, 51), (51, 180, 255), (255, 51, 51), (51, 255, 177),
        (255, 51, 204), (78, 255, 51), (153, 51, 255), (231, 255, 51)
    ]
    lines.extend([f"1,899,2,-15,3,{(-15 * (i + 1)):.2f},7,{r},8,{g},9,{b},23,{i};" for i, (r, g, b) in enumerate(colors, start=1)])

    lvlstr = '\n'.join(lines)

    with open("var.txt", "r") as v:lvlstr = v.read() + lvlstr
    with open("ui.txt", "r") as v:lvlstr = v.read() + lvlstr

    compressed_lvlstr = compress(lvlstr.encode())
    encoded_lvlstr = urlsafe_b64encode(compressed_lvlstr).decode()

    strin = '<?xml version="1.0"?><plist version="1.0" gjver="2.0"><dict><k>kCEK</k><i>4</i><k>k2</k><s>test</s><k>k4</k><s>'
    strlast = "</s><k>k5</k><s>ObeyGDBot</s><k>k101</k><s>0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0</s><k>k13</k><t /><k>k21</k><i>2</i><k>k16</k><i>1</i><k>k80</k><i>2</i><k>k50</k><i>45</i><k>k47</k><t /><k>kI1</k><r>0</r><k>kI2</k><r>156</r><k>kI3</k><r>1</r><k>kI6</k><d><k>0</k><s>0</s><k>1</k><s>0</s><k>2</k><s>0</s><k>3</k><s>0</s><k>4</k><s>0</s><k>5</k><s>0</s><k>6</k><s>0</s><k>7</k><s>0</s><k>8</k><s>0</s><k>9</k><s>0</s><k>10</k><s>0</s><k>11</k><s>0</s><k>12</k><s>0</s><k>13</k><s>0</s></d></dict></plist>"

    final = strin + encoded_lvlstr + strlast

    with open(output_file_path, 'wb') as fn:
        fn.write(final.encode())

    print("X: ", big_note_y)
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
