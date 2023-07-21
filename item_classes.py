from base_classes import Sprite
import pygame
from config import *
item_name_to_class = {}


class Item(Sprite):
    def __init__(self, name, image, items_window_groups, usable=True, amount=1, description=''):
        super(Item, self).__init__(items_window_groups)
        self.name = name
        self.image = image
        self.usable = usable
        self.amount = amount
        self.description = description
        item_name_to_class[self.name] = self

    def draw(self, screen):
        screen.blit(self.image, self.rect)

    def use(self):
        if self.amount > 0:
            self.amount -= 1


class Card(Item):
    def __init__(self, name, image, number, items_window_groups):
        super().__init__(name, image, items_window_groups, False)
        self.number = number
        self.description = "This access card allows you to open doors with the lock type " + str(self.number)
