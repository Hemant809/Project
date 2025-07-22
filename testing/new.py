import numpy as np
import matplotlib.pyplot as plt
import os

# Setup folder for saving plots
PLOTS_DIR = "static/plots"
os.makedirs(PLOTS_DIR, exist_ok=True)

def save_plot(x, y, title, filename):
    plt.figure(figsize=(8, 3))
    plt.plot(x, y)
    plt.title(title)
    plt.xlabel("Time (s)")
    plt.ylabel("Amplitude")
    plt.grid(True)
    plt.tight_layout()
    path = os.path.join(PLOTS_DIR, filename)
    plt.savefig(path)
    plt.close()
    print(f"Saved plot: {path}")

def generate_digital_modulation(mod_type, carrier_freq=100, carrier_amp=1, digital_message="1010"):
    fs = 1000  # samples per second
    bit_rate = 2  # bits per second (bit duration = 0.5 s)
    bit_duration = 1 / bit_rate
    samples_per_bit = int(fs * bit_duration)

    t_total = np.linspace(0, bit_duration * len(digital_message), samples_per_bit * len(digital_message), endpoint=False)
    modulated_signal = np.zeros_like(t_total)
    carrier_signal = np.zeros_like(t_total)
    message_signal = np.zeros_like(t_total)

    for i, bit_char in enumerate(digital_message):
        bit = int(bit_char)
        start = i * samples_per_bit
        end = start + samples_per_bit
        t_bit = np.linspace(0, bit_duration, samples_per_bit, endpoint=False)

        # Base carrier for this bit (used in message plot)
        carrier_signal[start:end] = carrier_amp * np.sin(2 * np.pi * carrier_freq * t_bit)

        # Message signal is just the bit value repeated
        message_signal[start:end] = bit

        if mod_type == "ASK":
            modulated_signal[start:end] = bit * carrier_amp * np.sin(2 * np.pi * carrier_freq * t_bit)
        elif mod_type == "FSK":
            freq0 = carrier_freq - 30
            freq1 = carrier_freq + 30
            freq = freq1 if bit == 1 else freq0
            modulated_signal[start:end] = carrier_amp * np.sin(2 * np.pi * freq * t_bit)
        elif mod_type == "PSK" or mod_type == "BPSK":
            phase = 0 if bit == 0 else np.pi
            modulated_signal[start:end] = carrier_amp * np.sin(2 * np.pi * carrier_freq * t_bit + phase)
        else:
            raise ValueError("Unsupported modulation type")

    save_plot(t_total, message_signal, "Digital Message Signal", f"{mod_type}_message.png")
    save_plot(t_total, carrier_signal, "Carrier Signal", f"{mod_type}_carrier.png")
    save_plot(t_total, modulated_signal, f"{mod_type} Modulated Signal", f"{mod_type}_modulated.png")

# Run all four modulations and save plots
for modulation in ["ASK", "FSK", "PSK", "BPSK"]:
    print(f"Generating {modulation} modulation plots...")
    generate_digital_modulation(modulation, carrier_freq=100, carrier_amp=1, digital_message="10101")
print("All modulation plots generated and saved.")
