import numpy as np
from scipy import signal

def generate_modulated_signal(mod_type, msg_freq, msg_amp,
                              carrier_freq, carrier_amp,
                              msg_waveform, carrier_waveform,
                              digital_msg):

    # Clamp values to reasonable ranges
    msg_freq = max(1, min(msg_freq, 100))         # Hz
    msg_amp = max(0.1, min(msg_amp, 10))          # amplitude
    carrier_freq = max(50, min(carrier_freq, 500))# Hz
    carrier_amp = max(0.1, min(carrier_amp, 10))  # amplitude

    # Time vector
    duration = 1
    sampling_rate = 1000
    t = np.linspace(0, duration, int(duration * sampling_rate))

    # Message signal
    if msg_waveform == "sine":
        message = msg_amp * np.sin(2 * np.pi * msg_freq * t)
    else:
        message = msg_amp * np.cos(2 * np.pi * msg_freq * t)

    # Carrier signal
    if carrier_waveform == "sine":
        carrier = carrier_amp * np.sin(2 * np.pi * carrier_freq * t)
    else:
        carrier = carrier_amp * np.cos(2 * np.pi * carrier_freq * t)

    wave = carrier
    mod_index = 0

    # ========================= ANALOG MODULATION =========================
    if mod_type == "AM":
        wave = (1 + message / carrier_amp) * carrier
        mod_index = msg_amp / carrier_amp

    elif mod_type == "FM":
        kf = 5
        beta = kf * msg_amp / msg_freq
        wave = carrier_amp * np.sin(2 * np.pi * carrier_freq * t +
                                    beta * np.sin(2 * np.pi * msg_freq * t))
        mod_index = beta

    elif mod_type == "PM":
        kp = 5
        wave = carrier_amp * np.sin(2 * np.pi * carrier_freq * t +
                                    kp * (message / msg_amp))
        mod_index = kp

    elif mod_type == "DSBSC":
        wave = message * carrier
        mod_index = msg_amp / carrier_amp

    elif mod_type == "SSB":
        m_hat = np.imag(signal.hilbert(message))
        wave = message * np.cos(2 * np.pi * carrier_freq * t) - \
               m_hat * np.sin(2 * np.pi * carrier_freq * t)
        mod_index = msg_amp / carrier_amp

    # ========================= DIGITAL MODULATION =========================
    elif mod_type in ["ASK", "FSK", "BPSK", "QPSK"]:
        # Convert string bits to list
        bits = [int(b) for b in str(digital_msg) if b in "01"]
        if not bits:
            bits = [0, 1, 0, 1]  # Default pattern if empty

        # ASK, FSK, BPSK use single bits per symbol
        if mod_type != "QPSK":
            bit_duration = len(t) // len(bits)
            binary_wave = np.repeat(bits, bit_duration)
            binary_wave = np.pad(binary_wave, (0, len(t) - len(binary_wave)), mode='constant')

        if mod_type == "ASK":
            wave = binary_wave * carrier
            message = binary_wave
            mod_index = 1

        elif mod_type == "FSK":
            freq0 = carrier_freq - 10
            freq1 = carrier_freq + 10
            wave = np.where(binary_wave,
                            carrier_amp * np.sin(2 * np.pi * freq1 * t),
                            carrier_amp * np.sin(2 * np.pi * freq0 * t))
            message = binary_wave
            bit_rate = sampling_rate / bit_duration
            mod_index = (freq1 - freq0) / (2 * bit_rate)

        elif mod_type == "BPSK":
            wave = carrier_amp * np.cos(2 * np.pi * carrier_freq * t +
                                        np.pi * binary_wave)
            message = binary_wave
            mod_index = np.pi

        elif mod_type == "QPSK":
            # Ensure even number of bits
            if len(bits) % 2 != 0:
                bits.append(0)

            I_bits = bits[0::2]
            Q_bits = bits[1::2]

            # Map bits to +1/-1
            I_symbols = 2*np.array(I_bits) - 1
            Q_symbols = 2*np.array(Q_bits) - 1

            samples_per_symbol = len(t) // len(I_symbols)

            I_wave = np.repeat(I_symbols, samples_per_symbol)
            Q_wave = np.repeat(Q_symbols, samples_per_symbol)

            I_wave = np.pad(I_wave, (0, len(t) - len(I_wave)), mode='constant')
            Q_wave = np.pad(Q_wave, (0, len(t) - len(Q_wave)), mode='constant')

            # QPSK modulation
            wave = carrier_amp * (I_wave * np.cos(2*np.pi*carrier_freq*t) -
                                  Q_wave * np.sin(2*np.pi*carrier_freq*t))

            message = I_wave  # For plotting baseband
            mod_index = np.pi / 2

    return t, message, carrier, wave, mod_index
