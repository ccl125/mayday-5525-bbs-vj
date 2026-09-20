"""Render a 21-second README GIF from the player's own assets and timeline.

Usage on macOS: uv run --with pillow python render-profile.py
The interactive HTML remains the full-quality version.
"""
import json
import math
from pathlib import Path
import subprocess
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent
data = json.loads(subprocess.check_output(['node', 'export-profile.cjs'], cwd=ROOT))
T = data['T']
COLORS = {'white': '#c7ccff', 'red': '#ff3333', 'cyan': '#55d8ff',
          'yellow': '#ffe98a', 'green': '#4dff88', 'blue': '#22b8ee'}
FONT_DIR = Path('/System/Library/Fonts/Supplemental')
fonts = {}
def font(size, cjk=False):
    key = (size, cjk)
    if key not in fonts:
        fonts[key] = ImageFont.truetype(str(FONT_DIR / ('Arial Unicode.ttf' if cjk else 'Courier New.ttf')), size)
    return fonts[key]

def width(text, size):
    return sum(font(size, ord(c) > 127).getlength(c) for c in text)

def text(draw, xy, value, size=18, color='white', center=False):
    x, y = xy
    if center:
        x -= width(value, size) / 2
    for char in value:
        f = font(size, ord(char) > 127)
        draw.text((x, y), char, font=f, fill=COLORS[color], anchor='lt')
        x += f.getlength(char)
    return x

def typed(draw, parts, start, now, x, y):
    remaining = now - start
    for part in parts:
        n = max(0, min(len(part['t']), math.floor(remaining * part['cps'] + 1e-8)))
        x = text(draw, (x, y), part['t'][:n], color=part.get('cls', 'white'))
        remaining -= len(part['t']) / part['cps']
        if remaining <= 0:
            break

def logo(draw):
    # Same M/A outline and infinity curves as the HTML SVG.
    def xy(p):
        return (955 + (p[0] - 128) * 102 / 192, 140 + (p[1] - 30) * 154 / 294)
    def dashed(points):
        phase = 0
        for a, b in zip(points, points[1:]):
            a, b = xy(a), xy(b)
            length = math.dist(a, b)
            steps = max(1, math.ceil(length * 2))
            for i in range(steps):
                if (phase + i / 2) % 3.7 < 1.6:
                    u, v = i / steps, (i + 1) / steps
                    draw.line((a[0]+(b[0]-a[0])*u, a[1]+(b[1]-a[1])*u,
                               a[0]+(b[0]-a[0])*v, a[1]+(b[1]-a[1])*v), fill=COLORS['white'], width=1)
            phase += length
    dashed([(144,311),(144,165),(224,241),(302,165),(302,311),(239,311),(224,297),(208,311),(144,311)])
    dashed([(170,311),(224,115),(278,311)])
    dashed([(224,241),(224,297)])
    curves = [((224,55),(211,35),(195,35),(194,54)),
              ((194,54),(193,73),(210,75),(224,55)),
              ((224,55),(238,35),(255,35),(254,54)),
              ((254,54),(253,73),(238,75),(224,55))]
    for a,b,c,d in curves:
        points=[]
        for i in range(31):
            u=i/30
            points.append(tuple((1-u)**3*a[k]+3*(1-u)**2*u*b[k]+3*(1-u)*u*u*c[k]+u**3*d[k] for k in (0,1)))
        dashed(points)

def frame(now):
    image = Image.new('RGB', (1280,720), '#000000')
    draw = ImageDraw.Draw(image)
    typed(draw, data['h1parts'], T['h1'], now, 52,42)
    typed(draw, data['h2parts'], T['h2'], now, 52,64)
    prompt=data['h3parts'][0]['t'][:max(0,min(6,math.floor((now-T['h3'])*28)))]
    stars=max(0,min(T['starMax'],math.floor((now-T['stars'])/T['starEvery'])+1))
    text(draw,(52,86),prompt+'*'*stars)
    if T['h3End'] <= now < T['face'] and now % .9 < .45:
        x=52+width(prompt+'*'*stars,18)
        draw.rectangle((x,86,x+10,104),fill=COLORS['white'])
    chunk=min(len(data['faceChunks'])-1,math.floor((now-T['face'])/.2))
    if chunk>=0:
        face=data['faceText'][:data['faceChunks'][chunk]]
        for i,line in enumerate(face.split('\n')):
            text(draw,(52,139+i*25),line,20)
    if now>=T['castle']:
        logo(draw)
    right=[('r1','歡 迎 光 臨',23,'red',314),('r2','5525回到那一天 BBS 站',19,'cyan',353),
           ('r4','★★★★★★★★★★★★★★★★★★★★★★★',17,'cyan',422),
           ('r5','Since 1997 . 3 . 29',18,'green',462),('r7','歡迎多加利用',19,'white',512)]
    for key,value,size,color,y in right:
        if now>=T[key]: text(draw,(1006,y),value,size,color,True)
    if now>=T['r3']:
        value=data['r3parts'][0]['t']
        n=max(0,min(len(value),math.floor((now-T['r3'])*20)))
        text(draw,(1006-width(value,18)/2,396),value[:n],18,'yellow')
    if now>=T['r6']:
        values=[('本站開放 ','white'),('5521~5525','yellow'),(' 等五個port','white')]
        x=1006-width(''.join(v for v,c in values),18)/2
        for value,color in values: x=text(draw,(x,488),value,18,color)
    for i,row in enumerate(data['skyRows']):
        if now>=row['at']:
            draw.text((772,564+i*20.7),row['text'],font=font(18),fill=COLORS['blue'],anchor='lt')
    return image.resize((960,540),Image.Resampling.LANCZOS)

out=ROOT/'assets'
out.mkdir(exist_ok=True)
poster=frame(21)
poster.save(out/'mayday-5525-poster.png')
palette=poster.quantize(colors=128)
frames=[frame(i/10).quantize(palette=palette,dither=Image.Dither.NONE) for i in range(210)]
frames[0].save(out/'mayday-5525-21s.gif',save_all=True,append_images=frames[1:],
               duration=100,loop=0,optimize=True,disposal=1)
with Image.open(out/'mayday-5525-21s.gif') as gif:
    duration=0
    for i in range(gif.n_frames):
        gif.seek(i); duration+=gif.info['duration']
    assert duration==21000, duration
    print(f'GIF verified: {gif.n_frames} frames, {duration} ms, {(out/"mayday-5525-21s.gif").stat().st_size} bytes')
