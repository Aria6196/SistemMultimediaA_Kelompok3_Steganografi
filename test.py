from Steganografi import embed_message, extract_message
import cv2

# Embed pesan
original_img = cv2.imread('armstrong.png')
secret_msg = "Pesan rahasia"
encoded_img = embed_message(original_img, secret_msg)

# Extract pesan
extracted_msg = extract_message(encoded_img)
print("Pesan yang diekstrak:", extracted_msg)

