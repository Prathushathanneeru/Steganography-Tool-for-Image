import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
import numpy as np
import threading

class StegoApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Efficient Steganography Tool")
        self.root.geometry("900x600")
        self.root.configure(bg='#E0F7FA')  # Soft cyan background
        self.root.minsize(500, 350)  # Minimum size to avoid layout break

        self.elements = [] # Holds widgets for resizing

        # Decorative gradient (simulated using solid colors for simplicity)
        self.gradient_bg = tk.Canvas(self.root, highlightthickness=0)
        self.gradient_bg.pack(fill="both", expand=True)
        self.elements.append(self.gradient_bg)

        # Main header label
        self.title_label = tk.Label(self.root, text="Steganography Tool",
                                   font=("Segoe UI", 34, "bold"),
                                   fg="#004D40", bg="#E0F7FA")
        self.title_label.place(relx=0.5, rely=0.08, anchor="center")
        self.elements.append(self.title_label)

        # Entry label and box
        self.entry_label = tk.Label(self.root, text="Enter the text:", font=("Segoe UI", 20, "bold"),
                                    fg="#00695C", bg="#E0F7FA")
        self.entry_label.place(relx=0.5, rely=0.20, anchor="center")
        self.elements.append(self.entry_label)

        self.entry_box = tk.Entry(self.root, font=("Segoe UI", 18), width=36, bg="#ffffff", fg="#333333",
                                 bd=4, relief="solid", justify="center")
        self.entry_box.place(relx=0.5, rely=0.28, anchor="center")
        self.elements.append(self.entry_box)

        # Custom styled buttons
        self.embed_btn = tk.Button(self.root, text="Embed Text in Image",
                                  font=("Segoe UI", 19, "bold"), bg="#0097A7", fg="white",
                                  activebackground="#00838F", activeforeground="white",
                                  relief="flat", bd=0, height=2, width=20, cursor="hand2",
                                  command=self.embed_dialog)
        self.embed_btn.place(relx=0.5, rely=0.42, anchor="center")
        self.elements.append(self.embed_btn)

        self.extract_btn = tk.Button(self.root, text="Extract Text from Image",
                                     font=("Segoe UI", 19, "bold"), bg="#0097A7", fg="white",
                                     activebackground="#00838F", activeforeground="white",
                                     relief="flat", bd=0, height=2, width=20, cursor="hand2",
                                     command=self.extract_dialog)
        self.extract_btn.place(relx=0.5, rely=0.52, anchor="center")
        self.elements.append(self.extract_btn)

        # Subtle drop shadows to buttons
        self.shadow_btn1 = tk.Label(self.root, bg="#80CBC4", width=23, height=2)
        self.shadow_btn1.place(relx=0.5, rely=0.42 + 0.013, anchor="center")
        self.shadow_btn2 = tk.Label(self.root, bg="#80CBC4", width=23, height=2)
        self.shadow_btn2.place(relx=0.5, rely=0.52 + 0.013, anchor="center")
        self.embed_btn.lift(self.shadow_btn1)
        self.extract_btn.lift(self.shadow_btn2)
        self.elements.extend([self.shadow_btn1, self.shadow_btn2])

        # Responsive resizing bindings
        self.root.bind('<Configure>', self.on_resize)

    def on_resize(self, event):
        """Redraw gradient and reposition widgets when window is resized"""
        w, h = event.width, event.height
        self.gradient_bg.config(width=w, height=h)
        self.gradient_bg.delete("all")
        self.gradient_bg.create_rectangle(0, 0, w, h, fill="#E0F7FA", outline="")
        self.gradient_bg.create_oval(-350, -150, w * 0.8, h * 0.9, fill="#80DEEA", outline="")
        self.gradient_bg.create_oval(w * 0.7, h * 0.6, w * 1.22, h * 1.14, fill="#26C6DA", outline="")

        # Relocate widgets based on new window size
        # Use proportional placements (relx, rely, anchor)
        self.title_label.place(relx=0.5, rely=0.08, anchor="center")
        self.entry_label.place(relx=0.5, rely=0.20, anchor="center")
        self.entry_box.place(relx=0.5, rely=0.28, anchor="center")
        self.embed_btn.place(relx=0.5, rely=0.42, anchor="center")
        self.extract_btn.place(relx=0.5, rely=0.52, anchor="center")
        self.shadow_btn1.place(relx=0.5, rely=0.42 + 0.013, anchor="center")
        self.shadow_btn2.place(relx=0.5, rely=0.52 + 0.013, anchor="center")

    def embed_dialog(self):
        img_path = filedialog.askopenfilename(title="Select Image", filetypes=[("PNG/BMP Files", "*.png *.bmp")])
        if not img_path: return
        text = self.entry_box.get()
        if not text:
            messagebox.showwarning("No text!", "Please enter text before embedding.")
            return
        threading.Thread(target=self.embed_text, args=(img_path, text)).start()

    def extract_dialog(self):
        img_path = filedialog.askopenfilename(title="Select Stego Image", filetypes=[("PNG/BMP Files", "*.png *.bmp")])
        if not img_path: return
        threading.Thread(target=self.extract_text, args=(img_path,)).start()

    def embed_text(self, img_path, text):
        img = Image.open(img_path)
        img = img.convert("RGB")
        data = np.array(img)
        binary = ''.join([format(ord(i), '08b') for i in text]) + '00000000'
        flat_data = data.flatten()
        if len(binary) > len(flat_data):
            messagebox.showerror("Error", "Message too long for image.")
            return
        for i in range(len(binary)):
            flat_data[i] = (flat_data[i] & 0xFE) | int(binary[i])
        new_img = np.reshape(flat_data, data.shape)
        save_path = filedialog.asksaveasfilename(defaultextension=".png")
        Image.fromarray(new_img.astype('uint8'), "RGB").save(save_path)
        messagebox.showinfo("Done", "Message embedded and image saved.")
        self.entry_box.delete(0, 'end')  # Clear the text box after embedding!

    def extract_text(self, img_path):
        img = Image.open(img_path)
        img = img.convert("RGB")
        data = np.array(img)
        flat_data = data.flatten()
        binary = ""
        for value in flat_data:
            binary += str(value & 1)
            if len(binary) % 8 == 0 and binary[-8:] == "00000000":
                break
        text = ''.join([chr(int(binary[i:i+8], 2)) for i in range(0, len(binary)-8, 8)])
        messagebox.showinfo("Result", f"Extracted Text:\n\n{text}")

if __name__ == "__main__":
    root = tk.Tk()
    StegoApp(root)
    root.mainloop()
