from PIL import Image, ImageDraw, ImageFont
# import glob

w, h, b, f = 19, 20, 3, 4
# otl = (192,192,192)
# otl = (102,102,102)
otl = (0,0,0)

def image_unknown(warn):
  image = Image.new('RGBA', (w, h))
  dc = ImageDraw.Draw(image)
  if warn:
    dc.rectangle([(1, 1), (w-2, h-1)], fill=None)
  dc.polygon([(0, h-1), (4, h-1-h/3), (w-1-4, h-1-h/3), (w-1, h-1)], fill=(160, 160, 160), outline=(0, 0, 0))
  dc.polygon([(4, 0), (w-1-4, 0), (w/2, h-1-h/6)], fill=(160, 160, 160), outline=(0, 0, 0))
  return image

def image_up(color, warn, bkcolor=(255, 255, 255)):
  image = Image.new('RGBA', (w, h))
  dc = ImageDraw.Draw(image)
  if warn:
    dc.rectangle([(0,0), (w-1,h)], fill=(255,100,76))
  dc.polygon([(0, h-1), (4, h-1-h/3), (w-1-4, h-1-h/3), (w-1, h-1)], fill=bkcolor, outline=(0, 0, 0))
  dc.polygon([(4, 0), (w-1-4, 0), (w/2, h-1-h/6)], fill=color, outline=(0, 0, 0))
  return image

def image_down(color, warn, bkcolor=(255, 255, 255)):
  image = Image.new('RGBA', (w, h))
  dc = ImageDraw.Draw(image)
  if warn:
    dc.rectangle([(0,0), (w-1,h)], fill=(255,100,76))
  dc.polygon([(0, h-1), (4, h-1-h/3), (w-1-4, h-1-h/3), (w-1, h-1)], fill=bkcolor, outline=(0, 0, 0))
  dc.polygon([(4, h/3+1), (w-1-4, h/3+1), (w-1-4-2, h-1-h/5), (4+2, h-1-h/5)], fill=color, outline=otl)
  return image

def image_disabled(warn):
  image = Image.new('RGBA', (w, h))
  dc = ImageDraw.Draw(image)
  if warn:
    dc.rectangle([(1, 1), (w-2, h-1)], fill=(255,100,76))
  dc.polygon([(0, h-1), (4, h-1-h/3), (w-1-4, h-1-h/3), (w-1, h-1)], fill=(0,0,0), outline=(255, 255, 255))
  dc.polygon([(4, 0), (w-1-4, 0), (w/2, h-1-h/6)], fill=(0,0,0), outline=(255, 255, 255))
  return image


# for fn in glob.iglob("c:/Windows/Fonts/*.*"):
#   try:
#     ttf = ImageFont.truetype(font=fn)
#     print("FT {}: {}".format(fn, ttf.getname()))
#   except Exception as e:
#     print("XX {}: {}".format(fn, e))

# fnt = ImageFont.truetype('YuGothB.ttc', 12)

fnt = ImageFont.truetype("arial.ttf", 12)


def image_timers(color, bkcolor=(255, 255, 255)):
  imageset = []

  def image_with_text(text):
    image = Image.new('RGBA', (w, h))
    dc = ImageDraw.Draw(image)
    dc.polygon([(4, 0), (w-1-4, 0), (w/2, h-1-h/6)], fill=color, outline=(0, 0, 0))
    dc.polygon([(0, h-1), (0, h/4), (w-1, h/4), (w-1, h-1)], fill=bkcolor, outline=(0, 0, 0))
    dc.text((3 if i>9 else 8, h/4+1), text, fill=(0, 0, 0), font=fnt)
    return image
  def image_plus():
    image = Image.new('RGBA', (w, h))
    dc = ImageDraw.Draw(image)
    dc.polygon([(4, 0), (w-1-4, 0), (w/2, h-1-h/6)], fill=color, outline=(0, 0, 0))
    dc.polygon([(0, h-1), (0, h/4), (w-1, h/4), (w-1, h-1)], fill=bkcolor, outline=(0, 0, 0))
    # dc.rectangle([(2, 12), (w-4, 15)], fill=(0,0,0))
    for i in range(10):
      dc.rectangle([(2+i*2, 7), (2+i*2+2, 19)], fill=(0, 0, 0), outline=(255,255,255))
    return image

  for i in range(1, 61):
    image = image_with_text(str(i))
    imageset.append(image)
  imageset.append(image_plus())
  return imageset
