import tkinter as tk
from tkinter import ttk, scrolledtext
from PIL import Image, ImageTk
import os
import sys
import subprocess

def open_with_default_app(file_path):
    """
    Otwiera plik za pomocą domyślnej aplikacji systemowej.
    Działa na systemach Windows, macOS i Linux.
    """
    try:
        if sys.platform == "win32":
            os.startfile(file_path)
        elif sys.platform == "darwin":
            subprocess.run(['open', file_path], check=True)
        else:
            subprocess.run(['xdg-open', file_path], check=True)
    except Exception as e:
        print(f"Błąd: Nie można otworzyć pliku '{file_path}'. Powód: {e}")
        # Opcjonalnie można dodać okno dialogowe z błędem
        # from tkinter import messagebox
        # messagebox.showerror("Błąd otwierania pliku", f"Nie można otworzyć pliku: {e}")

class ImageViewerApp:
    """
    Samodzielna aplikacja do przeglądania plików, obrazów i tekstów,
    z drzewem katalogów po lewej stronie.
    """
    def __init__(self, root):
        self.root = root
        self.root.title("White War Explorer")
        self.root.geometry("1200x600")

        self.current_directory = os.getcwd()
        # Ścieżka do obrazka domyślnego, który zostanie utworzony, jeśli nie istnieje
        self.default_image_path = os.path.join(self.current_directory, "default_image.png")

        self.create_default_image_if_needed()
        self.setup_gui()
        self.populate_tree(self.current_directory, "")

    def create_default_image_if_needed(self):
        """Tworzy prosty, szary obrazek, jeśli domyślny plik nie istnieje."""
        if not os.path.exists(self.default_image_path):
            try:
                print(f"Tworzenie domyślnego obrazka w: {self.default_image_path}")
                img = Image.new('RGB', (800, 600), color='gray')
                img.save(self.default_image_path)
            except Exception as e:
                print(f"Nie udało się stworzyć domyślnego obrazka: {e}")

    def setup_gui(self):
        """Konfiguruje interfejs graficzny aplikacji."""
        main_frame = tk.Frame(self.root)
        main_frame.pack(fill="both", expand=True)

        # Panel z drzewem plików (lewa strona)
        tree_frame = tk.Frame(main_frame)
        tree_frame.pack(side="left", fill="y", padx=5, pady=5)

        self.tree = ttk.Treeview(tree_frame, show="tree", selectmode=tk.BROWSE)
        self.tree.pack(side="left", fill="y", expand=True)
        self.tree.bind("<<TreeviewSelect>>", self.on_tree_select)
        self.tree.bind("<<TreeviewOpen>>", self.on_tree_expand)

        ysb = ttk.Scrollbar(tree_frame, orient='vertical', command=self.tree.yview)
        self.tree.configure(yscroll=ysb.set)
        ysb.pack(side='right', fill='y')

        # Panel do wyświetlania treści (prawa strona)
        self.display_frame = tk.Frame(main_frame, bg="black")
        self.display_frame.pack(side="right", fill="both", expand=True)

        self.canvas = tk.Canvas(self.display_frame, bg="black")
        self.text_area = scrolledtext.ScrolledText(self.display_frame, wrap=tk.WORD, bg="#1e1e1e", fg="#d4d4d4", insertbackground="white")

        self.show_default_image()

    def populate_tree(self, parent_path, parent_node):
        """Wypełnia gałąź drzewa zawartością podanej ścieżki."""
        if not os.path.isdir(parent_path):
            return

        try:
            # Sortowanie: katalogi na górze, potem pliki, alfabetycznie
            items = sorted(os.listdir(parent_path), key=lambda x: (not os.path.isdir(os.path.join(parent_path, x)), x.lower()))
            for item_name in items:
                item_path = os.path.join(parent_path, item_name)
                node = self.tree.insert(parent_node, 'end', text=item_name, open=False, values=[item_path])
                # Jeśli element jest katalogiem, dodaj pusty element-dziecko, aby pokazać strzałkę rozwijania
                if os.path.isdir(item_path):
                    self.tree.insert(node, 'end', text='...')
        except PermissionError:
            self.tree.insert(parent_node, 'end', text="[Brak dostępu]")

    def on_tree_expand(self, event):
        """Obsługuje zdarzenie rozwinięcia katalogu w drzewie."""
        node_id = self.tree.focus()
        # Pobierz elementy-dzieci, które są tylko placeholderami
        children = self.tree.get_children(node_id)
        if children and self.tree.item(children[0], "text") == "...":
            # Usuń placeholder
            self.tree.delete(children)
            # Wypełnij katalog rzeczywistą zawartością
            path = self.tree.item(node_id, 'values')[0]
            self.populate_tree(path, node_id)

    def on_tree_select(self, event):
        """Obsługuje zdarzenie zaznaczenia elementu w drzewie."""
        selected_item = self.tree.selection()
        if selected_item:
            item_path = self.tree.item(selected_item[0], "values")[0]
            if os.path.isfile(item_path):
                self.show_file_content(item_path)

    def is_image_file(self, path):
        """Sprawdza, czy plik ma rozszerzenie typowe dla obrazów."""
        return path.lower().endswith((".png", ".jpg", ".jpeg", ".gif", ".bmp", ".tiff"))

    def is_text_file(self, path):
        """Sprawdza, czy plik ma rozszerzenie typowe dla plików tekstowych."""
        return path.lower().endswith((".txt", ".log", ".py", ".md", ".json", ".csv", ".xml", ".html", ".css", ".js", ".ini"))

    def show_file_content(self, file_path):
        """Wybiera metodę wyświetlania w zależności od typu pliku."""
        if self.is_image_file(file_path):
            self.show_image(file_path)
        elif self.is_text_file(file_path):
            self.show_text_content(file_path)
        else:
            # Dla pozostałych plików, otwórz za pomocą domyślnej aplikacji
            open_with_default_app(file_path)

    def show_image(self, image_path):
        """Wyświetla obraz na płótnie (Canvas), dopasowując jego rozmiar."""
        try:
            self.text_area.pack_forget()
            self.canvas.pack(fill="both", expand=True)
            img = Image.open(image_path)
            
            self.canvas.update_idletasks()
            canvas_width = self.canvas.winfo_width()
            canvas_height = self.canvas.winfo_height()

            # Zabezpieczenie na wypadek, gdyby widget nie był jeszcze narysowany
            if canvas_width < 2 or canvas_height < 2:
                canvas_width, canvas_height = 800, 600
            
            # Skalowanie obrazu z zachowaniem proporcji
            img.thumbnail((canvas_width, canvas_height), Image.Resampling.LANCZOS)
            
            photo = ImageTk.PhotoImage(img)
            self.canvas.delete("all")
            # Wyśrodkowanie obrazu na płótnie
            self.canvas.create_image(canvas_width / 2, canvas_height / 2, image=photo, anchor="center")
            self.canvas.image = photo  # Zachowaj referencję, aby obraz nie zniknął
        except Exception as e:
            print(f"Błąd podczas ładowania obrazu '{image_path}': {e}")
            self.show_default_image()

    def show_text_content(self, file_path):
        """Wyświetla zawartość pliku tekstowego."""
        try:
            self.canvas.pack_forget()
            self.text_area.pack(fill="both", expand=True)
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as file:
                self.text_area.delete('1.0', tk.END)
                self.text_area.insert('1.0', file.read())
        except Exception as e:
            self.text_area.delete('1.0', tk.END)
            self.text_area.insert('1.0', f"Błąd podczas odczytu pliku:\n\n{e}")

    def show_default_image(self):
        """Wyświetla domyślny obraz, jeśli istnieje."""
        if os.path.exists(self.default_image_path):
            self.show_image(self.default_image_path)
        else:
            # Jeśli domyślny obrazek nie istnieje, pokaż czarne tło
            self.text_area.pack_forget()
            self.canvas.pack(fill="both", expand=True)
            self.canvas.delete("all")

if __name__ == "__main__":
    root = tk.Tk()
    app = ImageViewerApp(root)
    root.mainloop()