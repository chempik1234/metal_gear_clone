import os, sys, pygame, csv
from base_classes import *
from base_functions import *
from character_classes import *
from item_classes import *
from door_class import Door
from config import *
from math import ceil

mixer = pygame.mixer
mixer.init()

# win = mixer.Sound('data/sounds/win.wav')
# lvl_start = mixer.Sound('data/sounds/lvl_start.wav')
# gas = mixer.Sound('data/sounds/gas.wav')
# bg_bike = mixer.Sound('data/sounds/bike.wav')
# not_gas = mixer.Sound('data/sounds/not_gas.wav')
# bg_music = mixer.Sound('data/sounds/bg_music.mp3')

pygame.init()
screen = pygame.display.set_mode(screen_size)
pygame.display.set_caption('Metal gear')
clock = pygame.time.Clock()


'''
#########################################
########### IMAGES ######################
'''
#########################################
def load_image(name, color_key=None):
    fullname = os.path.join('data/images', name)
    try:
        image = pygame.image.load(fullname)
    except pygame.error as message:
        print('Не могу загрузить изображение:', name)
        raise SystemExit(message)
    if color_key is not None:
        if color_key == -1:
            color_key = image.get_at((0, 0))
            image.set_colorkey(color_key)
        else:
            image.set_colorkey(image.get_at((49, 0)))
    else:
        image = image.convert_alpha()
    return image


tilename_to_image = {}
for i in symbol_to_tilename.values():
    n = i + '/' + i
    tilename_to_image[i] = load_image(n + '.png')
    if tilename_to_has_edge_variation[i]:
        for j in ["left", "right", "Xmiddle"]:
            fucking_fuck = i + "_" + j
            for k in ["up", "down", "Ymiddle"]:
                tilename_to_image[fucking_fuck + "_" + k] = load_image(n + '_' + j + "_" + k + '.png')
    #tilename_to_image[i + "_top"] = load_image(i + '_top.png')
    #tilename_to_image[i + "_bottom"] = load_image(i + '_bottom.png')
tilename_to_image['black'] = load_image('black.png')
'''
########### IMAGES ######################
#########################################
'''


