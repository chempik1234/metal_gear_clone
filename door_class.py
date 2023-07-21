from base_classes import Tile
from item_classes import Card


class Door(Tile):
    def __init__(self, tile_image, tile_name, pos_x, pos_y, sprite_group, all_sprites, leads_to_room, room_name,
                 location_name, has_collisions=True, needed_card_number=0, opened=False):  # 0 means bare hand
        super().__init__(tile_image, tile_name, pos_x, pos_y, sprite_group, all_sprites, has_collisions)
        self.leads_to_room = leads_to_room
        self.room_name = room_name
        self.location_name = location_name
        self.needed_card_number = needed_card_number
        self.opened = opened

    def open(self, player=None):
        if player:
            try:
                item_class = player.inventory[player.chosen_item_index]
                if isinstance(item_class, Card) and item_class.number == self.needed_card_number or \
                        self.needed_card_number == 0:
                    self.has_collisions = False
                    self.opened = True
                    map_ = player.map
                    size_y = len(map_)
                    for y in range(size_y):
                        size_x = len(map_[y])
                        for x in range(size_x):
                            if map_[y][x] == self:
                                for xx in range(x - 1, -1, -1):
                                    cell = map_[y][xx]
                                    if not isinstance(cell, Door) or isinstance(cell, Door) and \
                                            cell.needed_card_number != self.needed_card_number:
                                        break
                                    else:
                                        if not cell.opened:
                                            cell.open(player)
                                for xx in range(x + 1, size_x):
                                    cell = map_[y][xx]
                                    if not isinstance(cell, Door) or isinstance(cell, Door) and \
                                            cell.needed_card_number != self.needed_card_number:
                                        break
                                    else:
                                        if not cell.opened:
                                            cell.open(player)
                                for yy in range(y - 1, -1, -1):
                                    cell = map_[yy][x]
                                    if not isinstance(cell, Door) or isinstance(cell, Door) and \
                                            cell.needed_card_number != self.needed_card_number:
                                        break
                                    else:
                                        if not cell.opened:
                                            cell.open(player)
                                for yy in range(y + 1, size_y):
                                    cell = map_[yy][x]
                                    if not isinstance(cell, Door) or isinstance(cell, Door) and \
                                            cell.needed_card_number != self.needed_card_number:
                                        break
                                    else:
                                        if not cell.opened:
                                            cell.open(player)
                                self.image = map_.black_image
            except Exception as ex:
                print(ex.__traceback__)