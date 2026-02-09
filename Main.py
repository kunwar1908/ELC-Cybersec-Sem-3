import time
import numpy as np
import os
import matplotlib.pyplot as plt

# --- UTILITY FUNCTIONS ---

def save_file(filename, data):
    with open(filename, 'w') as f:
        f.write(str(data))

def load_file(filename):
    with open(filename, 'r') as f:
        return f.read().strip()

def char_to_num(char):
    return ord(char.upper()) - 65

def num_to_char(num):
    return chr((num % 26) + 65)

# --- 1. CAESAR CIPHER [cite: 24-46] ---

def caesar_encrypt(text, shift):
    result = ""
    for char in text:
        if char.isalpha():
            start = 65 if char.isupper() else 97
            result += chr((ord(char) - start + shift) % 26 + start)
        else:
            result += char
    return result

def caesar_decrypt(text, shift):
    return caesar_encrypt(text, -shift)

# --- 2. PLAYFAIR CIPHER [cite: 53-62] ---

def create_playfair_matrix(key):
    key = "".join(dict.fromkeys(key.upper().replace("J", "I") + "ABCDEFGHIKLMNOPQRSTUVWXYZ"))
    matrix = [list(key[i:i+5]) for i in range(0, 25, 5)]
    return matrix

def find_position(matrix, char):
    for r, row in enumerate(matrix):
        if char in row:
            return r, row.index(char)
    return None

def playfair_process(text, key, mode='encrypt'):
    matrix = create_playfair_matrix(key)
    text = text.upper().replace("J", "I").replace(" ", "")
    
    # Prepare text (add X padding)
    processed_text = ""
    i = 0
    while i < len(text):
        a = text[i]
        b = text[i+1] if i+1 < len(text) else 'X'
        if a == b:
            processed_text += a + 'X'
            i += 1
        else:
            processed_text += a + b
            i += 2
    if len(processed_text) % 2 != 0: processed_text += 'X'

    result = ""
    shift = 1 if mode == 'encrypt' else -1
    
    for i in range(0, len(processed_text), 2):
        pos1 = find_position(matrix, processed_text[i])
        pos2 = find_position(matrix, processed_text[i+1])
        if pos1 is None or pos2 is None:
            continue
        r1, c1 = pos1
        r2, c2 = pos2
        
        if r1 == r2: # Same row
            result += matrix[r1][(c1 + shift) % 5] + matrix[r2][(c2 + shift) % 5]
        elif c1 == c2: # Same column
            result += matrix[(r1 + shift) % 5][c1] + matrix[(r2 + shift) % 5][c2]
        else: # Rectangle
            result += matrix[r1][c2] + matrix[r2][c1]
            
    return result

# --- 3. HILL CIPHER [cite: 63-89] ---

def mod_inverse_matrix(matrix, modulus=26):
    # Calculate determinant
    det = int(np.round(np.linalg.det(matrix)))
    det_inv = pow(det, -1, modulus) # Modular inverse of determinant
    
    # Calculate adjugate matrix
    adjugate = np.zeros_like(matrix)
    for i in range(matrix.shape[0]):
        for j in range(matrix.shape[1]):
            sub_matrix = np.delete(np.delete(matrix, i, 0), j, 1)
            cofactor = ((-1) ** (i + j)) * int(np.round(np.linalg.det(sub_matrix)))
            adjugate[j, i] = cofactor # Transpose of cofactor matrix
            
    inv_matrix = (det_inv * adjugate) % modulus
    return inv_matrix

def hill_encrypt(text, key_matrix):
    text = text.upper().replace(" ", "")
    n = key_matrix.shape[0]
    
    # Pad text to fit matrix size
    while len(text) % n != 0:
        text += 'X'
        
    text_vector = [char_to_num(c) for c in text]
    text_matrix = np.array(text_vector).reshape(-1, n)
    
    cipher_matrix = (np.dot(text_matrix, key_matrix)) % 26
    
    return "".join(num_to_char(num) for row in cipher_matrix for num in row)

def hill_decrypt(cipher, key_matrix):
    try:
        inv_key = mod_inverse_matrix(key_matrix)
        n = key_matrix.shape[0]
        cipher_vector = [char_to_num(c) for c in cipher]
        cipher_matrix = np.array(cipher_vector).reshape(-1, n)
        
        plain_matrix = (np.dot(cipher_matrix, inv_key)) % 26
        return "".join(num_to_char(int(num)) for row in plain_matrix for num in row)
    except ValueError:
        return "Error: Key matrix is not invertible modulo 26."

