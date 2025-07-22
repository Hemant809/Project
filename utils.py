import numpy as np
from scipy import signal

def generate_modulated_signal(mod_type, msg_freq, msg_amp,
                              carrier_freq, carrier_amp,
                              msg_waveform, carrier_waveform,
                              digital_msg):
    duration = 1
    sampling_rate = 1000
    t = np.linspace(0, duration, int(duration * sampling_rate))

    # Analog message
    if msg_waveform == "sine":
        message = msg_amp * np.sin(2 * np.pi * msg_freq * t)
    else:
        message = msg_amp * np.cos(2 * np.pi * msg_freq * t)

    # Carrier signal
    if carrier_waveform == "sine":
        carrier = carrier_amp * np.sin(2 * np.pi * carrier_freq * t)
    else:
        carrier = carrier_amp * np.cos(2 * np.pi * carrier_freq * t)

    # Default modulated wave
    wave = carrier
    # mod_index = 0

    if mod_type == "AM":
        wave = (1 + message / carrier_amp) * carrier
        mod_index = msg_amp / carrier_amp

    elif mod_type == "FM":
        kf = 5
        wave = carrier_amp * np.sin(2 * np.pi * carrier_freq * t + kf * message)
        mod_index = kf * msg_amp

    elif mod_type == "PM":
        kp = 5
        wave = carrier_amp * np.sin(2 * np.pi * carrier_freq * t + kp * message)
        mod_index = kp * msg_amp
        
    elif mod_type == "DSBSC":
        wave = message * carrier
        mod_index = msg_amp / carrier_amp

    elif mod_type == "SSB":
        hilbert_msg = signal.hilbert(message)
        ssb_signal = np.real(hilbert_msg * np.exp(1j * 2 * np.pi * carrier_freq * t))
        wave = ssb_signal
        mod_index = msg_amp / carrier_amp

    elif mod_type in ["ASK", "FSK", "QPSK", "BPSK"]:
        bits = [int(b) for b in str(digital_msg) if b in "01"]
        bit_duration = len(t) // len(bits)
        binary_wave = np.repeat(bits, bit_duration)

        if len(binary_wave) < len(t):
            binary_wave = np.pad(binary_wave, (0, len(t) - len(binary_wave)), mode='constant')

        if mod_type == "ASK":
            wave = binary_wave * carrier
            mod_index = (carrier_amp - 0) / carrier_amp

        elif mod_type == "FSK":
            freq0 = carrier_freq - 10
            freq1 = carrier_freq + 10
            wave = np.where(binary_wave,
                            carrier_amp * np.sin(2 * np.pi * freq1 * t),
                            carrier_amp * np.sin(2 * np.pi * freq0 * t))
            bit_rate = 1 / (t[1] - t[0]) / bit_duration 
            mod_index = (freq1 - freq0) / bit_rate

        elif mod_type == "BPSK":
            wave = carrier_amp * np.sin(2 * np.pi * carrier_freq * t + np.pi * (1 - 2 * np.array(binary_wave)))
            mod_index = np.pi 

        message = binary_wave
        # mod_index = 0

    return t, message, carrier, wave, mod_index
