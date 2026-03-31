import customtkinter as ctk
from PIL import Image
import os
from tkinter import filedialog, messagebox

# ASCII characters to use for the "dot" effect, from densest to lightest
# Standard dots and characters
ASCII_CHARS = "@%#*+=-:. "

class ImageToDotApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Image to Text Dot Converter")
        self.geometry("800x700")

        # Set appearance
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        # UI Elements
        self.setup_ui()

        # State
        self.image_path = None
        self.original_image = None

    def setup_ui(self):
        # Main layout
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # Header Frame
        header_frame = ctk.CTkFrame(self)
        header_frame.grid(row=0, column=0, padx=20, pady=20, sticky="ew")
        
        title_label = ctk.CTkLabel(header_frame, text="Image to Text Dot Converter", font=ctk.CTkFont(size=24, weight="bold"))
        title_label.pack(pady=10)

        # Controls Frame
        controls_frame = ctk.CTkFrame(self)
        controls_frame.grid(row=1, column=0, padx=20, pady=(0, 20), sticky="nsew")
        controls_frame.grid_columnconfigure(0, weight=1)
        controls_frame.grid_rowconfigure(2, weight=1)

        # Button for Upload
        self.upload_btn = ctk.CTkButton(controls_frame, text="Upload Image", command=self.upload_image)
        self.upload_btn.grid(row=0, column=0, padx=10, pady=10)

        # Options Frame
        options_frame = ctk.CTkFrame(controls_frame)
        options_frame.grid(row=1, column=0, padx=10, pady=10, sticky="ew")
        
        # Mode Toggle
        self.research_mode_var = ctk.BooleanVar(value=False)
        self.mode_switch = ctk.CTkSwitch(options_frame, text="Research Mode (Transparency)", variable=self.research_mode_var)
        self.mode_switch.pack(pady=10)

        # Width Slider
        width_container = ctk.CTkFrame(options_frame, fg_color="transparent")
        width_container.pack(fill="x", padx=10, pady=5)
        self.width_label = ctk.CTkLabel(width_container, text="Width (characters):")
        self.width_label.pack(side="left", padx=10)
        
        self.width_slider = ctk.CTkSlider(width_container, from_=10, to=100, number_of_steps=90)
        self.width_slider.set(30)
        self.width_slider.pack(side="left", padx=10, fill="x", expand=True)

        # Research Mode Chars
        char_container = ctk.CTkFrame(options_frame, fg_color="transparent")
        char_container.pack(fill="x", padx=10, pady=5)
        
        self.opaque_label = ctk.CTkLabel(char_container, text="Opaque:")
        self.opaque_label.pack(side="left", padx=5)
        self.opaque_char_entry = ctk.CTkEntry(char_container, width=30)
        self.opaque_char_entry.insert(0, "▣")
        self.opaque_char_entry.pack(side="left", padx=5)

        self.trans_label = ctk.CTkLabel(char_container, text="Transparent:")
        self.trans_label.pack(side="left", padx=5)
        self.trans_char_entry = ctk.CTkEntry(char_container, width=30)
        self.trans_char_entry.insert(0, "※")
        self.trans_char_entry.pack(side="left", padx=5)

        self.convert_btn = ctk.CTkButton(controls_frame, text="Convert to Dots", command=self.convert_image)
        self.convert_btn.grid(row=2, column=0, padx=10, pady=10)

        # Result Display (TextBox)
        self.result_text = ctk.CTkTextbox(controls_frame, font=("Courier", 12), wrap="none")
        self.result_text.grid(row=3, column=0, padx=10, pady=10, sticky="nsew")

        # Save Button
        self.save_btn = ctk.CTkButton(controls_frame, text="Save as Text File", command=self.save_text)
        self.save_btn.grid(row=4, column=0, padx=10, pady=10)

    def upload_image(self):
        file_path = filedialog.askopenfilename(
            filetypes=[("Image files", "*.jpg *.jpeg *.png *.bmp *.gif")]
        )
        if file_path:
            self.image_path = file_path
            self.original_image = Image.open(file_path)
            messagebox.showinfo("Success", f"Loaded image: {os.path.basename(file_path)}")

    def scale_image(self, image, new_width, mode_multiplier=0.5):
        (original_width, original_height) = image.size
        aspect_ratio = original_height / float(original_width)
        # Text characters aspect ratio correction
        # Research mode characters (▣, ※) are typically square, so use multiplier 1.0
        # Standard ASCII characters are tall, so use multiplier 0.5
        new_height = int(aspect_ratio * new_width * mode_multiplier)
        new_image = image.resize((new_width, new_height))
        return new_image

    def convert_to_grayscale(self, image):
        return image.convert("L")

    def pixels_to_ascii(self, image):
        pixels = image.getdata()
        characters = "".join([ASCII_CHARS[pixel // (256 // len(ASCII_CHARS))] for pixel in pixels])
        return characters

    def pixels_to_research_dots(self, image, opaque_char="▣", trans_char="※"):
        # Ensure image has alpha channel
        if image.mode != 'RGBA':
            image = image.convert('RGBA')
        
        pixels = image.getdata()
        characters = []
        for pixel in pixels:
            # pixel is (R, G, B, A)
            if pixel[3] > 0: # If alpha is not 0
                characters.append(opaque_char)
            else:
                characters.append(trans_char)
        
        return "".join(characters)

    def convert_image(self):
        if not self.original_image:
            messagebox.showwarning("Warning", "Please upload an image first!")
            return

        try:
            new_width = int(self.width_slider.get())
            is_research_mode = self.research_mode_var.get()
            
            if is_research_mode:
                # Research Mode: Use transparency and 1:1 aspect ratio
                opaque_char = self.opaque_char_entry.get() or "▣"
                trans_char = self.trans_char_entry.get() or "※"
                
                # Full-width characters are usually square, multiplier 1.0 or 0.8
                # But let's try 1.0 first
                image = self.scale_image(self.original_image, new_width, mode_multiplier=1.0)
                pixels = self.pixels_to_research_dots(image, opaque_char, trans_char)
            else:
                # Standard Mode
                image = self.scale_image(self.original_image, new_width, mode_multiplier=0.5)
                image = self.convert_to_grayscale(image)
                pixels = self.pixels_to_ascii(image)
                
            pixel_count = len(pixels)
            ascii_image = "\n".join([pixels[index:(index + new_width)] for index in range(0, pixel_count, new_width)])
            
            # Display result
            self.result_text.delete("1.0", "end")
            self.result_text.insert("1.0", ascii_image)
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to convert image: {str(e)}")


    def save_text(self):
        content = self.result_text.get("1.0", "end-1c")
        if not content.strip():
            messagebox.showwarning("Warning", "No content to save!")
            return
            
        file_path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt")]
        )
        if file_path:
            with open(file_path, "w") as f:
                f.write(content)
            messagebox.showinfo("Success", f"Saved to: {file_path}")

if __name__ == "__main__":
    app = ImageToDotApp()
    app.mainloop()
