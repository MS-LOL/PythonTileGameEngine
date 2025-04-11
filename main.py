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
################################# LOAD PLAYER AND SPRITESHEET###################################
spritesheet = Spritesheet('spritesheet.png')
player_img = spritesheet.parse_sprite('chick.png')
player_rect = player_img.get_rect()

#################################### LOAD THE LEVEL #######################################
map = TileMap('test_level.csv', spritesheet )
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









