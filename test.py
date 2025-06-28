from Steganografi import embed_message, extract_message
import cv2
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from PIL import Image, ImageTk
import numpy as np
import os

class ImprovedStegoApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Steganografi DCT - Penyembunyian Pesan dalam Gambar")
        self.root.geometry("900x700")
        
        # Style configuration
        self.style = ttk.Style()
        self.style.configure('TButton', font=('Helvetica', 10), padding=5)
        self.style.configure('TFrame', background='#f0f0f0')
        
        # Variables
        self.original_image = None
        self.encoded_image = None
        self.message_var = tk.StringVar()
        
        # Main container
        self.main_frame = ttk.Frame(root)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Image display frame
        self.image_frame = ttk.Frame(self.main_frame)
        self.image_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # Original image
        self.original_label = ttk.Label(self.image_frame, text="Gambar Asli", anchor=tk.CENTER)
        self.original_label.grid(row=0, column=0, padx=5, pady=5)
        self.original_canvas = tk.Canvas(self.image_frame, width=400, height=300, bg='#e0e0e0')
        self.original_canvas.grid(row=1, column=0, padx=5, pady=5)
        
        # Encoded image
        self.encoded_label = ttk.Label(self.image_frame, text="Gambar Hasil", anchor=tk.CENTER)
        self.encoded_label.grid(row=0, column=1, padx=5, pady=5)
        self.encoded_canvas = tk.Canvas(self.image_frame, width=400, height=300, bg='#e0e0e0')
        self.encoded_canvas.grid(row=1, column=1, padx=5, pady=5)
        
        # Control frame
        self.control_frame = ttk.Frame(self.main_frame)
        self.control_frame.pack(fill=tk.X, pady=10)
        
        # Buttons
        ttk.Button(self.control_frame, text="📂 Buka Gambar", command=self.load_image).pack(side=tk.LEFT, padx=5)
        ttk.Button(self.control_frame, text="🔐 Sisipkan Pesan", command=self.show_embed_ui).pack(side=tk.LEFT, padx=5)
        ttk.Button(self.control_frame, text="🔓 Ekstrak Pesan", command=self.extract_message).pack(side=tk.LEFT, padx=5)
        ttk.Button(self.control_frame, text="💾 Simpan Gambar", command=self.save_image).pack(side=tk.LEFT, padx=5)
        
        # Embed UI
        self.embed_frame = ttk.Frame(self.main_frame)
        self.message_entry = ttk.Entry(self.embed_frame, textvariable=self.message_var, width=50)
        self.message_entry.pack(side=tk.LEFT, padx=5)
        ttk.Button(self.embed_frame, text="Proses", command=self.embed_message).pack(side=tk.LEFT, padx=5)
        
        # Result display
        self.result_frame = ttk.Frame(self.main_frame)
        self.result_text = tk.Text(self.result_frame, height=5, width=80, wrap=tk.WORD, 
                                 font=('Consolas', 10), bg='#f8f8f8', padx=5, pady=5)
        scrollbar = ttk.Scrollbar(self.result_frame, command=self.result_text.yview)
        self.result_text.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.result_text.pack(fill=tk.BOTH, expand=True)
        
        # Status bar
        self.status_var = tk.StringVar()
        self.status_var.set("Siap")
        self.status_bar = ttk.Label(self.main_frame, textvariable=self.status_var, 
                                  relief=tk.SUNKEN, anchor=tk.W)
        self.status_bar.pack(fill=tk.X, pady=(5,0))
        
        # Initialize UI state
        self.clear_ui()
    
    def clear_ui(self):
        """Reset UI elements"""
        self.embed_frame.pack_forget()
        self.result_frame.pack_forget()
        self.encoded_label.config(text="Gambar Hasil")
        self.message_var.set("")
        self.result_text.delete(1.0, tk.END)
    
    def load_image(self):
        """Load image file"""
        self.clear_ui()
        path = filedialog.askopenfilename(
            filetypes=[("Image files", "*.png;*.jpg;*.jpeg;*.bmp"), ("All files", "*.*")])
        
        if not path:
            return
            
        try:
            self.original_image = cv2.imread(path)
            if self.original_image is None:
                raise ValueError("Format gambar tidak didukung")
                
            self.original_image = cv2.cvtColor(self.original_image, cv2.COLOR_BGR2RGB)
            self.encoded_image = None
            self.show_image(self.original_image, self.original_canvas)
            self.encoded_canvas.delete("all")
            self.encoded_canvas.create_text(200, 150, text="Gambar hasil akan muncul di sini", 
                                          fill="gray", font=('Helvetica', 12))
            self.status_var.set(f"Gambar berhasil dimuat: {os.path.basename(path)}")
        except Exception as e:
            messagebox.showerror("Error", f"Gagal memuat gambar: {str(e)}")
            self.status_var.set("Gagal memuat gambar")
    
    def show_image(self, image, canvas):
        """Display image on canvas"""
        if image is None:
            return
            
        # Convert numpy array to PIL Image
        img_pil = Image.fromarray(image)
        
        # Calculate aspect ratio
        img_width, img_height = img_pil.size
        canvas_width = canvas.winfo_width()
        canvas_height = canvas.winfo_height()
        
        ratio = min(canvas_width/img_width, canvas_height/img_height)
        new_size = (int(img_width*ratio), int(img_height*ratio))
        img_pil = img_pil.resize(new_size, Image.LANCZOS)
        
        # Display on canvas
        self.tk_image = ImageTk.PhotoImage(img_pil)
        canvas.delete("all")
        canvas.create_image(canvas_width//2, canvas_height//2, 
                          anchor=tk.CENTER, image=self.tk_image)
    
    def show_embed_ui(self):
        """Show embed message UI"""
        if self.original_image is None:
            messagebox.showwarning("Peringatan", "Silakan buka gambar terlebih dahulu")
            return
            
        self.clear_ui()
        self.embed_frame.pack(pady=10)
        self.message_entry.focus()
        self.status_var.set("Masukkan pesan yang akan disisipkan")
    
    def embed_message(self):
        """Embed message into image"""
        message = self.message_var.get().strip()
        if not message:
            messagebox.showwarning("Peringatan", "Masukkan pesan yang akan disisipkan")
            return
            
        try:
            self.encoded_image = embed_message(self.original_image.copy(), message)
            self.show_image(self.encoded_image, self.encoded_canvas)
            self.status_var.set("Pesan berhasil disisipkan ke dalam gambar")
            self.encoded_label.config(text="Gambar Hasil (Dengan Pesan Tersembunyi)")
        except Exception as e:
            messagebox.showerror("Error", f"Gagal menyisipkan pesan: {str(e)}")
            self.status_var.set("Gagal menyisipkan pesan")
    
    def extract_message(self):
        """Extract hidden message from image"""
        if self.original_image is None:
            messagebox.showwarning("Peringatan", "Silakan buka gambar terlebih dahulu")
            return
            
        self.clear_ui()
        self.result_frame.pack(fill=tk.X, pady=10)
        
        try:
            # Use encoded image if available, otherwise use original
            image_to_extract = self.encoded_image if self.encoded_image is not None else self.original_image
            message = extract_message(image_to_extract.copy())
            
            if message:
                self.result_text.insert(tk.END, f"Pesan yang ditemukan:\n\n{message}")
                self.status_var.set("Pesan berhasil diekstrak dari gambar")
            else:
                self.result_text.insert(tk.END, "Tidak ditemukan pesan dalam gambar")
                self.status_var.set("Tidak ditemukan pesan")
        except Exception as e:
            messagebox.showerror("Error", f"Gagal mengekstrak pesan: {str(e)}")
            self.status_var.set("Gagal mengekstrak pesan")
    
    def save_image(self):
        """Save encoded image to file"""
        if self.encoded_image is None:
            messagebox.showwarning("Peringatan", "Tidak ada gambar hasil untuk disimpan")
            return
            
        path = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=[("PNG files", "*.png"), ("JPEG files", "*.jpg"), ("All files", "*.*")])
            
        if not path:
            return
            
        try:
            # Convert back to BGR for OpenCV saving
            image_to_save = cv2.cvtColor(self.encoded_image, cv2.COLOR_RGB2BGR)
            cv2.imwrite(path, image_to_save)
            messagebox.showinfo("Berhasil", f"Gambar berhasil disimpan ke:\n{path}")
            self.status_var.set(f"Gambar disimpan ke: {os.path.basename(path)}")
        except Exception as e:
            messagebox.showerror("Error", f"Gagal menyimpan gambar: {str(e)}")
            self.status_var.set("Gagal menyimpan gambar")

if __name__ == "__main__":
    root = tk.Tk()
    app = ImprovedStegoApp(root)
    root.mainloop()