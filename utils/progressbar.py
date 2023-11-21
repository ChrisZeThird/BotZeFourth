from PIL import Image, ImageFont, ImageDraw, ImageEnhance


def drawProgressBar(d, x, y, w, h, progress, bg="black", fg="red"):
    # draw background
    d.ellipse((x+w, y, x+h+w, y+h), fill=bg)
    d.ellipse((x, y, x+h, y+h), fill=bg)
    d.rectangle((x+(h/2), y, x+w+(h/2), y+h), fill=bg)

    # draw progress bar
    w *= progress
    d.ellipse((x+w, y, x+h+w, y+h), fill=fg)
    d.ellipse((x, y, x+h, y+h), fill=fg)
    d.rectangle((x+(h/2), y, x+w+(h/2), y+h), fill=fg)

    return d


# # create image or load your existing image with out=Image.open(path)
# out = Image.new("RGB", (150, 100), (255, 255, 255))
# d = ImageDraw.Draw(out)
#
# # draw the progress bar to given location, width, progress and color
# d = drawProgressBar(d, 10, 10, 100, 25, 0.5)
# # out.save("output.jpg")
