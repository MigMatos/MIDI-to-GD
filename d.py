import base64
import zlib
from base64 import decode, urlsafe_b64decode
import tkinter as tk
from tkinter import filedialog,simpledialog,messagebox

def decode_level(level_data: str, is_official_level = False) -> str:
    if is_official_level:
        level_data = 'H4sIAAAAAAAAA' + level_data
    base64_decoded = base64.urlsafe_b64decode(level_data.encode())

    decompressed = zlib.decompress(base64_decoded, 15 | 32)
    return decompressed.decode()


def select_midi_file():
    root = tk.Tk()
    root.withdraw()
    file_path = filedialog.askopenfilename(filetypes=[("MIDI Files", "*.gmd;*.gmd2")])
    return file_path

# print(decode_level(data))

# data = decode_level(data)

with open("4284013.keyed", 'wb') as fn:
    path_rute = select_midi_file()
    with open(path_rute, "r") as v:
        data = v.read()
    index_int = data.find("<k>k4</k><s>") + len("<k>k4</k><s>")
    final_int = data[index_int:].find("</s>")

    data = decode_level(str(data[index_int:index_int+final_int]),False)
    fn.write(data.encode())

