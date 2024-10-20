import tkinter as tk
import tkinter.font as font
import tkinter.ttk as ttk

from PIL import Image
import os
import signal
import platform
import re
import json
import glob
import time

import pprint

import Pallet
import Objects
import Popup
import usefull
import theaterOpener
from Share import *

share = Share()

root = tk.Tk()
root.title('ウミヘビ-面白いものを作ろう!')
root.state('zoomed')
#root.geometry(f'{root.winfo_screenwidth()}x{root.winfo_screenheight()}+0+0')
#root.resizable(False, False)
root.iconbitmap(default='Ubazame.ico')
root['background'] = '#b90000'
root.grid_propagate(False)
#root.config(cursor="watch")

root.update_idletasks()

style = ttk.Style()
style.theme_use('classic')

topbar = tk.Frame(root, width=root.winfo_width(), height=Share.topBarHeight, background='#222', padx=20, pady=0)
topbar.pack_propagate(False)
topbar.grid(row=0, column=0, columnspan=2)

style.configure('topBar.TLabel', font=('tkDefaeultFont', 14), foreground='#ccc', background='#222')
style.configure('buttonOnTopBar.TLabel', anchor='w', font=16, foreground='#ccc',
    background=topbar['background'], borderwidth=0, highlightthickness=False, padding=(10, 0))

titleEntryLabel = ttk.Label(topbar, text='このゲームの名前', style='topBar.TLabel')
titleEntryLabel.pack(side = tk.LEFT, padx=(0, 10))

title = tk.StringVar()
tk.Entry(topbar,
    bd = 3,
    relief = 'flat',
    insertwidth = 1,
    insertbackground = '#ccc',
    foreground = '#ccc',
    background = '#444',
    width = 16,
    justify = tk.LEFT,
    font = ('tkDefaeultFont', 16),
    textvariable = title
).pack(side = tk.LEFT, padx=(0, 10))
title.set('?')
#entry.focus()
def shareTitleChanged(*args):
    share.title = title.get()
title.trace('w', shareTitleChanged)

popup = Popup.Popup()
popup.initialize(root)

def escapeFilename(STRING):
    '''文字列をウィンドウズで有効なファイル名に変換し、戻り値として返します'''
    result = STRING.replace('F', 'FF')
    result = result.replace('\\', 'Fb')
    result = result.replace('/', 'Fs')
    result = result.replace(':', 'Fc')
    result = result.replace('*', 'Fa')
    result = result.replace('?', 'Fq')
    result = result.replace('"', 'Fw')
    result = result.replace('<', 'Fl')
    result = result.replace('>', 'Fg')
    result = result.replace('|', 'Fv')
    return result
def unescapeFilename(FILENAME):
    '''escapeFilenameで変換したファイル名を元の文字列に戻し、戻り値として返します'''
    result = FILENAME.replace('FF', 'F')
    result = result.replace('Fb', '\\')
    result = result.replace('Fs', '/')
    result = result.replace('Fc', ':')
    result = result.replace('Fa', '*')
    result = result.replace('Fq', '?')
    result = result.replace('Fw', '"')
    result = result.replace('Fl', '<')
    result = result.replace('Fg', '>')
    result = result.replace('Fv', '|')
    return result

def saveProgram(event):
    saveData = {
        'version': Share.version,
        'window': {
            'code': []
        },
        'objects': [],
        'variable': []
    }
    for loopi, code in enumerate(pallet.codes):
        if loopi == 0:
            for blockscript in code:
                saveData['window']['code'].append(blockscript)
        else:
            saveData['objects'].append({'code': [], 'name': objects.nameofObject[loopi], 'imagePath': objects.pathofPreviewofObj[loopi],
                'indexofDefaultCostume': objects.actors['indexofDefaultCostume'][loopi]})
            for blockscript in code:
                saveData['objects'][loopi - 1]['code'].append(blockscript)
    saveData['variable'] = pallet.variableBlocks

    if os.path.isdir(f'savedData/{escapeFilename(title.get())}'):
        with open(f'savedData/{escapeFilename(title.get())}/script.json', 'w', encoding='utf-8') as saveFile:
            json.dump(saveData, saveFile, indent=2)
    else:
        os.mkdir(f'savedData/{escapeFilename(title.get())}')
        os.mkdir(f'savedData/{escapeFilename(title.get())}/costume')
        with open(f'savedData/{escapeFilename(title.get())}/script.json', 'w+', encoding='utf-8') as saveFile:
            json.dump(saveData, saveFile, indent=2)

    popup = Popup.Popup()
    popupLabel = tk.Label(popup.frame, text='ゲームを保存しました', fg='#ccc', bg='#000', font=('tkDefaeultFont', 16), padx=30)
    popupLabel.pack(side=tk.LEFT)
    popup.show(deathTimer=3)
    return
saver = ttk.Label(topbar, text='ゲームを保存', style='buttonOnTopBar.TLabel')
saver.bind('<Enter>', lambda e: saver.config(background='#444'))
saver.bind('<Leave>', lambda e: saver.config(background=topbar['background']))
saver.bind('<ButtonRelease-1>', saveProgram)
saver.pack(side = tk.LEFT, fill=tk.Y)

