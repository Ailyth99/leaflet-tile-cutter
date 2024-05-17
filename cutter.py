from PIL import Image
import math,os


img_path=""
max_zoom_level=4
output='output'

def calculate_tiles(image_path, max_zoom_level):
    image = Image.open(image_path)
    width, height = image.size

    tile_width = math.ceil(width / (2 ** (max_zoom_level-1)))
    tile_height = math.ceil(height / (2 ** (max_zoom_level-1)))

    zoom_levels = {}
    for zoom_level in range(max_zoom_level):
        tiles_num = (2 ** zoom_level) ** 2  
        zoomed_width = tile_width * (2 ** zoom_level)  
        zoomed_height = tile_height * (2 ** zoom_level)  
        zoom_levels[zoom_level] = {'tiles_num': tiles_num, 'zoomed_size': (zoomed_width, zoomed_height)} 

    return (tile_width, tile_height), zoom_levels

#i=calculate_tiles(img_path,max_zoom_level)
#print(i)



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

def cut_tiles(image_path, max_zoom_level, output_folder):
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
                tile.save(f"{dir_path}/{y//tile_size[1]}.jpg")

cut_tiles(img_path, max_zoom_level, output)