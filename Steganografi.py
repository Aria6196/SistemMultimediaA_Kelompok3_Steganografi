import streamlit as st
import numpy as np
import cv2
from PIL import Image
import io
import os
import sys
os.environ["PYTHONUTF8"] = "1"
sys.stdin.reconfigure(encoding='utf-8')
sys.stdout.reconfigure(encoding='utf-8')
from typing import Tuple, Optional

def embed_message(image: np.ndarray, message: str) -> np.ndarray:
    """Sisipkan pesan dengan DCT lebih robust"""
    ycrcb = cv2.cvtColor(image, cv2.COLOR_RGB2YCrCb)
    y = ycrcb[:, :, 0].astype(np.float32)
    
    # Tambah checksum dan end marker
    message = f"{message}###{len(message)}" 
    bits = ''.join([format(ord(c), '08b') for c in message])
    
    h, w = y.shape
    bit_idx = 0
    
    for i in range(0, h-7, 8):
        for j in range(0, w-7, 8):
            if bit_idx >= len(bits):
                break
                
            block = y[i:i+8, j:j+8]
            dct_block = cv2.dct(block)
            
            # Gunakan koefisien frekuensi lebih tinggi [5,3]
            bit = int(bits[bit_idx])
            dct_block[5,3] = 30.0 if bit else 10.0  # Jarak lebih besar
            
            y[i:i+8, j:j+8] = cv2.idct(dct_block)
            bit_idx += 1
    
    ycrcb[:, :, 0] = np.clip(y, 0, 255).astype(np.uint8)
    return cv2.cvtColor(ycrcb, cv2.COLOR_YCrCb2RGB)

def extract_message(image: np.ndarray) -> Optional[str]:
    """Ekstrak pesan dengan validasi checksum"""
    ycrcb = cv2.cvtColor(image, cv2.COLOR_RGB2YCrCb)
    y = ycrcb[:, :, 0].astype(np.float32)
    
    bits = []
    extracted = []
    h, w = y.shape
    
    for i in range(0, h-7, 8):
        for j in range(0, w-7, 8):
            block = y[i:i+8, j:j+8]
            dct_block = cv2.dct(block)
            
            # Ekstrak dengan threshold
            bit = 1 if dct_block[5,3] > 20.0 else 0
            bits.append(str(bit))
            
            # Coba decode setiap byte
            if len(bits) >= 8:
                byte = bits[:8]
                bits = bits[8:]
                try:
                    char = chr(int(''.join(byte), 2))
                    extracted.append(char)
                    
                    # Cek end marker dan checksum
                    msg_str = ''.join(extracted)
                    if '###' in msg_str:
                        parts = msg_str.split('###')
                        if len(parts) == 2:
                            msg, length = parts
                            if len(msg) == int(length):
                                return msg
                except:
                    continue
    return None

# Streamlit Interface
st.title("🖼️ DCT Image Steganography")

option = st.radio("Pilih mode:", ["🔐 Sisipkan Pesan", "🔓 Ekstrak Pesan"])

uploaded_file = st.file_uploader("Unggah gambar", type=['png', 'jpg', 'jpeg'])

if uploaded_file:
    image = Image.open(uploaded_file).convert('RGB')
    image_np = np.array(image)

    st.subheader("📷 Gambar Asli:")
    st.image(image_np, use_container_width=True)

    if option == "🔐 Sisipkan Pesan":
        message = st.text_input("Masukkan pesan untuk disisipkan:")
        if st.button("Sisipkan dan tampilkan hasil"):
            if message:
                encoded = embed_message(image_np.copy(), message)
                st.subheader("🧪 Gambar Setelah Disisipi:")
                st.image(encoded, use_container_width=True)

                # Simpan sebagai download
                is_success, buffer = cv2.imencode(".png", cv2.cvtColor(encoded, cv2.COLOR_RGB2BGR))
                if is_success:
                    st.download_button(
                        label="💾 Unduh Gambar Disisipi",
                        data=io.BytesIO(buffer.tobytes()),
                        file_name="encoded_image.png",
                        mime="image/png"
                    )
            else:
                st.warning("Mohon masukkan pesan terlebih dahulu.")

    elif option == "🔓 Ekstrak Pesan":
        if st.button("Ekstrak Pesan"):
            result = extract_message(image_np.copy())
            st.subheader("📄 Pesan Tersembunyi:")
            st.code(result if result else "(Tidak ditemukan pesan)")

