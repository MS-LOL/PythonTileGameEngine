import turtle
import json
import os
import time
import runpy

# Attempt to import Pillow for PNG conversion.
try:
    from PIL import Image
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False

# Constant for the world file name.
WORLD_FILENAME = "worldfile.json"

def load_texture(file_path):
    """
    Registers a texture with turtle. If the file is not a GIF and Pillow is available,
    converts the image to GIF format.
    Returns the path to the registered GIF file or None on failure.
    """
    ext = os.path.splitext(file_path)[1].lower()
    if ext != '.gif':
        if PIL_AVAILABLE:
            try:
                image = Image.open(file_path)
                gif_path = os.path.splitext(file_path)[0] + '.gif'
                image.save(gif_path, 'GIF')
                file_path = gif_path
            except Exception as e:
                print(f"Error converting {file_path} to GIF: {e}")
                return None
        else:
            print(f"File {file_path} is not a GIF and Pillow is not installed. Please convert to GIF or install Pillow.")
            return None
    try:
        turtle.register_shape(file_path)
        return file_path
    except Exception as e:
        print(f"Error registering shape for {file_path}: {e}")
        return None

class Level:
    """
    Represents a game level loaded from a world folder.
    Expects a JSON file (WORLD_FILENAME) with:
      - background_data: texture filename for the background.
      - floor_layer: 2D array of tile names.
      - collision_layer: 2D array for collision.
      - object_data: list of objects, each with:
           texture_file_name, method_of_interaction, starting_coordinates, script_name.
      - tile_data: list of tiles with:
           tile_name, tile_texture_file_name, walking_sound_file_name.
      - background_music: (optional) filename of an mp3 file.
    """
    def __init__(self, world_path):
        self.world_path = world_path
        self.data = self.load_world_data()
        self.tiles = {}       # Maps tile names to texture file paths.
        self.objects = []     # List of GameObject instances (includes the player).
        self.background = None  # Background texture file path.
        self.load_assets()

    def load_world_data(self):
        world_file = os.path.join(self.world_path, WORLD_FILENAME)
        try:
            with open(world_file, 'r') as f:
                data = json.load(f)
            return data
        except Exception as e:
            print(f"Error loading world data from {world_file}: {e}")
            return {}

    def load_assets(self):
        # Load and register tile textures.
        for tile in self.data.get("tile_data", []):
            tile_name = tile["tile_name"]
            texture_file = os.path.join(self.world_path, tile["tile_texture_file_name"])
            loaded_texture = load_texture(texture_file)
            if loaded_texture:
                self.tiles[tile_name] = loaded_texture

        # Register background texture if available.
        bg_texture = self.data.get("background_data")
        if bg_texture:
            bg_texture_path = os.path.join(self.world_path, bg_texture)
            loaded_bg = load_texture(bg_texture_path)
            if loaded_bg:
                self.background = loaded_bg

        # Create objects from object_data.
        for obj in self.data.get("object_data", []):
            texture_path = os.path.join(self.world_path, obj["texture_file_name"])
            loaded_texture = load_texture(texture_path)
            new_object = GameObject(
                texture=loaded_texture if loaded_texture else texture_path,
                interaction_method=obj["method_of_interaction"],
                start_pos=tuple(obj["starting_coordinates"]),
                script_name=obj["script_name"],
                world_path=self.world_path
            )
            self.objects.append(new_object)

    def draw_floor_layer(self, tile_size=16):
        """
        Draws the floor layer based on the 2D array "floor_layer".
        Each entry in the array should correspond to a tile name in tile_data.
        """
        floor = self.data.get("floor_layer")
        if not floor:
            return

        drawer = turtle.Turtle()
        drawer.hideturtle()
        drawer.penup()
        # Assume that the floor layer's first row corresponds to y=0.
        for y, row in enumerate(floor):
            for x, tile_name in enumerate(row):
                if tile_name in self.tiles:
                    drawer.goto(x * tile_size, y * tile_size)
                    drawer.shape(self.tiles[tile_name])
                    drawer.stamp()

class GameObject:
    """
    Represents an interactive object in the game world.
    """
    def __init__(self, texture, interaction_method, start_pos, script_name, world_path):
        self.texture = texture
        self.interaction_method = interaction_method  # e.g., "trigger_zone" or "key_press"
        self.start_pos = start_pos  # (x, y) tile coordinates.
        self.script_name = script_name  # Script to run on interaction.
        self.world_path = world_path
        self.turtle = turtle.Turtle()
        if self.texture:
            self.turtle.shape(self.texture)
        self.turtle.penup()
        self.set_position_from_tile(start_pos)

    def set_position_from_tile(self, tile_coords, tile_size=32):
        x, y = tile_coords
        self.turtle.goto(x * tile_size, y * tile_size)

    def interact(self):
        if self.script_name:
            script_path = os.path.join(self.world_path, self.script_name)
            try:
                runpy.run_path(script_path, run_name="__main__")
            except Exception as e:
                print(f"Error executing script {script_path}: {e}")

