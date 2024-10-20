import hashlib
import imagehash
import os
from PIL import Image

def cache(imagePath):
    thumbnailPath = f'sys/thumbnailCache/{hashlib.sha256(bytes(imagePath, encoding="utf-8")).hexdigest()}.png'
    if not os.path.isfile(thumbnailPath) or imagehash.average_hash(Image.open(imagePath)) != imagehash.average_hash(Image.open(thumbnailPath)):
        #print(f'[INFO] chaching {imagePath}...', end='')
        img = Image.open(imagePath)
        if img.width > img.height:
            img.resize((100, int(img.height * 100 / img.width))).save(thumbnailPath, quality=90)
        else:
            img.resize((int(img.width * 100 / img.height), 100)).save(thumbnailPath, quality=90)
        #print(f'done')
    return getThumbnail(imagePath)

def getThumbnail(imagePath):
    return f'''sys/thumbnailCache/{hashlib.sha256(bytes(imagePath, encoding='utf-8')).hexdigest()}.png'''
