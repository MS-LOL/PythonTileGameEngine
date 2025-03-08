from PIL import Image

def join_tiles(tile_map, tile_images, tile_size):
    """
    Joins individual tile images into one large world map image.
    
    Parameters:
        tile_map (list of list of str): A 2D list where each element is a tile name.
        tile_images (dict): A mapping from tile names to file paths (assumed to be valid GIFs).
        tile_size (int): The size (width and height) of each tile in pixels.
        
    Returns:
        Image: A PIL Image object representing the full world.
    """
    if not tile_map:
        raise ValueError("Tile map is empty.")

    rows = len(tile_map)
    cols = len(tile_map[0])
    world_img = Image.new("RGBA", (cols * tile_size, rows * tile_size))
    
    for y, row in enumerate(tile_map):
        for x, tile_name in enumerate(row):
            tile_path = tile_images.get(tile_name)
            if not tile_path:
                continue  # Optionally fill with a default tile
            try:
                tile_img = Image.open(tile_path).resize((tile_size, tile_size))
                world_img.paste(tile_img, (x * tile_size, y * tile_size))
            except Exception as e:
                print(f"Error processing tile '{tile_name}' from {tile_path}: {e}")
    
    return world_img
