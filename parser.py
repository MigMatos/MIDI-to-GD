from mido import MidiFile, MidiTrack, Message
import tkinter as tk
from tkinter import filedialog,simpledialog,messagebox



def dividir_midi_por_tiempo(archivo_midi, intervalo_segundos, salida_prefijo):
    midi = MidiFile(archivo_midi)
    ticks_por_negra = midi.ticks_per_beat
    tempo = 500000  # Tempo por defecto (120 BPM)

    # Encontrar el tempo real (si existe un evento 'set_tempo')
    for track in midi.tracks:
        for msg in track:
            if msg.type == 'set_tempo':
                tempo = msg.tempo
                break

    # Calcular el número de ticks por intervalo
    ticks_por_segundo = ticks_por_negra * (1_000_000 / tempo)
    ticks_por_intervalo = int(intervalo_segundos * ticks_por_segundo)

    # Crear las partes del MIDI
    partes = []
    tiempo_acumulado = 0
    tiempo_restante = 0

    while True:
        nueva_parte = MidiFile(ticks_per_beat=midi.ticks_per_beat)
        for original_track in midi.tracks:
            nueva_track = MidiTrack()
            temp_time = 0

            for msg in original_track:
                # Ajustar el tiempo acumulado dentro de los límites del intervalo
                if temp_time + msg.time > ticks_por_intervalo - tiempo_restante:
                    sobrante = (temp_time + msg.time) - (ticks_por_intervalo - tiempo_restante)
                    msg.time -= sobrante
                    nueva_track.append(msg)
                    tiempo_restante = sobrante
                    break
                else:
                    nueva_track.append(msg)
                    temp_time += msg.time

            # Ajustar el tiempo para la siguiente parte
            tiempo_restante = max(0, tiempo_restante)

            nueva_parte.tracks.append(nueva_track)

        partes.append(nueva_parte)

        # Salir del bucle si ya se procesó todo
        if tiempo_acumulado >= sum([sum(msg.time for msg in track) for track in midi.tracks]):
            break

    # Guardar las partes como archivos MIDI independientes
    for i, parte in enumerate(partes):
        parte.save(f"{salida_prefijo}_parte_{i + 1}.mid")
    print(f"Archivo dividido en {len(partes)} partes.")
#dividir_midi_por_tiempo("archivo.mid", 10, "salida")

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
        output_file_path = "merge/rdr"
        #output_file_path = select_output_location()
        if output_file_path:
            dividir_midi_por_tiempo(midi_file_path,30,output_file_path)
        else:
            print("No output file selected.")
    else:
        print("No MIDI file selected.")