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

    def __init__(self, image, x, y, spritesheet):
        pygame.sprite.Sprite.__init__(self)
        self.image = spritesheet.parse_sprite(image)
        # Manual load in: self.image = pygame.image.load(image)
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

    def __init__(self, filename, spritesheet):
        self.tile_size = 16
        self.starting_positions = list()
        self.start_x, self.start_y = 0, 0
        self.spritesheet = spritesheet
        self.tiles = self.load_tiles(filename)
        self.map_surface = pygame.Surface((self.map_w, self.map_h))
        self.map_surface.set_colorkey((0, 0, 0)) # use this for static game maps. I'm going to be making a moving map game so I will need a different method.
        self.load_map()
    
    def draw_map(self, surface):
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
        tiles = []
        map = self.read_map_csv(map_csv_filename)
        x, y = 0, 0
        for row in map:
            x = 0
            for tile in row:

                tilesheet = self.read_tile_csv(tile_csv_filename)
                # We aren't going to be referencing the tile names to number keys, Instead we will replace this.
                try:
                    tiles.append(Tile(tilesheet[tile]["texture"], x * self.tile_size, y * self.tile_size, self.spritesheet))
                except ValueError as e:

                    # Handle the error here (e.g., log it, raise a custom error, etc.)

                    print(f"Error loading tile '{tile}' at ({x}, {y}): {e}")
                    dump = dump + "Error loading tile " + tile + " at (" + x + ", " + y + "): " + e + "\n"

                    # The dump variable is used for debugging when the exception causes a breakpoint.
                    # Look at the dump variable in the memory viewer to see a trace of all the errors that occured as the result of one thing.
                    
                    raise ValueError(f"Error loading tile '{tile}' at ({x}, {y}): Unable to load tile due to duplicate entry in {tile_csv_filename}: {e}")
                
                # move to next tile in current row
                x += 1
            # Move to the next row
            y += 1
        # store the size of the tile map
        self.map_w, self.map_h = x * self.tile_size, y * self.tile_size
        return tiles