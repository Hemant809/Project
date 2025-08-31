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
            # --- Prepare bits ---
            if len(bits) % 2 != 0:
                bits.append(0)

            # Gray mapping to 45°, 135°, 225°, 315° using normalized amplitudes (±1/√2)
            # 00 -> ( +,+ ), 01 -> ( -, + ), 11 -> ( -, - ), 10 -> ( +, - )
            sym_map = {
                (0, 0): ( 1/np.sqrt(2),  1/np.sqrt(2)),
                (0, 1): (-1/np.sqrt(2),  1/np.sqrt(2)),
                (1, 1): (-1/np.sqrt(2), -1/np.sqrt(2)),
                (1, 0): ( 1/np.sqrt(2), -1/np.sqrt(2)),
            }

            I_bits = bits[0::2]
            Q_bits = bits[1::2]
            n_syms = len(I_bits)
            samples_per_symbol = max(1, len(t) // n_syms)

            # Baseband I/Q step waveforms
            I_bb = np.zeros_like(t, dtype=float)
            Q_bb = np.zeros_like(t, dtype=float)

            for i_sym, (Ib, Qb) in enumerate(zip(I_bits, Q_bits)):
                Iamp, Qamp = sym_map[(Ib, Qb)]
                start_idx = i_sym * samples_per_symbol
                end_idx = min(len(t), start_idx + samples_per_symbol)
                I_bb[start_idx:end_idx] = Iamp
                Q_bb[start_idx:end_idx] = Qamp

            # Passband synthesis: s(t) = Ac [ I(t) cos(2πfct) - Q(t) sin(2πfct) ]
            cos_c = np.cos(2 * np.pi * carrier_freq * t)
            sin_c = np.sin(2 * np.pi * carrier_freq * t)
            wave = carrier_amp * (I_bb * cos_c - Q_bb * sin_c)

            # For plotting: message carries I(t) and Q(t) as columns
            message = np.column_stack([I_bb, Q_bb])
            mod_index = None

    return t, message, carrier, wave, mod_index
