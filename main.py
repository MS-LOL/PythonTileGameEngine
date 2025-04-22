from tiles import *
from spritesheet import Spritesheet


################################# LOAD UP A BASIC WINDOW AND CLOCK #################################
pygame.init()
DISPLAY_W, DISPLAY_H = 512, 288
SCALE_FACTOR = 2
SCALED_W, SCALED_H = DISPLAY_W * SCALE_FACTOR, DISPLAY_H * SCALE_FACTOR

surfaces = {
    "world": pygame.Surface((DISPLAY_W, DISPLAY_H)),
    "mainmenu": pygame.Surface((DISPLAY_W, DISPLAY_H)),
    "settingsmenu": pygame.Surface((DISPLAY_W, DISPLAY_H)),
    "levelselectmanu": pygame.Surface((DISPLAY_W, DISPLAY_H)),
    "campaignselectmenu": pygame.Surface((DISPLAY_W, DISPLAY_H)),
    "creditsmenu": pygame.Surface((DISPLAY_W, DISPLAY_H)),
    "gameover": pygame.Surface((DISPLAY_W, DISPLAY_H)),
    "pausemenu": pygame.Surface((DISPLAY_W, DISPLAY_H)),
    "loadingscreen": pygame.Surface((DISPLAY_W, DISPLAY_H)),
    "overlay": pygame.Surface((DISPLAY_W, DISPLAY_H), pygame.SRCALPHA)  # Transparent overlay
}

active_surface = "mainmenu"  # Set the initial active surface
# Set the initial active surface to "mainmenu"

window = pygame.display.set_mode(((SCALED_W, SCALED_H)))
running = True
clock = pygame.time.Clock()
pygame.display.set_caption("Chick Game")
################################## DEBUG VARIABLES #################################
lock_surface = False # Set to True to lock the surface to the currently active surface
# Set to False to allow switching between surfaces
freecam = False # Set to True to allow free camera movement, even if the player is not moving
# Set to False to restrict camera movement to gameplay rules
no_clip = False # Set to True to disable wall collision detection, allowing the player to move through walls and other obstacles
# Set to False to enable wall collision detection, preventing the player from moving through walls and other obstacles
true_no_collision = False # Set to True to disable all collision detection, making the player undetectable to all collision and trigger events
# Set to False to enable collision detection, allowing the player to interact with other objects in the game world via collision and trigger events
trigger_debug_checkpoint = False # Set to True to trigger a breakpoint with the breakpoint() function
# Upon continuing, this variable will be set to False again
################################# LOAD PLAYER AND SPRITESHEET###################################
spritesheet = Spritesheet('spritesheet.png')
player_img = spritesheet.parse_sprite('chick.png')
player_rect = player_img.get_rect()

#################################### LOAD THE LEVEL ############################################
map = TileMap('test_level.csv', spritesheet )
#################################### SET THE STARTING POSITION OF THE PLAYER ###################
player_rect.x, player_rect.y = map.start_x, map.start_y

################################# GAME LOOP ##########################
while running:
    clock.tick(60)
    ################################# CHECK PLAYER INPUT #################################
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            pass
        #     if event.key == pygame.K_LEFT:
        #         player.LEFT_KEY, player.FACING_LEFT = True, True
        #     elif event.key == pygame.K_RIGHT:
        #         player.RIGHT_KEY, player.FACING_LEFT = True, False
        #
        # if event.type == pygame.KEYUP:
        #     if event.key == pygame.K_LEFT:
        #         player.LEFT_KEY = False
        #     elif event.key == pygame.K_RIGHT:
        #         player.RIGHT_KEY = False

    ################################# UPDATE/ Animate SPRITE #################################

    ################################# UPDATE WINDOW AND DISPLAY #################################
    canvas.fill((0, 180, 240)) # Fills the entire screen with light blue
    map.draw_map(canvas)
    canvas.blit(player_img, player_rect)

    scaled_canvas = pygame.transform.scale(canvas, (SCALED_W, SCALED_H))
    window.blit(scaled_canvas, (0,0))
    pygame.display.update()
    ################################## DEBUGGING #################################
    if trigger_debug_checkpoint:
        breakpoint()
        # Hey there! If you see this, it means that you have triggered a breakpoint.
        # You can use this to inspect and modify variables at this point in time. (e.g. forcing a scene change to the loading screen)
        # You can also use this to inspect the current state of the game and see how [THAT WORD WILL[40% OFF] ME!] the player is.
        # If you triggered this by accident, just type "continue" in the console to continue the game.
        # If you triggered this by accident but now you're curious about what happens behind the scenes, open up the scripts in editors like VSCode or PyCharm and see the code documented right next to the code itself.
        # If you are massochistic enough to want to navigate this turing tarpit of an excuse of a game engine, call 0800-555-5555 and ask to schedule a lobotomy.
        # I would say have fun, but I don't think you will. Neither will I say good luck, because it won't make a difference.
        # I will say this: If you are reading this, you are either a developer or a masochist. Either way, I hope you have a good day.
        #
        # When I started making this game, the only person who could best understand this code was me.
        # Now, only my classmates can understand this code, and there is a reason that only AC took Computer Science GCSE and even he is regretting his decision.
        #
        # These ridigulously long comments are courtesy of VSCode's autocomplete AI, which leads the Department of Redundancy Department.
        # -LM
        trigger_debug_checkpoint = False









