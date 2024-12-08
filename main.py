import random
import shutil
from pretty_midi import PrettyMIDI
import os
from zlib import compress
from base64 import urlsafe_b64encode, b64encode
import tkinter as tk
from tkinter import filedialog,simpledialog,messagebox
import json

with open('notes.json', 'r') as file:
    notes_obj_key = json.load(file)

def get_obj_note(pitch, x, y, speed, volume):
    key_data = pitch - 37
    try:key_data = notes_obj_key[str(key_data)]
    except:return ""
    try:return str(key_data).format(round(float(x),4),round(float(y),4),int(speed),round(float(volume),2))
    except:return ""

def random_id_song():return random.randint(1000000, 5000000)

def copy_and_rename_midi(midi_file_path,new_filename):
    try:
        dest_folder = os.path.join(os.getenv('LOCALAPPDATA'), 'GeometryDash')
        if not os.path.exists(dest_folder):
            raise FileNotFoundError("Folder 'GeometryDash' not found")
        mp3_file_path = os.path.join(dest_folder, new_filename + ".mp3")
        shutil.copy(midi_file_path, mp3_file_path)
        print(f"MIDI File moved to Geometry Dash Folder: {mp3_file_path}")
    except FileNotFoundError:
        messagebox.showerror("Error", "Error finding the 'GeometryDash' folder")
    except Exception as e:
        messagebox.showerror("Error", str(e))


def gdNumber(number: float) -> str:
    return "{:.5e}".format(number) if number > 9999 else str(number)


def gdText(text: str) -> str:
    return b64encode(text.encode('utf-8')).decode('utf-8')


def gdtimeMod(tempo, init_tempo):
    return round(max(0.10, min(2.0, (tempo / init_tempo) * 1.0)), 2)

def scaleGDNotes(scale=40):return scale,(scale*30)

