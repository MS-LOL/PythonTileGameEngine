import pygame, csv, os

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
        self.start_x, self.start_y = 0, 0
        self.spritesheet = spritesheet
        self.tiles = self.load_tiles(filename)
        self.map_surface = pygame.Surface((self.map_w, self.map_h))
        self.map_surface.set_colorkey((0, 0, 0)) # use this for static game maps. I'm going to be making a moving map game so I will need a different method.
        self.load_map()
    
    def draw_map(self, surface):
        surface.blit(self.map_surface, (0, 0))
    
    def load_map(self):
        for tile in self.tiles:
            tile.draw(self.map_surface)
    
    def read_tile_csv(self, filename):
        tilesheet = {}
        with open(os.path.join(filename)) as data:
            data = csv.reader(data, delimiter=',')
            for row in data:
                # What is the CSV format going to contain?
                tile_id = row[0]
                tilesheet[tile_id] = {
                    "name": row[1],
                    "texture": row[2],
                    "walk_sound": row[3],
                    "collision": row[4].lower() == "true"
                }
                tilesheet.append(list(row))
        return tilesheet

    def read_map_csv(self, filename):
        map = []
        with open(os.path.join(filename)) as data:
            data = csv.reader(data, delimiter=',')
            for row in data:
                map.append(list(row))
        return map
    
    def load_tiles(self, filename):
        tiles = []
        map = self.read_csv(filename)
        x, y = 0, 0
        for row in map:
            x = 0
            for tile in row:

                texturenames = self.read_tile_csv()

                if tile == '0':
                    self.start_x, self.start_y = x * self.tile_size, y * self.tile_size
                elif tile == '1':
                    tiles.append(Tile('grass.png', x * self.tile_size, y * self.tile_size, self.spritesheet))
                elif tile == '2':
                    tiles.append(Tile('grass2.png', x * self.tile_size, y * self.tile_size, self.spritesheet))
                    # move to next tile in current row
                
                x += 1
                # Move to the next row
            y += 1
            # store the size of the tile map
        self.map_w, self.map_h = x * self.tile_size, y * self.tile_size
        return tiles