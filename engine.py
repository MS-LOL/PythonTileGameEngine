import turtle
import json
import os
import time
import runpy
from image_joiner import join_tiles

# Global scaling constants.
BASE_SCREEN_WIDTH = 256
BASE_SCREEN_HEIGHT = 144
SCALE_FACTOR = 2

SCALED_SCREEN_WIDTH = BASE_SCREEN_WIDTH * SCALE_FACTOR
SCALED_SCREEN_HEIGHT = BASE_SCREEN_HEIGHT * SCALE_FACTOR

BASE_TILE_SIZE = 16
SCALED_TILE_SIZE = BASE_TILE_SIZE * SCALE_FACTOR  # 32

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
    Expects a JSON file (WORLD_FILENAME) with keys for background, floor layer,
    collision layer, object data, tile data, etc.
    """
    def __init__(self, world_path, tile_size=SCALED_TILE_SIZE):
        self.world_path = world_path
        self.tile_size = tile_size
        self.data = self.load_world_data()
        self.tiles = {}       # Mapping of tile names to texture paths.
        self.objects = []     # List of GameObject instances.
        self.background = None  # Background texture file path.
        self.world_image_path = None  # Path to the pre-rendered world image.
        self.load_assets()

    def load_world_data(self):
        world_file = os.path.join(self.world_path, WORLD_FILENAME)
        try:
            with open(world_file, 'r') as f:
                return json.load(f)
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

        # Pre-render the entire floor (world) image using the floor_layer data.
        tile_map = self.data.get("floor_layer")
        if tile_map:
            world_img = join_tiles(tile_map, self.tiles, self.tile_size)
            # Save the generated image to the world folder (or a temp path).
            self.world_image_path = os.path.join(self.world_path, "temp_world_map.gif")
            world_img.save(self.world_image_path, "GIF")
            # Register the world image as a turtle shape.
            turtle.register_shape(self.world_image_path)

        # Create objects from object_data.
        for obj in self.data.get("object_data", []):
            texture_path = os.path.join(self.world_path, obj["texture_file_name"])
            loaded_texture = load_texture(texture_path)
            new_object = GameObject(
                texture=loaded_texture if loaded_texture else texture_path,
                interaction_method=obj["method_of_interaction"],
                start_pos=tuple(obj["starting_coordinates"]),
                script_name=obj["script_name"],
                world_path=self.world_path,
                tile_size=self.tile_size  # Pass the scaled tile size.
            )
            self.objects.append(new_object)

    def draw_floor_layer(self):
        """
        (Optional) Draws the floor layer by stamping individual tiles.
        Not used if the pre-rendered image is displayed.
        """
        floor = self.data.get("floor_layer")
        if not floor:
            return

        drawer = turtle.Turtle()
        drawer.hideturtle()
        drawer.penup()
        for y, row in enumerate(floor):
            for x, tile_name in enumerate(row):
                if tile_name in self.tiles:
                    drawer.goto(x * self.tile_size, y * self.tile_size)
                    drawer.shape(self.tiles[tile_name])
                    drawer.stamp()

class GameObject:
    """
    Represents an interactive object in the game world.
    """
    def __init__(self, texture, interaction_method, start_pos, script_name, world_path, tile_size=SCALED_TILE_SIZE):
        self.texture = texture
        self.interaction_method = interaction_method
        self.start_pos = start_pos
        self.script_name = script_name
        self.world_path = world_path
        self.tile_size = tile_size  # Store the scaled tile size.
        self.turtle = turtle.Turtle()
        if self.texture:
            self.turtle.shape(self.texture)
        self.turtle.penup()
        self.set_position_from_tile(start_pos)

    def set_position_from_tile(self, tile_coords):
        x, y = tile_coords
        self.turtle.goto(x * self.tile_size, y * self.tile_size)

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
    def __init__(self, texture, start_pos, world_path, tile_size=SCALED_TILE_SIZE):
        super().__init__(texture, interaction_method="player", start_pos=start_pos, script_name=None, world_path=world_path, tile_size=tile_size)
        self.turtle.color("blue")

class Camera:
    """
    The camera follows a target (e.g., the player).
    """
    def __init__(self, screen_width, screen_height):
        self.screen_width = screen_width
        self.screen_height = screen_height

    def get_offset(self, target):
        # Calculate an offset so that the player's position is centered.
        offset_x = (self.screen_width / 2) - target.turtle.xcor()
        offset_y = (self.screen_height / 2) - target.turtle.ycor()
        return offset_x, offset_y

class GameEngine:
    def __init__(self):
        self.screen = turtle.Screen()
        self.screen.setup(width=SCALED_SCREEN_WIDTH, height=SCALED_SCREEN_HEIGHT)
        self.screen.tracer(0)  # Manual updates for smoother animation.
        self.levels = self.load_levels()
        self.current_level = None
        self.player = None
        self.camera = Camera(screen_width=SCALED_SCREEN_WIDTH, screen_height=SCALED_SCREEN_HEIGHT)
        self.world_bg = None  # Turtle that displays the pre-rendered world image.

    def load_levels(self):
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
        if level_name not in self.levels:
            print(f"Level '{level_name}' not found!")
            return

        self.fade_out()
        turtle.clearscreen()  # Reset turtle state.
        self.current_level = Level(self.levels[level_name], tile_size=SCALED_TILE_SIZE)
        
        # Create a background turtle to display the pre-rendered world image.
        if self.current_level.world_image_path:
            self.world_bg = turtle.Turtle()
            self.world_bg.shape(self.current_level.world_image_path)
            self.world_bg.penup()
            self.world_bg.speed(0)
        else:
            print("No pre-rendered world image available.")

        # Assume the first object is the player.
        if self.current_level.objects:
            obj = self.current_level.objects[0]
            self.player = Player(texture=obj.texture, start_pos=obj.start_pos, world_path=obj.world_path, tile_size=self.current_level.tile_size)
            self.current_level.objects[0] = self.player

        self.fade_in()

    def fade_out(self):
        fade = turtle.Turtle()
        fade.hideturtle()
        fade.penup()
        fade.speed(0)
        fade.color("black")
        # Use the scaled screen dimensions.
        width, height = SCALED_SCREEN_WIDTH, SCALED_SCREEN_HEIGHT
        turtle.tracer(0)
        for i in range(20):
            fade.clear()
            fade.goto(-width/2, -height/2)
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
        fade = turtle.Turtle()
        fade.hideturtle()
        fade.penup()
        fade.speed(0)
        fade.color("black")
        width, height = SCALED_SCREEN_WIDTH, SCALED_SCREEN_HEIGHT
        turtle.tracer(0)
        for i in range(20, 0, -1):
            fade.clear()
            fade.goto(-width/2, -height/2)
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
        while True:
            if self.player and self.world_bg:
                # Calculate offset to center the view on the player.
                offset_x, offset_y = self.camera.get_offset(self.player)
                # Position the background turtle so that the proper portion of the world image is visible.
                self.world_bg.goto(offset_x, offset_y)
            self.screen.update()
            time.sleep(0.016)  # Approximately 60 FPS.

def main():
    engine = GameEngine()
    if engine.levels:
        first_level = list(engine.levels.keys())[0]
        print(f"Loading level: {first_level}")
        engine.change_level(first_level)
    else:
        print("No levels found in the worlds directory.")
        return
    engine.game_loop()

if __name__ == '__main__':
    main()
