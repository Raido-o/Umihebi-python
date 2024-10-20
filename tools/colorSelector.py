import tkinter as tk
import tkinter.font as font
from tkinter.colorchooser import askcolor
import tkinter.ttk as ttk

root = tk.Tk()
root.title('色を調合しましょう')
ROOTBG = '#222'
root['background'] = ROOTBG
WINDOWWIDTH = 360
WINDOWHEIGHT = 600
root.geometry(f'{WINDOWWIDTH}x{WINDOWHEIGHT}+{(root.winfo_screenwidth() - WINDOWWIDTH) // 2}+{(root.winfo_screenheight() - WINDOWHEIGHT) // 2}')
style = ttk.Style()

rootFrame = tk.Frame(root, bg=ROOTBG)
rootFrame.pack(padx=10, pady=20)

labelFont = font.Font(family='tkDefaeultFont', size=20)

tk.Label(rootFrame, text='現在の色', font=labelFont,
    fg='#ccc', bg=ROOTBG, padx=5, pady=5).pack(pady=(0, 10))

defaultColor = '#000000'

colorPreview = tk.Canvas(
    rootFrame,
    width=WINDOWWIDTH * 0.8, height=WINDOWWIDTH * 0.8,
    highlightthickness=False,
    background=ROOTBG
)
colorPreview.create_oval(0, 0, colorPreview.winfo_reqwidth(), colorPreview.winfo_reqwidth(),
    fill=defaultColor, tag='colorCircle')
colorPreview.pack()

nowColor = tk.Entry(rootFrame, font=('tkDefaeultFont', 22), bd=0, width=7,
    insertwidth=1, insertbackground='#ccc', fg='#ccc', bg=ROOTBG)
nowColor.insert(tk.END, defaultColor)
nowColor.pack(pady=(5, 5))

copier = tk.Label(rootFrame, text='Copy', font=labelFont,
    fg='#ccc', bg='#666', padx=5, pady=5)
def copierClicked(event):
    event.widget['bg'] = '#444'
def finishCopyAnime():
    copier['text'] = 'Copy'
def copyColorCode(event):
    root.clipboard_clear()
    root.clipboard_append(nowColor.get())
    copier['text'] = 'Copied!'
    event.widget['bg'] = '#666'
    root.after(700, finishCopyAnime)
copier.bind('<ButtonPress-1>', copierClicked)
copier.bind('<ButtonRelease-1>', copyColorCode)
copier.pack(pady=(0, 10))

def changeColor(RGBcolorCode):
    colorPreview.itemconfig('colorCircle', fill=RGBcolorCode)
    nowColor.delete(0, tk.END)
    nowColor.insert(0, RGBcolorCode)