# --- MAIN EXECUTION & TIMING  ---

def run_assignment():
    # 0. Setup Files
    source_path = "/home/preet/CyberSecELC/Text_To_Be_Encypted_f13bb925bd874f6408405c41b4c6ab30.txt"
    if not os.path.exists(source_path):
        raise FileNotFoundError(f"Input text file not found: {source_path}")
    plaintext = load_file(source_path)
    save_file("plaintext.txt", plaintext)
    
    # 1. Keys (Save/Load) 
    caesar_key = 3
    playfair_key = "MONARCHY"
    # Hill key from PDF example [cite: 76]
    hill_key = np.array([[6, 24, 1], [13, 16, 10], [20, 17, 15]]) 
    
    save_file("key_caesar.txt", caesar_key)
    save_file("key_playfair.txt", playfair_key)
    # Hill key is complex, saving as string representation for simplicity here
    save_file("key_hill.txt", str(hill_key.tolist())) 

    print(f"Original Text: {plaintext}\n")

    # --- MEASURE CAESAR ---
    start = time.perf_counter()
    c_enc = caesar_encrypt(plaintext, caesar_key)
    c_enc_time = (time.perf_counter() - start) * 1000 # ms
    
    start = time.perf_counter()
    c_dec = caesar_decrypt(c_enc, caesar_key)
    c_dec_time = (time.perf_counter() - start) * 1000

    print(f"Caesar Enc: {c_enc} | Time: {c_enc_time:.5f} ms")
    print(f"Caesar Dec: {c_dec} | Time: {c_dec_time:.5f} ms\n")

    # --- MEASURE PLAYFAIR ---
    start = time.perf_counter()
    p_enc = playfair_process(plaintext, playfair_key, 'encrypt')
    p_enc_time = (time.perf_counter() - start) * 1000

    start = time.perf_counter()
    p_dec = playfair_process(p_enc, playfair_key, 'decrypt')
    p_dec_time = (time.perf_counter() - start) * 1000

    print(f"Playfair Enc: {p_enc} | Time: {p_enc_time:.5f} ms")
    print(f"Playfair Dec: {p_dec} | Time: {p_dec_time:.5f} ms\n")

    # --- MEASURE HILL ---
    start = time.perf_counter()
    h_enc = hill_encrypt(plaintext, hill_key)
    h_enc_time = (time.perf_counter() - start) * 1000

    start = time.perf_counter()
    h_dec = hill_decrypt(h_enc, hill_key)
    h_dec_time = (time.perf_counter() - start) * 1000
    
    print(f"Hill Enc: {h_enc} | Time: {h_enc_time:.5f} ms")
    print(f"Hill Dec: {h_dec} | Time: {h_dec_time:.5f} ms")

    # Save outputs for submission
    save_file("cipher_caesar.txt", c_enc)
    save_file("cipher_playfair.txt", p_enc)
    save_file("cipher_hill.txt", h_enc)
    encrypted_bundle = (
        f"Caesar: {c_enc}\n"
        f"Playfair: {p_enc}\n"
        f"Hill: {h_enc}\n"
    )
    save_file("encrypted_text.txt", encrypted_bundle)

    # Plot timing comparison
    algorithms = ["Caesar", "Playfair", "Hill"]
    enc_times = [c_enc_time, p_enc_time, h_enc_time]
    dec_times = [c_dec_time, p_dec_time, h_dec_time]

    x = np.arange(len(algorithms))
    width = 0.35

    fig, ax = plt.subplots(figsize=(8, 4))
    ax.bar(x - width / 2, enc_times, width, label="Encrypt")
    ax.bar(x + width / 2, dec_times, width, label="Decrypt")
    ax.set_title("Cipher Timing (ms)")
    ax.set_ylabel("Time (ms)")
    ax.set_xticks(x)
    ax.set_xticklabels(algorithms)
    ax.legend()
    ax.grid(axis="y", linestyle="--", alpha=0.4)

    fig.tight_layout()
    fig.savefig("timing_comparison.png", dpi=150)
    plt.close(fig)

if __name__ == "__main__":
    run_assignment()