def midi_to_gmd(midi_file_path, output_file_path, midi_converter_mode = 0):
    filename = os.path.basename(midi_file_path)
    print("MIDI Selected:", filename)
    print("Loading MIDI with PrettyMIDI...")
    print(f"Converting mode: {midi_converter_mode}")
    midi_data = PrettyMIDI(midi_file_path)
    seconds_midi = midi_data.get_end_time()
    rel_mid = midi_data.resolution # f

    lines = []
    initial_y_pos = 1005
    total_notes = 0
    big_note_y = 0
    view_notes_scale, ticks_ingame_viewer = scaleGDNotes(scale=30)
    notes_active_per_second = [0] * (int(seconds_midi) + 1)
    i = 1
    end_time_midi = 0
    last_note_time = 0
    
    print(view_notes_scale, ticks_ingame_viewer)

    print("Generating objects...")

    for instrument in midi_data.instruments:
        #print(instrument, i)
        if instrument.is_drum:
            continue  # Ignore drums
        i+=1
        end_time_midi = max(end_time_midi, last_note_time)
        
        for note in instrument.notes:

            last_note_time = note.end
            total_notes += 1
            start_time = note.start
            duration = note.end - note.start
            for second in range(int(start_time), int(note.end) + 1):
                if second < len(notes_active_per_second):notes_active_per_second[second] += 1
            scaleX, scaleY = 0.25, max(duration*view_notes_scale, 0.05)
            
            # view inverted
            xPos = 960 - (note.pitch * 7.5)
            yPos = initial_y_pos + (start_time * ticks_ingame_viewer) + ((30 * scaleY - 30) / 2)
            
            # view settings in channels
            big_note_y = max(big_note_y, yPos)
            colorChannel = (i % 15) + 1

            if(midi_converter_mode in {0}):
                obj_note = get_obj_note(note.pitch, yPos, 527.25, (duration * (note.velocity*0.01)), (note.velocity*0.01))
                lines.append(obj_note)
            elif (midi_converter_mode in {1,2}):
                lines.append(f"1,890,2,{yPos:.2f},3,{xPos:.2f},57,0,21,{colorChannel},32,1.0,155,1,128,{scaleY:.2f},129,{scaleX:.2f},24,{i},25,{i};")
            
    print(f"Total length of MIDI: {end_time_midi:.2f} seconds")
    print(f"Total length level: {big_note_y}")
    ## Notes counter
    print("Adding counter....")
    #print(notes_active_per_second, sum(notes_active_per_second[1:]))
    for second, count_notes in enumerate(notes_active_per_second):
        xpos_counter = (((big_note_y-initial_y_pos) / end_time_midi) * (second+1)) +  initial_y_pos
        ## Counter notes
        if(count_notes == 0):continue
        lines.append(f"1,1817,2,{xpos_counter:.2f},3,527.25,155,1,11,1,36,1,80,3,77,{int(count_notes)},449,1;")
        lines.append(f"1,1817,2,{xpos_counter:.2f},3,525,155,1,11,1,36,1,80,4,77,{int(count_notes)},139,1,449,1;")

    print("Adding tempo changes...")
    try:
        tempos = midi_data.get_tempo_changes()
        init_tempo = tempos[1][0] if tempos[1] else 120  # default BPM
        for time, tempo in zip(*tempos):
            posX = initial_y_pos + (time * ticks_ingame_viewer)
            timeMod = gdtimeMod(tempo, init_tempo)
            lines.append(f"1,1935,2,{posX:.2f},3,527.25,155,1,13,1,36,1,120,{timeMod},11,1;")
    except:pass

    # Total notes:
    lines.append(f"1,914,2,213.316,3,1936.82,57,3,155,4,21,25,128,0.25,129,0.25,31,{gdText('Total Notes: {}'.format(total_notes))};")

    # BG Color
    lines.append("1,899,2,-15,3,-15,155,1,36,1,7,48,8,48,9,48,10,0,35,1,23,1000;")

    # Move (LEGACY)
    lines.append(f"1,901,2,12.5,3,-73.75,155,1,36,1,51,1,57,10,28,{int(initial_y_pos + 30)},29,0,10,1.3,30,0,85,2;")

    # Timewarp (LEGACY)
    lines.append(f"1,1616,2,{initial_y_pos},3,527.25,51,10,580,0,11,1;")

    ## Text MIDI Name
    StringXPOS = 213.316 - ((5.5 * len(filename) - 5.5) / 2)
    lines.append(f"1,914,2,{StringXPOS:.4f},3,1866.82,57,3,155,4,21,25,128,0.25,129,0.25,31,{gdText(filename)};")

    # Move to sync with MIDI
    final = int(big_note_y)
    lines.append(f"1,901,2,{initial_y_pos},3,527.25,155,1,36,1,51,1,57,10,11,1,28,{final},29,0,10,{end_time_midi:.4f},30,0,85,2;")

    # End MIDI
    #lines.append(f"1,1616,2,{big_note_y},3,527.25,51,5,580,0,11,1;") #Stop trigger
    lines.append("1,3614,2,-44.5,3,1748.75,57,5,155,1,36,1,80,2,468,1,470,1,62,1;") #Timerchecker
    lines.append(f"1,3614,2,-44.5,3,1728.75,57,5,155,1,36,1,80,1,473,{end_time_midi:.2f},474,1,468,1,469,1,470,1,62,1;") #Timestopped
    lines.append(f"1,1268,2,{initial_y_pos},3,528.75,51,5,11,1;") #Spawn trigger

    # Song triggers
    id_song = random_id_song()
    lines.append(f"1,1934,2,1005.5,3,488.75,155,1,129,4,11,1,13,1,36,1,392,{id_song},406,1,421,1,422,0.5,10,0.5;")
    lines.append(f"1,1934,2,-5.5,3,488.75,155,1,129,1,13,1,36,1,392,1,406,0.0,421,1,422,0.5,10,0.5;") #init

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

    strin = f'<?xml version="1.0"?><plist version="1.0" gjver="2.0"><dict><k>kCEK</k><i>4</i><k>k18</k><i>10</i><k>k23</k><i>5</i><k>k2</k><s>{str(filename)[:30]}</s><k>k4</k><s>'
    strlast = "</s><k>k5</k><s>ObeyGDBot</s><k>k101</k><s>0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0</s><k>k11</k><i>57</i><k>k13</k><t /><k>k21</k><i>2</i><k>k16</k><i>1</i><k>k80</k><i>673</i><k>k27</k><i>57</i><k>k50</k><i>45</i><k>k47</k><t /><k>k48</k><i>26</i><k>k104</k><s>131313</s><k>kI1</k><r>206.715</r><k>kI2</k><r>243.573</r><k>kI3</k><r>0.3</r><k>kI4</k><i>5</i><k>kI5</k><i>12</i><k>kI7</k><i>-1</i><k>kI6</k><d><k>0</k><s>0</s><k>1</k><s>0</s><k>2</k><s>0</s><k>3</k><s>0</s><k>4</k><s>0</s><k>5</k><s>3</s><k>6</k><s>0</s><k>7</k><s>0</s><k>8</k><s>0</s><k>9</k><s>0</s><k>10</k><s>0</s><k>11</k><s>0</s><k>12</k><s>5</s><k>13</k><s>0</s></d></dict></plist>"
    final = strin + encoded_lvlstr + strlast

    if(midi_converter_mode == 2):copy_and_rename_midi(midi_file_path,str(id_song))


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

def select_mode():
    selected_mode = 0
    def on_button_click(selection):
        nonlocal selected_mode
        selected_mode = selection
        root.quit()
    root = tk.Tk()
    root.title("MIDI TO GD")

    message = (
        "The level will only be playable in platformer mode (you'll need to change it manually).\n\n"
        "If you experience desynchronization, you'll need to manually adjust the move trigger time to match the MIDI's duration (sometimes the MIDI duration is detected incorrectly)."
    )
    label = tk.Label(root, text=message, wraplength=400, justify="left")
    label.pack(pady=10)

    button_audio = tk.Button(root, text="Only Audio for Mobiles [WIP] (BROKEN)", command=lambda: on_button_click(0))
    button_visual = tk.Button(root, text="Only Visual", command=lambda: on_button_click(1))
    button_both = tk.Button(root, text="Audio + Visual (PC ONLY) [Not recommended for big MIDIs]", command=lambda: on_button_click(2))
    button_audio.pack(pady=10)
    button_visual.pack(pady=10)
    button_both.pack(pady=10)
    root.mainloop()
    return selected_mode



if __name__ == "__main__":
    midi_file_path = select_midi_file()
    if midi_file_path:
        output_file_path = select_output_location()
        if output_file_path:
            midi_converter_mode = select_mode()
            midi_to_gmd(midi_file_path, output_file_path, midi_converter_mode)
        else:
            print("No output file selected.")
    else:
        print("No MIDI file selected.")