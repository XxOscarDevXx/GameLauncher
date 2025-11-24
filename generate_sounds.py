import wave
import math
import struct
import random

def generate_tone(filename, frequency=440, duration=0.1, volume=0.5, type="sine"):
    sample_rate = 44100
    n_samples = int(sample_rate * duration)
    
    with wave.open(filename, 'w') as wav_file:
        wav_file.setnchannels(1)
        wav_file.setsampwidth(2)
        wav_file.setframerate(sample_rate)
        
        for i in range(n_samples):
            t = float(i) / sample_rate
            if type == "sine":
                value = math.sin(2.0 * math.pi * frequency * t)
            elif type == "square":
                value = 1.0 if math.sin(2.0 * math.pi * frequency * t) > 0 else -1.0
            elif type == "noise":
                value = random.uniform(-1, 1)
            
            # Apply envelope (fade out)
            envelope = 1.0 - (i / n_samples)
            
            data = int(value * volume * envelope * 32767.0)
            wav_file.writeframes(struct.pack('<h', data))

if __name__ == "__main__":
    generate_tone("sounds/hover.wav", frequency=600, duration=0.05, volume=0.2)
    generate_tone("sounds/click.wav", frequency=1000, duration=0.1, volume=0.3)
    generate_tone("sounds/launch.wav", frequency=400, duration=0.5, volume=0.5, type="square")
    generate_tone("sounds/back.wav", frequency=300, duration=0.1, volume=0.3)
    print("Sounds generated.")
