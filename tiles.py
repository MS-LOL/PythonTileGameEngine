import pygame, csv, os

# I just realised that this file is structured in such a way that it has it's own surface.
# This is excellent for drawing a preexisting scene onto the main game scene. Especially if loading each level uses Tile and TileMap.
# This is a good way to load a level and draw it onto the main game scene. I will be using this for the main game scene.

class Tile(pygame.sprite.Sprite):

    # Properties:
    # image
    # rect
    #
    # Methods:
    # __init__(self, image, x, y, spritesheet)
    # draw(self, surface)

    def __init__(self, tile, x, y, spritesheet):
        """Initializes the Tile class by loading the sprite image and setting its position.

        Args:
            tile (str): The name of the sprite image (filename) to load from the spritesheet. Not to be confused with filename.
            x (int): The width of the tile.
            y (int): The height of the tile.
            spritesheet (Spritesheet): The Spritesheet object used to load the sprite image.
        """
        pygame.sprite.Sprite.__init__(self)
        self.image = spritesheet.get_sprite(tile)
        # Manual load in: self.image = pygame.image.load(image_filename)
        self.rect = self.image.get_rect()
        self.rect.x, self.rect.y = x, y
    
    def draw(self, surface):
        surface.blit(self.image, (self.rect.x, self.rect.y))

class TileMap():

    # Properties:
    # start_x
    # start_y
    # tile_size
    # spritesheet
    # tiles
    # map_surface
    # map_w
    # map_h
    #
    # Methods:
    # __init__(self, filename, spritesheet)
    # draw_map(self, surface)
    # load_map(self)
    # read_map_csv(self, filename)
    # load_tiles(self, filename)

    def __init__(self, map_csv_filename, tile_csv_filename, level_dir_full_path, spritesheet):
        """Initializes the TileMap class by loading the tile map and its properties.
        This is a class that loads a tile map from a CSV file and draws it onto a surface using a spritesheet.

        Args:
            filename (str): _description_
            spritesheet (Spritesheet): _description_
        """
        self.tile_size = 8
        self.starting_positions = list()
        self.start_x, self.start_y = 0, 0
        self.spritesheet = spritesheet
        self.tiles = self.load_tiles(os.path.join(level_dir_full_path, map_csv_filename), os.path.join(level_dir_full_path, tile_csv_filename))
        self.map_surface = pygame.Surface((self.map_w, self.map_h))
        self.map_surface.set_colorkey((0, 0, 0)) # use this for static game maps. I'm going to be making a moving map game so I will need a different method.
        self.load_map()
    
    def draw_map(self, surface):
        """
        Draws the map surface onto the given surface.

        :param surface: The surface to draw the map onto.
        """
        surface.blit(self.map_surface, (0, 0))
    
    def init_map_properties(self, map_properties_filename):
        with open(os.path.join(map_properties_filename), encoding="utf-8") as data:
            for line in data:
                line = line.strip()
                if line.startswith("START_POSITION"):
                    # This is a single entry of a tuple, so we need to append it to the list
                    self.starting_positions.append(int(line.split("=")[1].strip()))
                    (self.start_x, self.start_y) = self.starting_positions[0]
                elif line.startswith("MAP_CSV_FILENAME"):
                    self.MAP_CSV_FILENAME = line.split("=")[1].strip()
                elif line.startswith("TILE_CSV_FILENAME"):
                    self.tile = line.split("=")[1].strip()
    
    def load_map(self):
        for tile in self.tiles:
            tile.draw(self.map_surface)
    
    def read_tile_csv(self, filename):
        tilesheet = {}
        with open(os.path.join(filename), encoding="utf-8") as data:
            data = csv.reader(data, delimiter=',')
            for line_number, row in enumerate(data, start=1):
                # Expected CSV format: Each row contains the tile name, texture file name (with extension), walk sound file name (with extension), and a boolean for collision (True/False).
                tile_name = row[0]
                if tile_name in tilesheet:
                    # tilesheet[tile_name] is not None, which means that the tile name already exists in the dictionary
                    # Something exists when it shouldn't
                    # This is a duplicate tile name, so we need to raise an error
                    raise ValueError(f"Duplicate tile name found in {filename} on line {line_number}: {tile_name}")
                tilesheet[tile_name] = {
                    "texture": row[1],
                    "walk_sound": row[2],
                    "collision": row[3].lower() == "true"
                }
        return tilesheet

    def read_map_csv(self, filename):
        map = []
        with open(os.path.join(filename)) as data:
            data = csv.reader(data, delimiter=',')
            for row in data:
                map.append(list(row))
        return map
    
    def load_tiles(self, map_csv_filename, tile_csv_filename):
        """_summary_

        Args:
            map_csv_filename (_type_): _description_
            tile_csv_filename (_type_): _description_

        Raises:
            ValueError: _description_

        Returns:
            _type_: _description_
        """
        tiles = []
        map = self.read_map_csv(map_csv_filename)
        tilesheet = self.read_tile_csv(tile_csv_filename)
        x, y = 0, 0
        for row in map:
            x = 0
            for tile in row:
                # We aren't going to be referencing the tile names to number keys, Instead we will replace this in the file.
                if tile == "none":
                    # This is a blank tile, so we can skip it
                    continue
                else:
                    tiles.append(Tile(tile, x * self.tile_size, y * self.tile_size, self.spritesheet))
                # move to next tile in current row
                x += 1
            # Move to the next row
            y += 1
        # store the size of the tile map
        self.map_w, self.map_h = x * self.tile_size, y * self.tile_size
        return tiles