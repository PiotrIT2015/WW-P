import os
from tkinter import Tk, Label, Button, Frame, Canvas, PhotoImage, Scrollbar, Listbox, EXTENDED
from PIL import Image, ImageTk
import subprocess

class ImageViewerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("WW-P")
        self.root.geometry("1200x600")

        # Store loaded images
        self.categories = {}
        self.current_category = None
        self.current_image_index = 0
        self.image_labels = []

        # Default directory for categories
        self.base_directory = os.path.join(os.getcwd(), "img")  # Compatible with Windows and other OS

        # GUI Layout
        self.setup_gui()
        self.load_categories()  # Automatically load categories on startup

    def setup_gui(self):
        # Category list
        self.category_listbox = Listbox(self.root, selectmode=EXTENDED, height=20, width=30)
        self.category_listbox.pack(side="left", fill="y")
        self.category_listbox.bind("<<ListboxSelect>>", self.on_category_select)

        # Image display area
        self.image_frame = Frame(self.root)
        self.image_frame.pack(side="right", fill="both", expand=True)

        self.canvas = Canvas(self.image_frame, bg="white")
        self.canvas.pack(fill="both", expand=True)

        # Buttons
        self.button_frame = Frame(self.root)
        self.button_frame.pack(side="bottom", fill="x")

        Button(self.button_frame, text="Previous Image", command=self.prev_image).pack(side="top")
        Button(self.button_frame, text="Next Image", command=self.next_image).pack(side="top")
        Button(self.button_frame, text="Refresh Categories", command=self.load_categories).pack(side="top")
        Button(self.button_frame, text="RelaxationTube", command=self.launch_yii_app).pack(side="top")
        Button(self.button_frame, text="Exit", command=self.root.quit).pack(side="top")

    def launch_yii_app(self):
        try:
            subprocess.Popen(["php", "yii", "serve"], cwd=os.path.join(os.getcwd(), "RelaxationTube"))
            print("Yii application launched.")
        except Exception as e:
            print(f"Failed to launch Yii application: {e}")

    def load_categories(self):
        directory = self.base_directory
        if not os.path.exists(directory):
            print(f"Directory {directory} does not exist.")
            return

        self.categories.clear()
        self.category_listbox.delete(0, "end")

        for category in os.listdir(directory):
            category_path = os.path.join(directory, category)
            if os.path.isdir(category_path):
                images = [os.path.join(category_path, f) for f in os.listdir(category_path) if f.lower().endswith((".png", ".jpg", ".jpeg", ".gif"))]
                if images:
                    self.categories[category] = images
                    self.category_listbox.insert("end", category)

    def on_category_select(self, event):
        selected = self.category_listbox.curselection()
        if selected:
            self.current_category = self.category_listbox.get(selected[0])
            self.current_image_index = 0
            self.show_image()

    def show_image(self):
        if not self.current_category:
            return

        images = self.categories.get(self.current_category, [])
        if not images:
            return

        image_path = images[self.current_image_index]
        img = Image.open(image_path)
        img.thumbnail((800, 600))
        photo = ImageTk.PhotoImage(img)

        self.canvas.delete("all")
        self.canvas.create_image(400, 300, image=photo, anchor="center")
        self.canvas.image = photo

    def prev_image(self):
        if not self.current_category:
            return

        self.current_image_index -= 1
        if self.current_image_index < 0:
            self.current_image_index = len(self.categories[self.current_category]) - 1
        self.show_image()

    def next_image(self):
        if not self.current_category:
            return

        self.current_image_index += 1
        if self.current_image_index >= len(self.categories[self.current_category]):
            self.current_image_index = 0
        self.show_image()

if __name__ == "__main__":
    root = Tk()
    app = ImageViewerApp(root)
    root.mainloop()
