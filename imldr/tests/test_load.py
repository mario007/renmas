
from imldr import load_image, save_image

#img = load_image('E:/hdr_images/Desk_oBA2.hdr')
# print(img)
# # img = load_image('E:/hdr_images/Apartment_float_o15C.hdr')
# # print(img)
#img = load_image('E:/hdr_images/AtriumNight_oA9D.hdr')
# print(img)

# img = load_image('C:/Users/Public/Pictures/Sample Pictures/Koala.jpg')
# print(img)

img = load_image('C:/Users/Public/Pictures/Sample Pictures/Koala.jpg')
print(img)

save_image('Koala.png', img)
#save_image('Koala.exr', img)
