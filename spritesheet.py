import pygame
import json
import os


class Spritesheet:
    def __init__(self, json_file, level_directory_path):
        """
        Initializes the Spritesheet class by loading sprite data from a JSON file.
        :param json_file: Path to the JSON file containing sprite names and their corresponding file paths.
        """
        self.json_file = json_file
        self.level_directory_path = level_directory_path
        self.sprites = dict()  # Dictionary to store loaded sprites
        self.load_sprites(os.path.join(self.level_directory_path, self.json_file))

    def load_sprites(self, json_file):
        """
        Loads sprite data from a JSON file and initializes the sprite dictionary.
        :param json_file: Path to the JSON file.
        """
        if not os.path.exists(json_file):
            raise FileNotFoundError(f"JSON file '{json_file}' not found.")
        
        with open(json_file, 'r') as f:
            sprite_data = json.load(f)
        
        for name, filename in sprite_data.items():
            if not os.path.exists(os.path.join(self.level_directory_path, filename)):
                raise FileNotFoundError(f"Sprite file '{filename}' for '{name}' not found.")
            
            sprite = pygame.image.load(os.path.join(self.level_directory_path, filename)).convert_alpha()
            self.sprites[name] = sprite

    def get_sprite(self, name):
        """
        Retrieves a sprite by its name.
        :param name: The name of the sprite to retrieve.
        :return: The `pygame.Surface` object for the sprite.
        """
        if name not in self.sprites:
            raise KeyError(f"Sprite '{name}' not found in the spritesheet.")
        return self.sprites[name]

    def add_sprite(self, name, filepath):
        """
        Dynamically adds a new sprite to the spritesheet.
        :param name: The name to associate with the sprite.
        :param filepath: The path to the sprite image file.
        """
        if name in self.sprites:
            raise KeyError(f"Sprite '{name}' is already registered.")
        if not os.path.exists(os.path.join(self.level_directory_path, filepath)):
            raise FileNotFoundError(f"Sprite file '{filepath}' not found.")
        
        sprite = pygame.image.load(filepath).convert_alpha()
        self.sprites[name] = sprite

    def remove_sprite(self, name):
        """
        Removes a sprite from the spritesheet.
        :param name: The name of the sprite to remove.
        """
        if name in self.sprites:
            del self.sprites[name]
        else:
            raise KeyError(f"Sprite '{name}' not found in the spritesheet.")