projectListbox = None
def loadProgram(projectsName):
    global pallet
    global objects
    title.set(projectsName)
    if os.path.isfile(f'savedData/{escapeFilename(share.title)}/script.json'):
        with open(f'savedData/{escapeFilename(share.title)}/script.json', 'r', encoding='utf-8') as loadFile:
            saveData = json.load(loadFile)
            '''WIDTH = 80
            print('-' * (WIDTH // 2 - 4) + 'save--data' + '-' * (WIDTH // 2 - 4))
            pprint.pprint(saveData, width=WIDTH)
            print('-' * WIDTH)'''
            objects.reset()
            pallet.reset()
            pallet.codes[0] = saveData['window']['code']
            for i in range(len(saveData['objects'])):
                objects.addObject(saveData['objects'][i]['name'], tkimgPath=saveData['objects'][i]['imagePath'],
                    indexofDefaultCostume=saveData['objects'][i]['indexofDefaultCostume'])
                pallet.codes[i + 1] = saveData['objects'][i]['code']
                if not os.path.isdir(f"savedData/{escapeFilename(share.title)}/costume/{escapeFilename(saveData['objects'][i]['name'])}"):
                    os.mkdir(f"savedData/{escapeFilename(share.title)}/costume/{escapeFilename(saveData['objects'][i]['name'])}")
            for blockscript in saveData['variable']:
                pallet.addblock(blockscript, type='variable')
            objects.setup()
            pallet.setup()
            pallet.objFocusShiftHandler()
    else:
        tk.messagebox.showerror(title='ファイルを開けません', message='ゲームのファイルを開けませんでした')