class Player(GameObject):
    """
    The player character.
    """
    def __init__(self, texture, start_pos, world_path):
        super().__init__(texture, interaction_method="player", start_pos=start_pos, script_name=None, world_path=world_path)
        self.turtle.color("blue")  # Differentiate the player visually.

class Camera:
    """
    Camera that follows a target (e.g., the player). Simulated using turtle's world coordinate system.
    """
    def __init__(self):
        self.x = 0
        self.y = 0

    def follow(self, target):
        self.x, self.y = target.turtle.position()
        width, height = 800, 600  # Screen dimensions.
        turtle.setworldcoordinates(self.x - width//2, self.y - height//2,
                                   self.x + width//2, self.y + height//2)

class GameEngine:
    def __init__(self):
        self.screen = turtle.Screen()
        self.screen.setup(width=800, height=600)
        self.screen.tracer(0)  # Manual updates for smoother animation.
        self.levels = self.load_levels()
        self.current_level = None
        self.player = None
        self.camera = Camera()

    def load_levels(self):
        """
        Searches the worlds directory (located next to engine.py) for valid world folders.
        A valid world folder must contain the WORLD_FILENAME.
        """
        levels = {}
        base_dir = os.path.dirname(__file__)
        worlds_dir = os.path.join(base_dir, "worlds")
        if not os.path.exists(worlds_dir):
            print("Worlds directory not found!")
            return levels

        for folder in os.listdir(worlds_dir):
            folder_path = os.path.join(worlds_dir, folder)
            if os.path.isdir(folder_path) and WORLD_FILENAME in os.listdir(folder_path):
                levels[folder] = folder_path
        return levels

    def change_level(self, level_name):
        """
        Changes the current level with fade-out and fade-in transitions.
        """
        if level_name not in self.levels:
            print(f"Level '{level_name}' not found!")
            return

        self.fade_out()
        turtle.clearscreen()  # Clear current screen and reset turtle state.
        self.current_level = Level(self.levels[level_name])

        # Draw the floor layer.
        self.current_level.draw_floor_layer()

        # For simplicity, assume the first object is the player.
        if self.current_level.objects:
            obj = self.current_level.objects[0]
            self.player = Player(texture=obj.texture, start_pos=obj.start_pos, world_path=obj.world_path)
            self.current_level.objects[0] = self.player

        self.fade_in()

    def fade_out(self):
        """
        Simulate a fade-out by drawing an expanding black rectangle.
        """
        fade = turtle.Turtle()
        fade.hideturtle()
        fade.penup()
        fade.speed(0)
        fade.color("black")
        width, height = 800, 600
        turtle.tracer(0)
        for i in range(20):
            fade.clear()
            fade.goto(-width//2, -height//2)
            fade.begin_fill()
            factor = (i + 1) / 20
            for _ in range(2):
                fade.forward(width)
                fade.left(90)
                fade.forward(height * factor)
                fade.left(90)
            fade.end_fill()
            self.screen.update()
            time.sleep(0.05)
        fade.clear()
        turtle.tracer(1)

    def fade_in(self):
        """
        Simulate a fade-in by reversing the fade-out effect.
        """
        fade = turtle.Turtle()
        fade.hideturtle()
        fade.penup()
        fade.speed(0)
        fade.color("black")
        width, height = 800, 600
        turtle.tracer(0)
        for i in range(20, 0, -1):
            fade.clear()
            fade.goto(-width//2, -height//2)
            fade.begin_fill()
            factor = i / 20
            for _ in range(2):
                fade.forward(width)
                fade.left(90)
                fade.forward(height * factor)
                fade.left(90)
            fade.end_fill()
            self.screen.update()
            time.sleep(0.05)
        fade.clear()
        turtle.tracer(1)

    def game_loop(self):
        """
        Main game loop: update the camera and screen.
        """
        while True:
            self.current_level.draw_floor_layer()
            if self.current_level.objects:
                obj = self.current_level.objects[0]
                self.player = Player(texture=obj.texture, start_pos=obj.start_pos, world_path=obj.world_path)
                self.current_level.objects[0] = self.player
            if self.player:
                self.camera.follow(self.player)
            self.screen.update()
            time.sleep(0.016)  # Approximately 60 FPS.

def main():
    engine = GameEngine()

    # For demonstration, load the first available level.
    if engine.levels:
        first_level = list(engine.levels.keys())[0]
        print(f"Loading level: {first_level}")
        engine.change_level(first_level)
    else:
        print("No levels found in the worlds directory.")
        return

    engine.game_loop()