class Game:
    def __init__(self):
        self.location, self.floor, self.room = "building_1", "1", ""
        self.last_chosen_item_index = None
        self.prev_location, self.prev_room = "", ""
        self.anim_frame = 0
        self.NEEDED_FRAMES_FOR_TRANSITION = FPS * 1.5
        ########################################### DOORS CSV ############
        self.doors_dict = {}
        with open(DIR_MAPS + 'doors.csv', newline='') as csvfile:
            doors_csv = csv.reader(csvfile, delimiter=',', quotechar='"')
            self.doors_dict = {}
            for row in doors_csv:
                if row[0] != 'y':
                    dy, dx, b, ltr1, ltl2, wil, wif, wir = row
                    LOC = wil + "_floor_" + wif
                    if wir:
                        LOC += "_room_" + wir
                    if LOC not in self.doors_dict.keys():
                        self.doors_dict[LOC] = {}
                    if b == "1":
                        b = True
                    elif b == "0":
                        b = False
                    self.doors_dict[LOC][dy + "_" + dx] = (b, ltr1, ltl2)
        print(self.doors_dict)
        ######################################### ITEM LOCATIONS CSV #######
        self.items_locations_dict = {}
        with open(DIR_MAPS + 'items.csv', newline='') as csvfile:
            doors_csv = csv.reader(csvfile, delimiter=',', quotechar='"')
            self.items_locations_dict = {}
            for row in doors_csv:
                if row[0] != 'y':
                    iy, ix, loc, rn, flo, name = row
                    LOC = loc + "_floor_" + flo
                    if rn:
                        LOC += "_room_" + rn
                    if LOC not in self.items_locations_dict.keys():
                        self.items_locations_dict[LOC] = {}
                    self.items_locations_dict[LOC][iy + "_" + ix] = name
        print(self.items_locations_dict)
        ######################################### ITEM LOCATIONS CSV #######
        self.paths_dict = {}
        with open(DIR_MAPS + 'paths.csv', newline='') as csvfile:
            paths_csv = csv.reader(csvfile, delimiter=',', quotechar='"')
            self.paths_dict = {}
            for row in paths_csv:
                if row[0] != 'y':
                    iy, ix, loc, rn, flo, paths = row
                    LOC = loc + "_floor_" + flo
                    if rn:
                        LOC += "_room_" + rn
                    if LOC not in self.paths_dict.keys():
                        self.paths_dict[LOC] = {}
                    self.paths_dict[LOC][iy + "_" + ix] = parse_path(paths)
        print(self.paths_dict)


        self.all_gameplay_sprites = pygame.sprite.Group()
        self.sprite_group = pygame.sprite.Group()

        self.npc_group = pygame.sprite.Group()
        self.player_group = pygame.sprite.Group()

        self.items_window_group = pygame.sprite.Group()

        self.sprite_group_list = [self.all_gameplay_sprites,
                                  self.sprite_group,
                                  self.npc_group,
                                  self.player_group,
                                  self.items_window_group,]

        '''
        ######################################################
        ######################################################
        ########### I T E M S ## D E C L A R A T I O N #######
        ######################################################
        ######################################################
        '''
        self.item_name_to_class = {
            'cigarettes': Item("cigarettes", load_image('items/cigarettes.png', -1),
                          (), True, 1, description="This item makes security lasers visible, so they can be dodged."),
            'card_1': Card("card_1", load_image('items/card1.png', -1), 1, ())
        }
        '''
        ######################################################
        #### LOAD ######## SAVED ########### DATA ############
        ######################################################
        '''
        self.dataStore = load_save('data/save.txt')
        self.items_from_save = [self.item_name_to_class[i] for i in self.dataStore['inventory'].split(';') if i]
        self.last_chosen_item_index = int(self.dataStore['chosen_item_index'])
        '''
        ######################################################
        '''

    def generate_level(game_class, level, tilename_to_has_collision, tilename_to_image, symbol_to_tilename,
                       unit_symbols, LOC, need_multyply=False):
        player_x, player_y, map_, item_map = None, None, [], {}
        map_class = Map(map_, tilename_to_image['black'], item_map)
        player_symbol = unit_symbols["player"]
        enemy_symbol = unit_symbols["enemy"]
        if need_multyply:
            level = multiply_level(level, tiles_per_tile_hor, tiles_per_tile_ver, unit_symbols.values(),
                                   tilename_to_symbol["floor"])
        size_y = len(level)
        for y in range(size_y):
            map_.append([])
            size_x = len(level[y])
            for x in range(size_x):
                needed_item_name = None
                symb = level[y][x]
                if symb not in unit_symbols.values() and symb != ITEM_SYMBOL:
                    name = symbol_to_tilename[symb]
                else:
                    name = "floor"
                    if symb in unit_symbols.values():
                        if level[y][x] == player_symbol:
                            if game_class.prev_location or game_class.prev_room:
                                ned_pos = None
                                for xy, to_room_room_loc in game_class.doors_dict[LOC].items():
                                    ltr_, rn_, lc_ = to_room_room_loc
                                    if game_class.prev_room and ltr_:
                                        if game_class.prev_room == rn_:
                                            ned_pos = list(map(int, xy.split("_")))
                                            break
                                    elif game_class.prev_location and not ltr_:
                                        if game_class.prev_location == lc_:
                                            ned_pos = list(map(int, xy.split("_")))
                                            break
                            else:
                                ned_pos = None
                                player_x, player_y = x, y
                        else:
                            paths = game_class.paths_dict[LOC].get(str(y) + "_" + str(x))
                            Person(load_image('solid.png'), 9, 5, x * tile_width, y * tile_height, map_class,
                                   game_class.all_gameplay_sprites, game_class.sprite_group, game_class.npc_group,
                                   hor_tiles_per_second=1.5, ver_tiles_per_second=1.5, paths=paths)
                    elif symb == ITEM_SYMBOL:
                        for yx, item_name in game_class.items_locations_dict[LOC].items():
                            iy, ix = list(map(int, yx.split('_')))
                            if iy == y // tiles_per_tile_ver and ix == x // tiles_per_tile_hor:
                                needed_item_name = item_name
                                break
                img_name = name
                if tilename_to_has_edge_variation.get(name):
                    to_left, to_right = max(0, x - 1), min(x + 1, size_x - 1)
                    if 0 < x < size_x - 1:
                        if level[y][to_left] != symb and symb == level[y][to_right]:
                            img_name += "_left"
                        elif level[y][to_left] == symb and symb == level[y][to_right]:
                            img_name += "_Xmiddle"
                        elif level[y][to_left] == symb and symb != level[y][to_right]:
                            img_name += "_right"
                        else:
                            img_name += "_Xmiddle"  # so far
                    elif x == 0:
                        if symb == level[y][to_right]:
                            img_name += "_Xmiddle"
                        else:
                            img_name += "_right"
                    else:
                        if level[y][to_left] == symb:
                            img_name += "_Xmiddle"
                        else:
                            img_name += "_left"
                    to_up, to_down = max(0, y - 1), min(y + 1, size_y - 1)
                    if 0 < y < size_y - 1:
                        if level[to_up][x] != symb and symb == level[to_down][x]:
                            img_name += "_up"
                        elif level[to_up][x] == symb and symb == level[to_down][x]:
                            img_name += "_Ymiddle"
                        elif level[to_up][x] == symb and symb != level[to_down][x]:
                            img_name += "_down"
                        else:
                            img_name += "_Ymiddle"  # so far
                    elif y == 0:
                        if symb == level[to_down][x]:
                            img_name += "_Ymiddle"
                        else:
                            img_name += "_down"
                    else:
                        if symb == level[to_up][x]:
                            img_name += "_Ymiddle"
                        else:
                            img_name += "_up"
                image = tilename_to_image[img_name]
                if symb not in door_symbols:
                    map_[-1].append(Tile(image, name, x, y, game_class.all_gameplay_sprites, game_class.sprite_group,
                                         tilename_to_has_collision[name]))
                    if needed_item_name:
                        item_map[(y, x)] = ItemTile(game_class.item_name_to_class[needed_item_name], x, y,
                                                    game_class.sprite_group, game_class.all_gameplay_sprites)
                else:
                    if game_class.doors_dict[LOC].get(str(y // tiles_per_tile_ver)
                                                      + "_" +
                                                      str(x // tiles_per_tile_hor)):
                        leads_to_room, room_name, loc_name = game_class.doors_dict[LOC][str(y // tiles_per_tile_ver)
                                                                                        + "_" +
                                                                                        str(x // tiles_per_tile_hor)]
                    else:
                        '''
                        ###############################
                        #### CHECKING DOORS NEARBY ####'''
                        for y_offset in range(-1, 1):
                            for x_offset in range(-1, 1):
                                if y - y_offset <= 0 or x - x_offset <= 0 or x_offset == y_offset == 0:
                                    continue
                                tile = map_[y + y_offset][x + x_offset]
                                if isinstance(tile, Door):
                                    leads_to_room, room_name, loc_name = tile.leads_to_room, tile.room_name,\
                                                                         tile.location_name
                                    break
                    map_[-1].append(Door(image, name, x, y, game_class.all_gameplay_sprites, game_class.sprite_group,
                                         leads_to_room, room_name, loc_name, tilename_to_has_collision[name],
                                         door_symbol_to_number[symb]))
        if ned_pos:
            dir_ = None  # how to enter the door: #1 <- @ = left
            dy, dx = ned_pos
            col_to_up, col_to_down, col_to_left, col_to_right = False, False, False, False
            y_up, y_down, x_left, x_right = dy, None, dx, None
            #########
            if dy > 0 and map_[max(0, dy - 1)][dx].has_collisions:
                col_to_up = True
            elif dy == 0:
                col_to_up = True
            #########
            for yyy in range(dy + 1, len(map_)):
                if not isinstance(map_[yyy - 1][dx], Door):
                    break
                if isinstance(map_[yyy][dx], Door):
                    y_down = yyy
                elif map_[yyy][dx].has_collisions:
                    col_to_down = True
                    break
            if y_down == len(map_) - 1:
                col_to_down = True
            #########
            if dx > 0 and map_[dy][dx - 1].has_collisions:
                col_to_left = True
            elif dx == 0:
                col_to_left = True
            #########
            for xxx in range(dx + 1, len(map_[dy])):
                if not isinstance(map_[dy][xxx - 1], Door):
                    break
                if isinstance(map_[dy][xxx], Door):
                    x_right = xxx
                elif map_[dy][xxx].has_collisions:
                    col_to_right = True
                    break
            if x_right == len(map_[dy]) - 1:
                col_to_right = True
            #########
            if col_to_up and col_to_down:
                if col_to_left:
                    dir_ = LEFT
                elif col_to_right:
                    dir_ = RIGHT
            else:
                if col_to_up:
                    dir_ = UP
                elif col_to_down:
                    dir_ = DOWN
            if dir_ == UP:
                player_x = (x_left + x_right) // 2
                player_y = y_down  # + 1
            elif dir_ == DOWN:
                player_x = (x_left + x_right) // 2
                player_y = y_up - 3
            elif dir_ == LEFT:
                player_x = x_left - 1
                player_y = (y_up + y_down) // 2
            elif dir_ == RIGHT:
                player_x = x_right + 1
                player_y = (y_up + y_down) // 2
        return player_x, player_y, map_class

    def render(self, window, camera, all_sprites, sprite_group, Ysprites):
        tick = clock.tick(FPS)
        if window == GAMEPLAY:
            screen.fill(pygame.Color('blue'))
            for i in list(self.player_group) + list(self.npc_group):
                i.update()

            sprite_group.draw(screen)
            Ysprites.draw(screen)

            camera.update(self.player_character)
            for sprite in all_sprites:
                camera.apply(sprite)
            #### item
            pygame.draw.rect(screen, pygame.Color('black'), (WIDTH * 0.8, HEIGHT * 0.8, WIDTH * 0.15, HEIGHT * 0.15))
            draw_text(["ITEM"], HEIGHT * 0.912, WIDTH * 0.81, int(HEIGHT * 0.038), pygame.Color('white'), screen)
            screen.fill(pygame.Color("orange"),
                        (int(WIDTH * 0.93), int(HEIGHT * 0.81), int(WIDTH * 0.01), int(HEIGHT * 0.11)))
            screen.fill(pygame.Color("orange"),
                        (int(WIDTH * 0.93), int(HEIGHT * 0.93), int(WIDTH * 0.01), int(HEIGHT * 0.01)))
            if self.player_character.chosen_item_index >= 0:
                dat_item = self.player_character.inventory[self.player_character.chosen_item_index]
                dat_item.rect = pygame.Rect(WIDTH * 0.81, HEIGHT * 0.81, WIDTH * 0.13, HEIGHT * 0.08)
                dat_item.draw(screen)
                if dat_item.usable:
                    draw_text([str(dat_item.amount)], HEIGHT * 0.83, WIDTH * 0.89, int(HEIGHT * 0.1), pygame.Color('white'),
                              screen)
            ### life bar
            xx, yy, ww, hh, full_hh = int(WIDTH * 0.05), int(HEIGHT * 0.85), WIDTH // 3, int(HEIGHT * 0.05), \
                                      int(HEIGHT * 0.08)
            life_x, life_y, life_w, life_h = xx + int(WIDTH * 0.015), yy + int(HEIGHT * 0.005), ww - int(WIDTH * 0.02), \
                                             hh - int(HEIGHT * 0.03)
            screen.fill(pygame.Color('black'), (xx, yy, ww, full_hh))
            screen.fill(pygame.Color('green'), (xx + int(WIDTH * 0.005), yy + int(HEIGHT * 0.005),
                                                int(WIDTH * 0.005), hh - int(HEIGHT * 0.02)))
            screen.fill(pygame.Color('darkgreen'), (xx + int(WIDTH * 0.005), yy + hh - int(HEIGHT * 0.02),
                                                    ww - int(WIDTH * 0.01), int(HEIGHT * 0.01)))
            screen.fill(pygame.Color('darkgreen'), (life_x, life_y, life_w, life_h))
            screen.fill(pygame.Color('green'), (life_x, life_y,
                                                life_w * self.player_character.health / self.player_character.max_health, life_h))
            font = full_hh - hh
            draw_text(['LIFE'], yy + hh, xx + int(WIDTH * 0.005), font, pygame.Color('white'), screen)
        elif window == ITEMS:
            screen.fill(pygame.Color('black'))
            self.items_window_group.empty()
            for i in self.player_character.inventory:
                self.items_window_group.add(i)
            items_amount = len(self.player_character.inventory)
            rows = int(HEIGHT * 0.7) // max([i.image.get_width() for i in self.player_character.inventory])
            # all_pixels = items_amount * max([i.image.get_width() for i in player_character.inventory])
            columns = ceil(items_amount / rows)
            # rows = ceil(items_amount / columns)
            for col in range(columns):
                for row in range(rows):
                    index = rows * col + row
                    if index >= items_amount:
                        break
                    dat_item = self.player_character.inventory[index]
                    w, h = dat_item.image.get_width(), dat_item.image.get_height()
                    x, y = col * w + max(0, MARGIN * (col - 1)), row * h
                    dat_item.rect = pygame.Rect(x, y, w, h)
                    if index == self.player_character.chosen_item_index:
                        pygame.draw.rect(screen, pygame.Color('gray'), dat_item.rect)
                    if dat_item.usable:
                        draw_text([str(dat_item.amount)], y + h - FONTS[SMALL], x + w, FONTS[SMALL],
                                  pygame.Color('white'), screen)
            #### desc
            xx, yy, ww, hh = 0, int(HEIGHT * 0.7), WIDTH, HEIGHT - int(HEIGHT * 0.7)
            screen.fill(pygame.Color("white"), (xx, yy, ww, hh))
            screen.fill(pygame.Color("black"),
                        (xx + int(WIDTH * 0.005), yy + int(HEIGHT * 0.005), ww - int(WIDTH * 0.01),
                         hh - int(HEIGHT * 0.01)))
            desc, font = self.player_character.inventory[self.player_character.chosen_item_index].description, int(HEIGHT * 0.05)
            listt = divide_text_to_strings_depending_on_max_width(desc, font, ww * 0.99)
            draw_text(listt, yy + int(HEIGHT * 0.003), int(WIDTH * 0.005), font, pygame.Color('white'), screen)
            self.items_window_group.draw(screen)
        elif window == MOVING_TO_NEXT_LOCATION_WINDOW:
            col = int(self.anim_frame / self.NEEDED_FRAMES_FOR_TRANSITION * 255) // 2
            screen.fill(pygame.Color(col, col, col))
            sssghoul = ["QUICKLY MOVING TO:", "Location: " + self.location]
            if self.room:
                sssghoul.append('Room: ' + self.room)
            draw_text(sssghoul, HEIGHT * 0.4, WIDTH * 0.1, int(HEIGHT * 0.1),
                      pygame.Color(255 - col, 255 - col, 255 - col), screen)
            self.anim_frame += 1

        draw_text(['FPS: ' + str(int(1000 / tick))], 10, 560, FONTS[SMALL], pygame.Color('white'), screen)
        pygame.display.flip()

    def play_level(self):
        for i in self.sprite_group_list:
            i.empty()
        window = GAMEPLAY
        LOC = self.location + "_floor_" + self.floor
        if self.room:
            LOC += "_room_" + self.room
        px, py, map_class = self.generate_level(multiply_level(load_level(DIR_MAPS + LOC),
                                                          tiles_per_tile_ver, tiles_per_tile_hor,
                                                          unit_symbols, '.'),
                                           tilename_to_has_collision, tilename_to_image,
                                           symbol_to_tilename, unit_symbols, LOC)
        self.player_character = Person(load_image('solid.png'), 9, 5, px * tile_width, py * tile_height, map_class,
                                       self.all_gameplay_sprites, self.sprite_group, self.player_group,
                                       inventory=self.items_from_save, chosen_item_index=self.last_chosen_item_index,
                                       is_npc=False)
        Ysprites = YAwareGroup(*[i for i in list(self.npc_group) + list(self.player_group)])
        camera = Camera()
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    terminate()
                # elif event.type == pygame.MOUSEBUTTONDOWN:  # [1|2|3]
                #     if event.button == 1:
                #         player_character.punch()
                elif event.type == pygame.KEYDOWN:
                    if window == GAMEPLAY:
                        if event.key == keyboard_controls[LEFT] and event.key != keyboard_controls[RIGHT]:
                            self.player_character.set_l_r_inertion(-1)
                        elif event.key == keyboard_controls[RIGHT] and event.key != keyboard_controls[LEFT]:
                            self.player_character.set_l_r_inertion(1)
                        elif event.key == keyboard_controls[UP] and event.key != keyboard_controls[DOWN]:
                            self.player_character.set_up_down_inertion(1)
                        elif event.key == event.key == keyboard_controls[DOWN] and event.key != keyboard_controls[UP]:
                            self.player_character.set_up_down_inertion(-1)
                        elif event.key == keyboard_controls[PUNCH]:
                            self.player_character.punch()
                        elif event.key == keyboard_controls[USE]:
                            itemmmm = self.player_character.inventory[self.player_character.chosen_item_index]
                            if itemmmm.usable:
                                itemmmm.use()
                            if itemmmm.amount <= 0:
                                self.player_character.inventory.remove(itemmmm)
                    elif window == ITEMS:
                        if event.key == keyboard_controls[UP]:
                            self.player_character.chosen_item_index = max(0, self.player_character.chosen_item_index - 1)
                        elif event.key == keyboard_controls[DOWN]:
                            self.player_character.chosen_item_index = min(len(self.player_character.inventory) - 1,
                                                                          self.player_character.chosen_item_index + 1)
                    for i in WINDOWS:
                        if i == GAMEPLAY or not keyboard_controls.get(i):
                            continue
                        if event.key == keyboard_controls[i]:
                            if window != i:
                                window = i
                            else:
                                window = GAMEPLAY
                            break
                elif event.type == pygame.KEYUP:
                    if event.key == pygame.K_w or \
                            event.key == pygame.K_s:
                        self.player_character.set_up_down_inertion(0)
                    if event.key == pygame.K_a or \
                            event.key == pygame.K_d:
                        self.player_character.set_l_r_inertion(0)
            player_tile = self.player_character.tile_class
            if isinstance(player_tile, Door):
                if player_tile.opened and window != MOVING_TO_NEXT_LOCATION_WINDOW:
                    self.prev_room, self.prev_location = self.room, self.location
                    self.last_chosen_item_index = self.player_character.chosen_item_index
                    self.anim_frame = 0
                    window = MOVING_TO_NEXT_LOCATION_WINDOW
                    if player_tile.leads_to_room:
                        self.room = player_tile.room_name
                    else:
                        self.location = player_tile.location_name
                        self.room = player_tile.room_name
            if self.anim_frame >= self.NEEDED_FRAMES_FOR_TRANSITION:
                self.anim_frame = 0
                return
            self.render(window, camera, self.all_gameplay_sprites, self.sprite_group, Ysprites)

    def run(self):
        while True:
            self.play_level()


#while not game(levels_amount):
#    pass
#if not compl_game:
#    compl_game = True
#    finish_game()
# with open('data/save.txt', 'w') as f:
#     f.write(f'''level={your_levels}
# max_points={your_record}
# game_completed={compl_game}''')
if __name__ == '__main__':
    game = Game()
    game.run()
pygame.quit()