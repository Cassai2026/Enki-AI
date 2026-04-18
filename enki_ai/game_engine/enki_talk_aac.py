import os
import time

class EnkiSovereignTalk:
    def __init__(self):
        self.dwell_threshold = 1.5
        self.vocab = {"HIGH": {"phrase": "Everything is in flow."}, "MID": {"phrase": "I need a break."}, "LOW": {"phrase": "Assistance required."}}

    def execute_comm(self, zone):
        print(f"[HUD] EXECUTING {zone}")
        os.system(f'PowerShell -Command "Add-Type –AssemblyName System.Speech; (New-Object System.Speech.Synthesis.SpeechSynthesizer).Speak(\'{self.vocab[zone]["phrase"]}\')"')
