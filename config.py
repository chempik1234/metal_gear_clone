import pygame
WIDTH = 640
HEIGHT = 480
screen_size = (WIDTH, HEIGHT)
FPS = 50
tile_width = tile_height = 25
tiles_per_tile_ver = 1
tiles_per_tile_hor = 1
SPEED_VER, SPEED_HOR = 2, 2
#####
GAMEPLAY = "gameplay"
ITEMS = "items"
MOVING_TO_NEXT_LOCATION_WINDOW = "moving_to_next_location_window"
WINDOWS = [GAMEPLAY, ITEMS, MOVING_TO_NEXT_LOCATION_WINDOW]
#####
LEFT, RIGHT, UP, DOWN, IDLE, MOVE, PUNCH, STUNNED, USE = "left", "right", "up", "down", "idle", "move", "punch",\
                                                         "stunned", "use"
keyboard_controls = {LEFT: pygame.K_a,
                     RIGHT: pygame.K_d,
                     UP: pygame.K_w,
                     DOWN: pygame.K_s,
                     ITEMS: pygame.K_3,
                     PUNCH: pygame.K_q,
                     USE: pygame.K_e}
MARGIN = 20
SMALL, BIG = "SMALL", "BIG"
FONTS = {SMALL: 20, BIG: 40}
'''
##########################################'''
unit_symbols = {"player": "@",
                "enemy": "!"}
door_symbols = '0123456789'
symbol_to_tilename = {"#": "brick",
                      ".": "floor",
                      "=": "crate",
                      '-': 'crate_bottom',
                      '$': 'ceil',}
ITEM_SYMBOL = '?'
'''##########################################
'''
door_symbols_string = '0q1z2x3c4v5b6n7m8,'
# door_symbols = {}
door_symbol_to_number = {}
for i in range(len(door_symbols_string) // 2):
#     card_symbol_to_number[i * 2 + 1] =
    # door_symbols["door_{0}_top".format(i)] = door_symbols_string[i * 2]
    # door_symbols["door_{0}_bottom".format(i)] = door_symbols_string[i * 2 + 1]
    door_symbol_to_number[door_symbols_string[i * 2]] = i
    door_symbol_to_number[door_symbols_string[i * 2 + 1]] = i
    symbol_to_tilename[str(i)] = 'door'
STATE_TO_FRAME_10 = {IDLE: 10, MOVE: 10, PUNCH: 5, STUNNED: 10}
STATES_TO_NEXT_STATE = {MOVE: MOVE, IDLE: IDLE, PUNCH: IDLE, STUNNED: IDLE}

tilename_to_symbol = {i[1]: i[0] for i in symbol_to_tilename.items()}
#  tilename_to_image is in main.py
tilename_to_has_edge_variation = {"brick": True,
                                  "floor": False,
                                  "door": True,
                                  "crate": True,
                                  'crate_bottom': True,
                                  'ceil': True,}
tilename_to_has_collision = {'brick': True,
                             'floor': False,
                             'door': True,
                             'crate': True,
                             'crate_bottom': True,
                             'ceil': True}
DIR_MAPS = 'data/levels/'


def a_b(a, b):
    return a + "_" + b
