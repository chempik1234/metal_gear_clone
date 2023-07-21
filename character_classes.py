from base_classes import Sprite, ItemTile
from door_class import Door
from item_classes import Card
import pygame
from config import *


def is_moving_to_str(a):
    return "idle" if not a else "move"


class Person(Sprite):
    def __init__(self, sheet, columns, rows, x, y, map_class, all_sprites, sprite_group, special_sprite_group,
                 hor_tiles_per_second=SPEED_HOR, ver_tiles_per_second=SPEED_VER, max_health=50, punch_damage=5,
                 inventory=[], is_npc=True, chosen_item_index=0, paths=[], view_range=2, view_angle_tiles=2):
        super().__init__((all_sprites, special_sprite_group))

        self.special_srite_group = special_sprite_group
        self.sprite_group = sprite_group
        self.all_sprites = all_sprites

        self.frames = {}
        self.cut_sheet(sheet, columns, rows)
        self.cur_frame = 0
        self.frames_10 = 0

        self.can_set_inertion = True
        self.state = IDLE
        self.direction = RIGHT

        self.image = self.get_frame()
        self.mask = pygame.mask.from_surface(self.image)

        self.rect = self.image.get_rect().move(tile_width * x,
                                               tile_height * y)
        self.center = (self.rect.x + self.rect.w / 2, self.rect.y + self.rect.h)
        #self.rect = self.rect.move(x, y)
        self.origin_x = x
        self.origin_y = y

        self.map = map_class
        self.prev_left_cell = ()
        self.cur_left_cell = ()
        self.prev_right_cell = ()
        self.cur_right_cell = ()
        self.prev_middle_cell = ()
        self.cur_middle_cell = ()
        self.faced_cell = ()
        gett = self.get_cell()
        self.cur_left_cell = (gett[: 2])
        self.cur_right_cell = (gett[3: 5])
        self.cur_middle_cell = (gett[6: 8])
        self.faced_cell = gett[9]
        self.tile_class = gett[10]

        self.max_health = max_health
        self.health = max_health
        self.punch_damage = punch_damage

        self.Hspeed = hor_tiles_per_second  # * tile_width #  * tiles_per_tile_hor ** 0.5
        self.Vspeed = ver_tiles_per_second  # * tile_height #  * tiles_per_tile_ver ** 0.5
        self.down_up_inertion = 0  # up - -1, down - 1
        self.left_right_inertion = 0  # right - 1, left - -1
        self.last_du, self.last_lr = 0, 0
        self.collis_dir = self.get_col_dir()

        self.inventory = inventory
        self.chosen_item_index = chosen_item_index

        self.is_npc = is_npc
        self.paths = paths
        self.cur_path_point_index = 0
        self.prev_path_point = None
        self.next_path_point = None

        self.alarm = False
        self.view_range_h = view_range * tile_height
        self.view_range_w = view_range * tile_width
        self.view_angle_tiles = view_angle_tiles

    def cut_sheet(self, sheet, columns, rows):
        frames = []
        darect = pygame.Rect(0, 0, sheet.get_width() // columns, sheet.get_height() // rows)  # with borders!!!!
        for j in range(rows):  # created frames mustn't have these!!!!
            for i in range(columns):
                frame_location = (darect.w * i, darect.h * j)
                image = sheet.subsurface(pygame.Rect(frame_location, (darect.w - 1, darect.h - 1)))
                color_key = (255, 0, 238, 255)
                image.set_colorkey(color_key)
                frames.append(image)
        self.frames = {a_b(IDLE, RIGHT): [frames[0]], a_b(MOVE, RIGHT): frames[1: 3],
                       a_b(IDLE, DOWN): [frames[3]], a_b(MOVE, DOWN): frames[4: 6],
                       a_b(IDLE, UP): [frames[6]], a_b(MOVE, UP): frames[7: 9],
                       a_b(IDLE, LEFT): [frames[9]], a_b(MOVE, LEFT): frames[10: 12],

                       a_b(PUNCH, RIGHT): frames[12: 14], a_b(PUNCH, DOWN): frames[14: 16],
                       a_b(PUNCH, UP): frames[16: 18], a_b(PUNCH, LEFT): frames[18: 20],

                       a_b(STUNNED, RIGHT): [frames[20]], a_b(STUNNED, DOWN): [frames[21]],
                       a_b(STUNNED, UP): [frames[22]], a_b(STUNNED, LEFT): [frames[23]],
                       }

    def update_states(self):
        if self.state != PUNCH:
            if self.last_lr > 0:
                self.direction = RIGHT
            elif self.last_lr < 0:
                self.direction = LEFT
            elif self.last_du < 0:
                self.direction = DOWN
            elif self.last_du > 0:
                self.direction = UP
            if self.left_right_inertion != 0 or self.down_up_inertion != 0:
                self.state = MOVE
            else:
                self.state = IDLE

    def get_frame(self):
        anim_folder = self.frames[a_b(self.state, self.direction)]
        f10 = STATE_TO_FRAME_10[self.state]
        if self.frames_10 < f10:
            self.frames_10 += 1
        else:
            if self.cur_frame == len(anim_folder) - 1:
                self.state = STATES_TO_NEXT_STATE[self.state]
            self.frames_10 = 0
            self.cur_frame = (self.cur_frame + 1) % len(anim_folder)
        self.cur_frame = min(self.cur_frame, len(anim_folder) - 1)
        return anim_folder[self.cur_frame]

    def get_cell(self):
        if self.map == [[]]:
            return 0, 0, False
        ##############
        l_tile_x, l_tile_y = int(self.origin_x // tile_width),\
                         int((self.origin_y + self.rect.h) // tile_height)
        l_tile_y = max(min(len(self.map) -1, l_tile_y), 0)
        l_tile_x = max(min(len(self.map[l_tile_y]) - 1, l_tile_x), 0)
        cur_left_cell = (l_tile_x, l_tile_y)
        if self.cur_left_cell != cur_left_cell:
            self.prev_left_cell = self.cur_left_cell
        self.cur_left_cell = cur_left_cell
        ##############
        r_tile_x, r_tile_y = int((self.origin_x + self.rect.w) // tile_width),\
                         int((self.origin_y + self.rect.h) // tile_height)
        r_tile_y = max(min(len(self.map) -1, r_tile_y), 0)
        r_tile_x = max(min(len(self.map[r_tile_y]) - 1, r_tile_x), 0)
        cur_right_cell = (r_tile_x, r_tile_y)
        if self.cur_right_cell != cur_right_cell:
            self.prev_right_cell = self.cur_right_cell
        self.cur_right_cell = cur_right_cell
        ##############
        m_tile_x = int(int(self.origin_x + self.rect.w / 2) // tile_width)
        m_tile_x = max(min(m_tile_x, self.cur_right_cell[0]), self.cur_left_cell[0])
        m_tile_y = self.cur_left_cell[1]
        cur_middle_cell = (m_tile_x, m_tile_y)
        if self.cur_middle_cell != cur_middle_cell:
            self.prev_middle_cell = self.cur_middle_cell
        self.cur_middle_cell = cur_middle_cell
        ##############
        if self.direction == DOWN:
            self.faced_cell = (self.cur_middle_cell[0], self.cur_middle_cell[1] + 1)
        elif self.direction == UP:
            self.faced_cell = (self.cur_middle_cell[0], self.cur_middle_cell[1] - 1)
        elif self.direction == LEFT:
            self.faced_cell = (self.cur_middle_cell[0] - 1, self.cur_middle_cell[1])
        elif self.direction == RIGHT:
            self.faced_cell = (self.cur_middle_cell[0] + 1, self.cur_middle_cell[1])
        ################################################
        self.center = (self.rect.x + self.rect.w / 2, self.rect.y + self.rect.h)
        self.tile_class = self.map[m_tile_y][m_tile_x]
        itemm = self.map.get_item(self.cur_middle_cell[1], self.cur_middle_cell[0])
        if itemm:
            itemm.kill()
            if itemm.represented_item not in self.inventory:
                self.inventory.append(itemm.represented_item)
        ################################################
        return l_tile_x, l_tile_y, self.map[l_tile_y][l_tile_x].has_collisions,\
               r_tile_x, r_tile_y, self.map[r_tile_y][r_tile_x].has_collisions,\
               m_tile_x, m_tile_y, self.map[m_tile_y][m_tile_x].has_collisions,\
               self.faced_cell, self.map[m_tile_y][m_tile_x]

    def check_collisions(self):
        gett = self.get_cell()
        having_collisions = gett[2] or gett[5]
        #having_collisions = any([pygame.sprite.collide_mask(self, i) for i in self.sprite_group
        #                         if i.has_collisions and
        #                         abs(i.rect.x - self.rect.x) < tile_width and
        #                         abs(i.rect.y - self.rect.y) < tile_height])
        return having_collisions

    def get_col_dir(self):
        if not (self.prev_left_cell or self.prev_right_cell):
            return self.direction
        elif not self.prev_left_cell:
            dir = self.prev_right_cell
            dir1 = self.cur_right_cell
        elif not self.prev_right_cell:
             dir = self.prev_left_cell
             dir1 = self.cur_left_cell
        else:
            gett = self.get_cell()
            c0, c1 = gett[2], gett[5]
            if c0:
                dir = self.prev_left_cell
                dir1 = self.cur_left_cell
            elif c1:
                dir = self.prev_right_cell
                dir1 = self.cur_right_cell
            else:
                return self.direction
        x0, y0, x1, y1 = dir[0], dir[1], dir1[0], dir1[1]
        if x0 < x1:
            return RIGHT
        elif x1 < x0:
            return LEFT
        elif y0 < y1:
            return DOWN
        elif y1 < y0:
            return UP

    def take_damage(self, damage):
        if self.state != STUNNED:
            self.health -= damage
            self.frames_10 = 0
            self.state = STUNNED
        if self.health <= 0 and self.is_npc:
            self.kill()

    def update(self):
        if len(self.inventory) <= self.chosen_item_index:
            self.chosen_item_index = len(self.inventory) - 1
        if len(self.inventory) > 0 > self.chosen_item_index:
            self.chosen_item_index = 0
        self.get_cell()
        if self.is_npc:
            if self.cur_middle_cell == self.next_path_point:
                self.cur_path_point_index = (self.cur_path_point_index + 1) % len(self.paths)
                self.prev_path_point = self.next_path_point
                self.next_path_point = None
            cpp = self.paths[self.cur_path_point_index]
            if not self.prev_path_point:
                self.prev_path_point = self.cur_middle_cell
            if self.paths and not self.next_path_point:
                xof, yof = 0, 0
                for i in cpp:
                    if i[0] == 'U':
                        yof -= int(i[1:])
                    if i[0] == 'D':
                        yof += int(i[1:])
                    if i[0] == 'L':
                        xof -= int(i[1:])
                    if i[0] == 'R':
                        xof += int(i[1:])
                self.next_path_point = (self.prev_path_point[0] + xof, self.prev_path_point[1] + yof)
            if self.cur_middle_cell[1] > self.next_path_point[1]:
                self.set_up_down_inertion(1)
            elif self.cur_middle_cell[1] < self.next_path_point[1]:
                self.set_up_down_inertion(-1)
            else:
                self.set_up_down_inertion(0)
            if self.cur_middle_cell[0] > self.next_path_point[0]:
                self.set_l_r_inertion(-1)
            elif self.cur_middle_cell[0] < self.next_path_point[0]:
                self.set_l_r_inertion(1)
            else:
                self.set_l_r_inertion(0)
        v, h = self.down_up_inertion * self.Vspeed, self.left_right_inertion * self.Hspeed
        self.origin_x += h
        self.origin_y -= v
        faced_cell_class = self.map[self.faced_cell[1]][self.faced_cell[0]]
        if isinstance(faced_cell_class, Door):
            faced_cell_class.open(self)
        if self.check_collisions():
            self.collis_dir = self.get_col_dir()
        while self.check_collisions():
            self.can_set_inertion = False
            if self.collis_dir == LEFT:
                self.origin_x += max(1, h)
                self.rect.left += max(1, h)
                self.set_l_r_inertion(0)
            elif self.collis_dir == RIGHT:
                self.origin_x -= max(1, h)
                self.rect.left -= max(1, h)
                self.set_l_r_inertion(0)

            if self.collis_dir == DOWN:
                self.rect.top -= max(1, v)
                self.origin_y -= max(1, v)
                self.set_up_down_inertion(0)
            elif self.collis_dir == UP:
                self.rect.top += max(1, v)
                self.origin_y += max(1, v)
                self.set_up_down_inertion(0)
        if self.state == PUNCH and self.can_set_inertion:
            self.set_l_r_inertion(0, True)
            self.set_up_down_inertion(0, True)
            self.can_set_inertion = False
        else:
            self.can_set_inertion = True
        if self.state == PUNCH:
            npcs = [x for x in list(self.all_sprites) if isinstance(x, Person)]
            offset_x = tile_width * 2
            offset_y = tile_height * 2
            if self.direction == RIGHT:
                for i in npcs:
                    if i.state == STUNNED:
                        continue
                    if (i.origin_x > self.origin_x and i.origin_x - self.origin_x <= offset_x) and\
                            abs(i.origin_y - self.origin_y) <= offset_y / 3:
                        i.take_damage(self.punch_damage)
            elif self.direction == LEFT:
                for i in npcs:
                    if i.state == STUNNED:
                        continue
                    if (i.origin_x < self.origin_x and self.origin_x - i.origin_x <= offset_x) and\
                            abs(i.origin_y - self.origin_y) <= offset_y / 3:
                        i.take_damage(self.punch_damage)
            elif self.direction == UP:
                for i in npcs:
                    if i.state == STUNNED:
                        continue
                    if (i.origin_y < self.origin_y and self.origin_y - i.origin_y <= offset_y) and\
                            abs(i.origin_x - self.origin_x) <= offset_y / 3:
                        i.take_damage(self.punch_damage)
            elif self.direction == DOWN:
                for i in npcs:
                    if i.state == STUNNED:
                        continue
                    if (i.origin_y > self.origin_y and i.origin_y - self.origin_y <= offset_y) and\
                            abs(i.origin_x - self.origin_x) <= offset_y / 3:
                        i.take_damage(self.punch_damage)
        self.image = self.get_frame()
        self.mask = pygame.mask.from_surface(self.image)
        for i in [x for x in list(self.all_sprites) if isinstance(x, Person)]:
            if self.direction == RIGHT:
                print(i.rect.x - self.rect.x <= self.view_range_w, abs(i.rect.y - self.rect.y) <= tile_height * self.view_angle_tiles)
                if i.rect.x - self.rect.x <= self.view_range_w and \
                        abs(i.rect.y - self.rect.y) <= tile_height * self.view_angle_tiles:
                    self.alarm_on()
            elif self.direction == LEFT:
                if self.rect.x - i.rect.x <= self.view_range_w and \
                        abs(i.rect.y - self.rect.y) <= tile_height * self.view_angle_tiles:
                    self.alarm_on()
            elif self.direction == UP:
                if self.rect.y - i.rect.y <= self.view_range_h and \
                        abs(i.rect.x - self.rect.x) <= tile_width * self.view_angle_tiles:
                    self.alarm_on()
            elif self.direction == DOWN:
                if i.rect.y - self.rect.y <= self.view_range_h and \
                        abs(i.rect.x - self.rect.x) <= tile_width * self.view_angle_tiles:
                    self.alarm_on()

    def punch(self):
        if self.state != PUNCH:
            self.state = PUNCH
            self.frames_10 = 0

    def set_up_down_inertion(self, value, important=False):
        if (not self.can_set_inertion or self.state == PUNCH) and not important:
            return
        self.down_up_inertion = value
        if value != 0:
            self.left_right_inertion = 0
            self.last_du = value
            self.last_lr = 0
        self.update_states()

    def set_l_r_inertion(self, value, important=False):
        if (not self.can_set_inertion or self.state == PUNCH) and not important:
            return
        self.left_right_inertion = value
        if value != 0:
            self.down_up_inertion = 0
            self.last_lr = value
            self.last_du = 0
        self.update_states()

    def alarm_on(self):
        if not self.alarm:
            print("!")
            #self.alarm = True