def startLoadingProgram(event):
    global projectListbox
    popup = Popup.Popup()
    projects = []
    for projectsName in os.listdir('savedData/'):
        projects.append(unescapeFilename(projectsName))
    projectListBorder = tk.Frame(popup.frame, width=600, height=400, padx=10, background='#333')
    projectListBorder.pack_propagate(False)
    projectListBorder.pack(side=tk.LEFT)
    tk.Label(projectListBorder, text='読み込むゲームを選んでください', fg='#ccc', bg='#333', font=('tkDefaeultFont', 16)).pack(pady=10)
    projects = tk.StringVar(value=projects)
    projectListbox = tk.Listbox(projectListBorder, listvariable=projects, bg='#333', fg='#ccc', font=('tkDefaeultFont', 14),
        selectmode='single', bd=0, highlightthickness=False, selectbackground='green', selectforeground='#ddd',
        activestyle=tk.NONE)
    for roopi in range(projectListbox.size() // 2 + projectListbox.size() % 2):
        #projectListbox.itemconfig(roopi * 2 + 1, background='#555')
        projectListbox.itemconfig(roopi * 2, background='#444')
    projectListbox.pack(fill='both', expand=True)
    loader = tk.Label(projectListBorder, text='読み込む', fg='#ddd', bg='green', font=('tkDefaeultFont', 16),
        padx=6, pady=7)
    loader.bind('<ButtonRelease-1>', lambda e: popup.closePopup() == loadProgram(projectListbox.get(projectListbox.curselection())))
    loader.pack(side=tk.RIGHT, anchor=tk.SE, pady=10)
    closer = tk.Label(projectListBorder, text='取り消し', fg='#ddd', bg='#555', font=('tkDefaeultFont', 16),
        padx=6, pady=7)
    closer.bind('<ButtonRelease-1>', lambda e: popup.closePopup())
    closer.pack(side=tk.RIGHT, anchor=tk.SE, padx=(0, 10), pady=10)
    popup.show(okText=False)
    return
loader = ttk.Label(topbar, text='ゲームを読み込む', style='buttonOnTopBar.TLabel')
loader.bind('<Enter>', lambda e: loader.config(background='#444'))
loader.bind('<Leave>', lambda e: loader.config(background=topbar['background']))
loader.bind('<ButtonRelease-1>', startLoadingProgram)
loader.pack(side = tk.LEFT, fill=tk.Y)

versionInfo = ttk.Label(topbar, text='ウミヘビについて', style='buttonOnTopBar.TLabel')
versionInfo.bind('<Enter>', lambda e: e.widget.config(background='#444'))
versionInfo.bind('<Leave>', lambda e: e.widget.config(background=topbar['background']))
versionInfo.bind('<ButtonRelease-1>', lambda e: tk.messagebox.showinfo(title='ウミヘビについて',
    message=f'ウミヘビ\n\n制作> とあるプログラマ\n公式ホームページ> http://ubazame.php.xdomain.jp\nバージョン> {share.version}' ' (β版)\n' if share.version < 1 else '\n'))
versionInfo.pack(side=tk.LEFT, fill=tk.Y)

palletParent = tk.Frame(root, height=root.winfo_height())
palletParent.grid(row=1, column=0)
pallet = Pallet.Pallet(root, palletParent)
palletParent['width'] = pallet.width
palletParent.pack_propagate(False)

previewAndObjects = tk.Frame(root, bg='#666', width=root.winfo_width() - pallet.width, height=root.winfo_height(), padx=10, pady=10)
previewAndObjects.pack_propagate(False)
previewAndObjects.grid(row=1, column=1)

previewAndObjects.update()
previewWidth = previewAndObjects.winfo_width()
previewHeight = previewWidth // 2
preview = tk.Canvas(
    previewAndObjects,
    width=previewWidth, height=previewHeight,
    highlightthickness=False,
    background='#4f4f4f'
)
preview.pack(pady=(0, 10))
preview.create_text(
    (previewWidth // 2, previewHeight // 2), anchor=tk.CENTER,
    text='劇場の様子\n工事中...', fill='#aaa', font='tkDefaeultFont 24'
)

objectsParent = tk.Frame(previewAndObjects, background='red')
objectsParent.pack(fill='both')
objects = Objects.Objects(objectsParent, height=root.winfo_height() - previewHeight - 80)

#root.bind('<KeyPress>', lambda event: print(event.keysym))

PROJECTMEMORYJSON = 'sys/projectMemory.json'
with open('sys/projectMemory.json', 'r', encoding='utf-8') as projectMemoryFile:
    projectMemory = json.load(projectMemoryFile)
    loadProgram(projectMemory['workingOn'])

programRunning = False
programProcess = 'sonma'

def loadWorkingOn():
    global programProcess
    global programRunning
    try:
        projectMemory = {
            'version': 0,
            'workingOn': title.get()
        }
        with open('sys/projectMemory.json', 'w', encoding='utf-8') as projectMemoryFile:
            json.dump(projectMemory, projectMemoryFile, indent=2)
        #print(programRunning)
        '''if programRunning:
            print('try to kill...')
            print(programProcess)
            print(programProcess.terminate())
            os.kill(programProcess.pid, signal.SIGINT)
        else:
            print('there is nothing to kill.')'''
    except Exception as e:
        print('')
        print('!!!!ERROR WHEN EXITING THE PROGRAM!!!!')
        print(f'{e}')
        print('!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!')
    finally:
        root.destroy()
root.protocol('WM_DELETE_WINDOW', loadWorkingOn)

runner = ttk.Button(root, text='幕を上げる', style='run.TButton')
runner.bind('<ButtonRelease-1>', lambda e: theaterOpener.unveiling(pallet, objects, title))
style.configure('run.TButton', anchor='w', font=16, foreground='#ccc',
    background='#000', borderwidth=0, highlightthickness=False, padding=[10,5])
style.map('run.TButton', background=[('active', '#333')])
runner.place(x = root.winfo_width() - 20, y = root.winfo_height() - 20, anchor=tk.SE)

'''----------
|  debugger  |
-----------'''
debuggerPopup = Popup.Popup()
debugger = tk.Frame(debuggerPopup.frame, width=300, height=500, background='#444', padx=10, pady=4)
debugger.pack_propagate(False)
tk.Label(debugger, text='Debugger', font=('tkDefaeultFont', 18), fg='#ccc', bg=debugger['bg']).pack(pady=10, anchor=tk.W)

funcLabelFont = tk.font.Font(family='tkDefaeultFont', size=12, slant='italic')
def paintWidget(widget, colorCode):
    widget['bg'] = colorCode
    for child in widget.winfo_children():
        paintWidget(child, colorCode)

def addDebugButton(label, description, debugFunc):
    debugButton = tk.Frame(debugger, bg='#222', padx=5, pady=5)
    debugButton.pack(side = tk.TOP, fill=tk.X, pady=(0, 7))
    tk.Label(debugButton, text=label, font=funcLabelFont, fg='#ccc', bg='#222').pack(anchor=tk.W)
    tk.Label(debugButton, text=description, font=('tkDefaeultFont', 12),
        fg='#bbb', bg='#222', justify=tk.LEFT).pack(anchor=tk.W)
    usefull.bindAllChildren(debugButton, '<ButtonPress-1>', lambda e: paintWidget(debugButton, '#111'))
    def handler(e):
        debugFunc()
        paintWidget(debugButton, '#222')
    usefull.bindAllChildren(debugButton, '<ButtonRelease-1>', handler)

addDebugButton('printBlocks()', '現在使えるブロックの一覧を\nコンソールに出力します', pallet.printBlocks)
addDebugButton('printCodes()', 'パレットに置かれているコードを\nコンソールに出力します', pallet.printCodes)
addDebugButton('printWidgetTree()', 'パレット内のウィジェットを\nコンソールに出力します', pallet.printWidgetTree)

debugger.pack(anchor=tk.W)
def openDebugger():
    debuggerPopup.show(side=tk.BOTTOM, okText='閉じる')
debugOpener = ttk.Label(topbar, text='debug tools', style='buttonOnTopBar.TLabel')
debugOpener.bind('<Enter>', lambda e: debugOpener.config(background='#444'))
debugOpener.bind('<Leave>', lambda e: debugOpener.config(background=topbar['background']))
debugOpener.bind('<ButtonRelease-1>', lambda e: openDebugger())
debugOpener.pack(side = tk.RIGHT, fill=tk.Y)

# ウィンドウの表示
root.mainloop()
