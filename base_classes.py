import pygame
from config import *


class Camera:
    def __init__(self):
        self.dx = 0
        self.dy = 0

    def apply(self, obj):
        obj.rect.x = obj.origin_x + self.dx
        obj.rect.y = obj.origin_y + self.dy

    def update(self, target):
        self.dx = -(target.origin_x + target.rect.w // 2 - WIDTH // 2)
        self.dy = -(target.origin_y + target.rect.h // 2 - HEIGHT // 2)


class ScreenFrame(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.rect = (0, 0, 500, 500)


class Sprite(pygame.sprite.Sprite):
    def __init__(self, group):
        super().__init__(group)
        self.rect = None
        self.origin_x = self.origin_y = None

    def get_event(self, event):
        pass


'''############################################
################ TILE #########################
###############################################'''


class Tile(Sprite):
    def __init__(self, tile_image, tile_name, pos_x, pos_y, sprite_group, all_sprites, has_collisions=True):
        super().__init__((sprite_group, all_sprites))
        self.image = tile_image
        self.tile_type = tile_name
        self.rect = self.image.get_rect().move(tile_width * pos_x,
                                               tile_height * pos_y)
        self.origin_x = pos_x * tile_width
        self.origin_y = pos_y * tile_height
        self.mask = pygame.mask.from_surface(self.image)
        self.has_collisions = has_collisions


class ItemTile(Tile):
    def __init__(self, item_class, pos_x, pos_y, sprite_group, all_sprites):
        scaled_image = pygame.transform.scale(item_class.image, (tile_width, tile_height))
        super().__init__(scaled_image, "item_" + item_class.name, pos_x, pos_y, sprite_group, all_sprites, False)
        self.represented_item = item_class


###################################### END TILES ######


class YAwareGroup(pygame.sprite.Group):
    def by_y(self, spr):
        return spr.origin_y

    def draw(self, surface):
        sprites = self.sprites()
        surface_blit = surface.blit
        for spr in sorted(sprites, key=self.by_y):
            self.spritedict[spr] = surface_blit(spr.image, spr.rect)
        self.lostsprites = []


class Map:
    def __init__(self, list_, black_image, item_map):
        self.map = list_
        #for i in list_:
        #    self.map.append([])
        #    for j in i:
        #        self.map[-1].append(j)
        self.items_dict = item_map
        self.index_ = None  # for __iter__
        self.black_image = black_image

    def __len__(self):
        return len(self.map)

    def __getitem__(self, item):
        return self.map[item]

    def __iter__(self):
        self.index_ = 0  # self.map[0]
        return self

    def __next__(self):
        if self.index_ + 1 < len(self.map):
            self.index_ += 1
            return self.map[self.index_]
        else:
            raise StopIteration

    def get_item(self, y, x):
        item = self.items_dict.get((y, x))
        if item:
            if item.alive():
                return item
            else:
                del self.items_dict[(y, x)]
        return None
