import pygame, os, sys
from base_classes import Tile
from character_classes import Person
from config import *


def click_rect(xy, xywh):
    x, y = xy
    x1, y1, w, h = xywh
    return 0 <= x - x1 <= w and 0 <= y - y1 <= h


def terminate():
    pygame.quit()
    sys.exit()


##########


def load_save(filename):
    try:
        with open(filename, 'r') as f:  # 'data/save.txt'
            s = [i.split('=') for i in f.read().split('\n')]  # строки делятся '=', после '=' значение
            d = {i[0]: i[1] for i in s if i}
    except FileNotFoundError:
        with open('crash.txt', 'w') as f:
            f.write('Cannot find save.txt')
        pygame.quit()
        sys.exit()
    return d


def draw_text(text, text_coord_y, text_coord_x, size_font, color, screen):
    font = pygame.font.Font(None, size_font)
    for i in range(len(text)):
        line = text[i]
        string_rendered = font.render(line, 1, color)
        _rect = string_rendered.get_rect()
        # text_coord_y += 10
        _rect.top = text_coord_y
        _rect.x = text_coord_x
        text_coord_y += _rect.height
        screen.blit(string_rendered, _rect)


def divide_text_to_strings_depending_on_max_width(text, font_size, max_width):
    cur, font = [text.split()], pygame.font.Font(None, font_size)
    for line in cur:
        if not line:
            break
        string_rendered = font.render(' '.join(line), 1, pygame.Color("white"))
        cur.append([])
        while string_rendered.get_rect().width > max_width:
            cur[-1].insert(0, line.pop())
            string_rendered = font.render(' '.join(line), 1, pygame.Color("white"))
    res = [' '.join(i) for i in cur]
    return res


###########################


def load_level(filename):  # "data/levels/"
    filename = filename
    with open(filename, 'r') as mapFile:
        level_map = [line.strip() for line in mapFile]
    max_width = max(map(len, level_map))
    return list(map(lambda x: x.ljust(max_width, '.'), level_map))


###################
def multiply_level(level, ver, hor, unit_symb, floor):
    res = []
    for row in range(len(level)):
        for yy in range(ver):
            res.append([])
            for cell in range(len(level[row])):
                symb = level[row][cell]
                for xxx in range(hor):
                    if symb not in unit_symb:
                        res[-1].append(symb)
                        continue
                    bool = True
                    if yy > 0 and res[-2][cell * hor + xxx] == symb:
                        bool = False
                    if xxx > 0 and res[-1][-1] == symb:
                        bool = False
                    if xxx > 0 and yy > 0:
                        if res[-2][cell * hor + xxx - 1] == symb:
                            bool = False
                    if bool:
                        res[-1].append(symb)
                    else:
                        res[-1].append(floor)
                    #if res and res[-1] not in unit_symb:
                    #    if yy > 0 and res[-2][cell * xxx] != level[row][cell] or yy == 0:
                    #        res[-1].append(level[row][cell])
                    #    else:
                    #        res[-1].append(floor)
                    #else:
                    #    res[-1].append(floor)
    return res


def parse_path(s):
    return [i.split(':') for i in s.split(' ')]


##############################################################################
###### SOMETHING IS IN MAIN.PY BECAUSE OF PYGAME.INIT() CALL REQUIREMENT #####