HANDLER = 15    # Scaleのつまみの半径
def makeScale(parent, handleDragHandler):
    scale = tk.Canvas(parent,
        width=WINDOWWIDTH * 0.6, height=HANDLER * 2,
        highlightthickness=False,
        background=ROOTBG)
    #brightnessSelector.create_rectangle(1, 1, brightnessSelector.winfo_reqwidth() - 1, HANDLER * 2 - 1, fill='blue', width=0)
    scale.create_oval(HANDLER - 5, 10, HANDLER + 5, 19,
        fill='#ccc', width=0)
    scale.create_rectangle(HANDLER, 10, scale.winfo_reqwidth() - HANDLER, 20, fill='#ccc', width=0)
    scale.create_oval(scale.winfo_reqwidth() - HANDLER - 5, 10, scale.winfo_reqwidth() - HANDLER + 5, 19,
        fill='#ccc', width=0)
    scale.create_oval(0, 1, scale.winfo_reqheight() - 2, scale.winfo_reqheight() - 1,
        fill='#999', width=2, outline='#ddd', tag='handle')
    def handleDragging(event):
        if HANDLER > event.x:
            event.x = HANDLER
        elif event.x > scale.winfo_reqwidth() - HANDLER:
            event.x = scale.winfo_reqwidth() - HANDLER
        scale.moveto('handle', event.x - scale.winfo_reqheight() // 2, 0)
        #print((event.x - HANDLER) * 100 // (brightnessSelector.winfo_reqwidth() - HANDLER * 2))
        handleDragHandler(event, (event.x - HANDLER) * 100 // (scale.winfo_reqwidth() - HANDLER * 2))
    scale.tag_bind('handle', '<Button1-Motion>', handleDragging)
    return scale

def hsv2rgb(h, s, v):
    if s == 0.0: return (v, v, v)
    i = int(h*6.)
    f = (h*6.)-i; p,q,t = v*(1.-s), v*(1.-s*f), v*(1.-s*(1.-f)); i%=6
    if i == 0: return (v, t, p)
    if i == 1: return (q, v, p)
    if i == 2: return (p, v, t)
    if i == 3: return (p, q, v)
    if i == 4: return (t, p, v)
    if i == 5: return (v, p, q)

hsv = [0, 0, 0]
def selectorChanged():
    HSV = hsv2rgb(hsv[0] / 100, hsv[1] / 100, hsv[2] / 100)
    RGBcolorCode = '#'
    for i in HSV:
        i = round(255 * i)
        if i // 16 == 0: RGBcolorCode += '0'
        if i // 16 == 1: RGBcolorCode += '1'
        if i // 16 == 2: RGBcolorCode += '2'
        if i // 16 == 3: RGBcolorCode += '3'
        if i // 16 == 4: RGBcolorCode += '4'
        if i // 16 == 5: RGBcolorCode += '5'
        if i // 16 == 6: RGBcolorCode += '6'
        if i // 16 == 7: RGBcolorCode += '7'
        if i // 16 == 8: RGBcolorCode += '8'
        if i // 16 == 9: RGBcolorCode += '9'
        if i // 16 == 10: RGBcolorCode += 'a'
        if i // 16 == 11: RGBcolorCode += 'b'
        if i // 16 == 12: RGBcolorCode += 'c'
        if i // 16 == 13: RGBcolorCode += 'd'
        if i // 16 == 14: RGBcolorCode += 'e'
        if i // 16 == 15: RGBcolorCode += 'f'
        if i % 16 == 0: RGBcolorCode += '0'
        if i % 16 == 1: RGBcolorCode += '1'
        if i % 16 == 2: RGBcolorCode += '2'
        if i % 16 == 3: RGBcolorCode += '3'
        if i % 16 == 4: RGBcolorCode += '4'
        if i % 16 == 5: RGBcolorCode += '5'
        if i % 16 == 6: RGBcolorCode += '6'
        if i % 16 == 7: RGBcolorCode += '7'
        if i % 16 == 8: RGBcolorCode += '8'
        if i % 16 == 9: RGBcolorCode += '9'
        if i % 16 == 10: RGBcolorCode += 'a'
        if i % 16 == 11: RGBcolorCode += 'b'
        if i % 16 == 12: RGBcolorCode += 'c'
        if i % 16 == 13: RGBcolorCode += 'd'
        if i % 16 == 14: RGBcolorCode += 'e'
        if i % 16 == 15: RGBcolorCode += 'f'
    changeColor(RGBcolorCode)

hueSelectFrame = tk.Frame(rootFrame, bg=ROOTBG)
tk.Label(hueSelectFrame, text='色相', font=('tkDefaeultFont', 12),
    fg='#ccc', bg=ROOTBG).pack(side=tk.LEFT)
hueLabel = tk.Label(hueSelectFrame, text='0', font=('tkDefaeultFont', 12),
    fg='#ccc', bg=ROOTBG)
hueLabel.pack(side=tk.LEFT)
tk.Label(hueSelectFrame, text='%', font=('tkDefaeultFont', 12),
    fg='#ccc', bg=ROOTBG).pack(side=tk.LEFT)
def hueSelectorChanged(e, percent):
    hueLabel['text'] = str(percent)
    hsv[0] = percent
    selectorChanged()
makeScale(hueSelectFrame, hueSelectorChanged).pack(side=tk.LEFT)
hueSelectFrame.pack()

saturationSelectFrame = tk.Frame(rootFrame, bg=ROOTBG)
tk.Label(saturationSelectFrame, text='彩やかさ', font=('tkDefaeultFont', 12),
    fg='#ccc', bg=ROOTBG).pack(side=tk.LEFT)
saturationLabel = tk.Label(saturationSelectFrame, text='0', font=('tkDefaeultFont', 12),
    fg='#ccc', bg=ROOTBG)
saturationLabel.pack(side=tk.LEFT)
tk.Label(saturationSelectFrame, text='%', font=('tkDefaeultFont', 12),
    fg='#ccc', bg=ROOTBG).pack(side=tk.LEFT)
def saturationSelectorChanged(e, percent):
    saturationLabel['text'] = str(percent)
    hsv[1] = percent
    selectorChanged()
makeScale(saturationSelectFrame, saturationSelectorChanged).pack(side=tk.LEFT)
saturationSelectFrame.pack()

valueSelectFrame = tk.Frame(rootFrame, bg=ROOTBG)
tk.Label(valueSelectFrame, text='明るさ', font=('tkDefaeultFont', 12),
    fg='#ccc', bg=ROOTBG).pack(side=tk.LEFT)
valueLabel = tk.Label(valueSelectFrame, text='0', font=('tkDefaeultFont', 12),
    fg='#ccc', bg=ROOTBG)
valueLabel.pack(side=tk.LEFT)
tk.Label(valueSelectFrame, text='%', font=('tkDefaeultFont', 12),
    fg='#ccc', bg=ROOTBG).pack(side=tk.LEFT)
def valueSelectorChanged(e, percent):
    valueLabel['text'] = str(percent)
    hsv[2] = percent
    selectorChanged()
makeScale(valueSelectFrame, valueSelectorChanged).pack(side=tk.LEFT)
valueSelectFrame.pack()

root.mainloop()
