s, w = '', None
while w != 'jkl':
    w = input().replace('self.rect.h', "self.image.get_height()").replace('self.rect.w', "self.image.get_width()")
    s += w + '\n'
print(s)