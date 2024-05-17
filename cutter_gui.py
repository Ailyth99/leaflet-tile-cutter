from tkinter import *
from tkinter import filedialog,messagebox,ttk
from tkinter.ttk import Combobox
from PIL import Image
import math,os


class CutterGUI:
    def __init__(self, master):
        self.master = master
        master.title("LeafletTileCutter")

        
        master.grid_columnconfigure(0, weight=1)
        master.grid_columnconfigure(1, weight=1)
        master.grid_columnconfigure(2, weight=1)
        master.grid_columnconfigure(3, weight=1)
        master.grid_columnconfigure(4, weight=1)

        master.grid_rowconfigure(0, minsize=50)
        master.grid_rowconfigure(1, minsize=50)
        master.grid_rowconfigure(2, minsize=50)
        master.grid_rowconfigure(3, minsize=50)
        master.grid_rowconfigure(4, minsize=50)

        Label(master, text="Select Image:").grid(row=0, column=0, sticky=E)
        self.entry = Entry(master)
        self.entry.grid(row=0, column=1, sticky=EW)
        self.browse_button = Button(master, text="Browse", command=self.browse)
        self.browse_button.grid(row=0, column=2, sticky=W)

        Label(master, text="Zoom Level and Tile Size:").grid(row=1, column=0, sticky=E)
        self.combo = Combobox(master)
        self.combo.grid(row=1, column=1, sticky=EW)

        Label(master, text="Output Image Format:").grid(row=2, column=0, sticky=E)
        self.combo2 = Combobox(master, values=["png", "jpg", "webp"])
        self.combo2.grid(row=2, column=1, sticky=EW)
        self.combo2.current(0)

        Label(master, text="Output Directory:").grid(row=3, column=0, sticky=E)
        self.entry2 = Entry(master)
        self.entry2.grid(row=3, column=1, sticky=EW)
        self.browse_button2 = Button(master, text="Browse", command=self.browse2)
        self.browse_button2.grid(row=3, column=2, sticky=W)

        frame_left = Frame(master, width=20)
        frame_left.grid(row=4, column=0)
        frame_right = Frame(master, width=20)
        frame_right.grid(row=4, column=4)

        self.cut_button = Button(master, text="Start Slicing", command=self.cut)
        self.cut_button.grid(row=4, column=0, columnspan=8)


        master.geometry("400x250")  

    def browse(self):
        filetypes = (
            ('Image files', '*.jpeg;*.jpg;*.png;*.gif;*.bmp'),
            ('All files', '*.*')
        )
        self.entry.delete(0, END)
        img_path = filedialog.askopenfilename(filetypes=filetypes)
        if img_path:
            self.entry.delete(0, END)
            self.entry.insert(0, img_path)
            self.update_combo(img_path)
    
    def update_combo(self, img_path):
        zoom_levels = calculate_max_zoom_level(img_path)
        self.combo['values'] = [f"{level}, {size}" for level, size in zoom_levels.items()]
        self.combo.current(0)

    def browse2(self):
        self.entry2.delete(0, END)
        self.entry2.insert(0, filedialog.askdirectory())

    def cut(self):
        img_path = self.entry.get()
        if not img_path:
            messagebox.showerror("Error", "Please Select an Image")
            return

        output = self.entry2.get()
        if not output:
            messagebox.showerror("Error", "Please Select an Output Directory")
            return

        max_zoom_level = int(self.combo.get().split(',')[0])
        img_format = self.combo2.get()
        tile_size, _ = calculate_tiles(img_path, max_zoom_level)
        cut_tiles(img_path, max_zoom_level, output, img_format)
        self.generate_html(output, int(max_zoom_level), img_format, tile_size)
        messagebox.showinfo("info", "Complete")

    def generate_html(self, output, max_zoom_level, img_format, tile_size):
        center = [-tile_size[0] // 2, tile_size[1] // 2]
        
        html_content = f"""
<!DOCTYPE html>
<html>
    <head>
    <meta charset="utf-8">
    <title>EXAMPLE MAP</title>
    <link rel="stylesheet" href="https://unpkg.com/leaflet@1.7.1/dist/leaflet.css"/>
    <script src="https://unpkg.com/leaflet@1.7.1/dist/leaflet.js" ></script>
    <style>html, body {{height: 100%;margin: 0;padding: 0;}}</style>
    </head>
    <body>
        <div id="myMap" style="width:100%;height:100%"></div>
        <script type="text/javascript">
         var map = L.map('myMap', {{crs: L.CRS.Simple,minZoom: 1, maxZoom:{max_zoom_level-1}, maxNativeZoom:{max_zoom_level-1}}});
         var tile = {{tileSize: L.point{tile_size}}};
         L.tileLayer('{{z}}/{{x}}/{{y}}.{img_format}', tile).addTo(map)
         map.setView({center}, {max_zoom_level-1});
        </script>
    </body>
</html>
        """
        with open(f"{output}/index.html", "w") as f:
            f.write(html_content)

def calculate_tiles(image_path, max_zoom_level):
    image = Image.open(image_path)
    width, height = image.size

    tile_width = math.ceil(width / (2 ** (max_zoom_level-1)))
    tile_height = math.ceil(height / (2 ** (max_zoom_level-1)))

    zoom_levels = {}
    for zoom_level in range(max_zoom_level):
        tiles_num = (2 ** zoom_level) ** 2 # Calculate the number of tiles
        zoomed_width = tile_width * (2 ** zoom_level) # Calculate the zoomed width
        zoomed_height = tile_height * (2 ** zoom_level) # Calculate the zoomed height
        zoom_levels[zoom_level] = {'tiles_num': tiles_num, 'zoomed_size': (zoomed_width, zoomed_height)} # Tile size, zoomed width and height

    return (tile_width, tile_height), zoom_levels


def calculate_max_zoom_level(image_path):
    image = Image.open(image_path)
    width, height = image.size

    max_zoom_level = 2
    zoom_levels = {}
    while True:
        tile_width = math.ceil(width / (2 ** max_zoom_level))
        tile_height = math.ceil(height / (2 ** max_zoom_level))
        if tile_width < 30 or tile_height < 30:
            break
        zoom_levels[max_zoom_level+1] = (tile_width, tile_height)
        max_zoom_level += 1

    return zoom_levels

#print(calculate_max_zoom_level(img_path))

def cut_tiles(image_path, max_zoom_level, output_folder, img_format):
    tile_size, zoom_levels = calculate_tiles(image_path, max_zoom_level)
    image = Image.open(image_path)

    for zoom_level, info in zoom_levels.items():
        zoomed_size = info['zoomed_size']
        zoomed_image = image.resize(zoomed_size, Image.ANTIALIAS)
        for x in range(0, zoomed_size[0], tile_size[0]):
            for y in range(0, zoomed_size[1], tile_size[1]):
                tile = zoomed_image.crop((x, y, x + tile_size[0], y + tile_size[1]))
                dir_path = f"{output_folder}/{zoom_level}/{x//tile_size[0]}"
                if not os.path.exists(dir_path):
                    os.makedirs(dir_path)
                tile.save(f"{dir_path}/{y//tile_size[1]}.{img_format}")

#cut_tiles(img_path, max_zoom_level, output)

root = Tk()
my_gui = CutterGUI(root)
root.mainloop()