import tkinter as tk
import tkinter.ttk as ttk
import tkinter.messagebox as messagebox
import os
import glob
import re
from PIL import Image

from Share import *
import usefull
import thumbnailCache

class Objects:
    __share = Share()
    indexofCurrentlySelectedObj = None
    parent = None
    __canvas = None
    objectGroup = None
    funcs = {'<after init>': [], '<focus shift>': [], '<object added>': [], '<object deleted>': []}
    photoTemp = [None]
    objects = {'border': [], 'name': ['舞台'], 'preview': [''], 'previewPath': ['']}
    actors = {'costume': [None], 'nameCard': [None], 'indexofDefaultCostume': [None]}
    defaultImage = None
    adder = None
    space = []
    def __init__(self, parent=None, height=None):
        if parent != None:
            Objects.parent = parent
            Objects.parent.update()

            Objects.__canvas = tk.Canvas(Objects.parent, width=parent.winfo_width() - 17, height=height,
                bd=0, highlightthickness=0, background='#777')
            Objects.__canvas.pack(side=tk.LEFT)
            ybar = tk.Scrollbar(Objects.parent, orient='vertical', command=Objects.__canvas.yview)
            ybar.pack(side=tk.RIGHT, fill='y')
            Objects.__canvas.configure(yscrollcommand=ybar.set)

            Objects.objectGroup = tk.Frame(Objects.__canvas, padx=(parent.winfo_width() - self.numberofRows * 170) // 2,
                pady=20, background=Objects.__canvas['bg'])
            Objects.objectGroup.bind(
                '<Configure>', lambda e: Objects.__canvas.configure(scrollregion=Objects.__canvas.bbox('all'))
            )

            Objects.__canvas.create_window((0, 0), window=Objects.objectGroup, anchor='nw')
            windowObjectBorder = tk.Frame(Objects.objectGroup,
                width=parent.winfo_width() - Objects.objectGroup['padx'] * 2,
                height=80, padx=3, pady=3, background=Share.maincolor)
            windowObjectBorder.pack_propagate(False)
            windowObjectBorder.grid(row=0, column=0, columnspan=self.numberofRows, pady=(0, 10))
            Objects.objects['border'].append(windowObjectBorder)

            windowObject = tk.Label(windowObjectBorder, width=100, height=100, text=Objects.objects['name'][0],
                font=('tkDefaeultFont', 16), fg='#ccc', bg='#444')
            windowObject.pack(anchor='center', fill=tk.BOTH)
            usefull.bindAllChildren(Objects.__canvas, '<ButtonPress-1>',
                lambda e: self.objectSwitch(windowObjectBorder))

            Objects.indexofCurrentlySelectedObj = 0

            iconTempPath = 'temp/output.png'
            if os.path.isfile(iconTempPath) == False:
                img = Image.open('Ubazame.png')
                img.resize((int(img.width * 100 / img.height), 100)).save('temp/output.png', quality=90)

            Objects.defaultImage = tk.PhotoImage(file=iconTempPath)

            def addObject():
                res = tk.simpledialog.askstring('オブジェクトを名付けて下さい', '新しく作成するオブジェクトの名前を入力してください')
                if res != None:
                    self.addObject(res)
                    self.objectSwitch(Objects.objects['border'][-1])
            Objects.adder = tk.Frame(Objects.objectGroup, width=self.objectWidth, height=160,
                padx=3, pady=3, background='#555')
            Objects.adder.pack_propagate(False)
            objectAdderLabel = ttk.Label(Objects.adder, text='役者を追加', foreground='#ccc', background='#555',
                font=('tkDefaeultFont', 12), image=Objects.defaultImage, compound='top')
            objectAdderLabel.pack(expand=True)
            Objects.adder.bind('<ButtonPress-1>', lambda event: addObject())
            objectAdderLabel.bind('<ButtonPress-1>', lambda event: addObject())

            for i in range(self.numberofRows - 1):
                Objects.space.append(tk.Frame(Objects.objectGroup, width=self.objectWidth, height=160, background='#888'))
                Objects.space[i].grid(padx=(0, 10), pady=(0, 10), row=1)
                Objects.space[i].grid_remove()

            usefull.bindAllChildren(Objects.__canvas, '<MouseWheel>', self.mouseWheelHandler)
            #for i in range(self.numberofRows):
            #    self.addObject(name=f'オブジェクト{i}')

            for function in Objects.funcs['<after init>']:
                function()
        return
    def mouseWheelHandler(self, event):
        if self.exceptWindow(self.numberofObj) > self.numberofRows:
            Objects.__canvas.yview_scroll(-(event.delta // 120), 'units')
    def reset(self):
        '''ウィンドウを除くすべてのオブジェクトを削除し, 新しいゲームの読み込みに備えます'''
        if self.numberofObj > 1:
            for i in range(self.numberofObj - 1):
                self.deleteObject(1)
    def setup(self):
        '''新しいゲームの読み込みが終わったのちに必要な処理を行います'''
        #self.objectSwitch(Objects.objects['border'][0])
        pass
    def relocateAdder(self):
        Objects.adder.grid(padx=(0, 10), pady=(0, 10),
            row=self.exceptWindow(self.numberofObj) // self.numberofRows + 1,
            column=self.exceptWindow(self.numberofObj) % self.numberofRows)
        Objects.adder.tkraise()
    def exceptWindow(self, naturalNumber):
        if naturalNumber >= 1 and int(naturalNumber) == naturalNumber:
            return naturalNumber - 1
        else:
            print(f'[ERROR] Argument "natural number" is {naturalNumber}, not a natural number')
            return False
    def objectSwitch(self, selectedBorder, **kwargs):
        #print('focus shift!!')
        indexofTheObjectYouJustClicked = Objects.objects['border'].index(selectedBorder)
        for loopi, brd in enumerate(Objects.objects['border']):
            if brd['background'] == Share.maincolor:
                brd['background'] = '#333'
                if loopi != 0 and loopi != indexofTheObjectYouJustClicked:
                    deleteObjectButton = brd.winfo_children()[-1]
                    deleteObjectButton.pack_forget()
                    deleteObjectButton.destroy()
        selectedBorder['background'] = Share.maincolor

        if indexofTheObjectYouJustClicked == Objects.indexofCurrentlySelectedObj:
            return
        else:
            Objects.indexofCurrentlySelectedObj = indexofTheObjectYouJustClicked

        if indexofTheObjectYouJustClicked != 0:
            deleteObjectButton = tk.Label(selectedBorder, text='削除', font=12, fg='#fff', bg='#8a71ff', padx=10, pady=5)
            deleteObjectButton.bind('<ButtonPress-1>', lambda event: self.deleteObject())
            deleteObjectButton.place(relx=1, y=0, anchor=tk.NE)
            self.changeObjectPreview(tkimgPath=
                glob.glob(f'savedData/{Objects.__share.title}/costume/{self.nameofObject[indexofTheObjectYouJustClicked]}/*')[Objects.actors['indexofDefaultCostume'][indexofTheObjectYouJustClicked]],
                OBJECTINDEX=indexofTheObjectYouJustClicked)

        if 'func' in kwargs:
            kwargs['func']()
        for function in Objects.funcs['<focus shift>']:
            function()
        return
    def addObject(self, name, tkimgPath=None, indexofDefaultCostume=0):
        objectBorder = tk.Frame(Objects.objectGroup, width=self.objectWidth, height=160,
            padx=3, pady=3, background='#333')
        objectBorder.pack_propagate(False)
        objectBorder.grid(padx=(0, 10), pady=(0, 10), sticky=tk.E,
            row=self.exceptWindow(self.numberofObj) // self.numberofRows + 1,
            column=self.exceptWindow(self.numberofObj) % self.numberofRows)
        Objects.objects['border'].append(objectBorder)

        object = tk.Frame(objectBorder, width=160, height=160,
            background='#444')
        object.pack_propagate(False)
        object.pack(anchor='center', fill=tk.BOTH)

        objectPreview = ttk.Label(object, background='#444', image=Objects.defaultImage)
        Objects.objects['preview'].append(objectPreview)
        objectPreview['image'] = Objects.defaultImage
        Objects.objects['previewPath'].append('temp/output.png')
        Objects.actors['costume'].append(['temp/output.png'])
        Objects.actors['indexofDefaultCostume'].append(indexofDefaultCostume)
        objectPreview.place(anchor='center', relx=0.5, rely=0.45)

        Objects.objects['name'].append(name)
        nameCard = ttk.Label(object, text=self.nameofObject[self.numberofObj-1], foreground='#ccc', background='#444',
            font=('tkDefaeultFont', 12))
        nameCard.place(anchor='center', relx=0.5, rely=0.88)
        Objects.actors['nameCard'].append(nameCard)

        usefull.bindAllChildren(objectBorder, '<ButtonPress-1>', lambda event: self.objectSwitch(objectBorder))
        usefull.bindAllChildren(objectBorder, '<MouseWheel>', self.mouseWheelHandler)
        if tkimgPath != None:
            self.changeObjectPreview(tkimgPath=
                glob.glob(f'savedData/{Objects.__share.title}/costume/{self.nameofObject[-1]}/*')[indexofDefaultCostume],
                OBJECTINDEX=self.numberofObj - 1)
        if self.exceptWindow(self.numberofObj) < self.numberofRows:
            for i in range(self.numberofRows - self.exceptWindow(self.numberofObj) - 1):
                Objects.space[i].grid(column=self.exceptWindow(self.numberofObj) + i + 1)
        self.relocateAdder()
        for function in Objects.funcs['<object added>']:
            function()
        return
    def changeObjectPreview(self, tkimgPath, OBJECTINDEX=None):
        if OBJECTINDEX == 0:
            print('[ERROR] Incorrect actor index: Stage cannot change its preview')
            return False
        if OBJECTINDEX == None:
            OBJECTINDEX = self.indexofCurrentlySelectedObj
        thumbnail = tk.PhotoImage(file=thumbnailCache.cache(tkimgPath))
        Objects.photoTemp.append(thumbnail)
        Objects.actors['costume'][OBJECTINDEX][0] = tkimgPath
        Objects.objects['previewPath'][OBJECTINDEX] = tkimgPath
        Objects.objects['preview'][OBJECTINDEX]['image'] = Objects.photoTemp[Objects.photoTemp.index(thumbnail)]
        return True
    def addCostume(self, tkimgPath, ACTORINDEX=None):
        if ACTORINDEX == 0:
            print('[ERROR] Incorrect actor index: Stage does not wear costumes.')
            return False
        if ACTORINDEX == None:
            ACTORINDEX = self.indexofCurrentlySelectedObj
        Objects.actors['costume'][ACTORINDEX].append(tkimgPath)
        img = Image.open(tkimgPath)
        try:
            #shutil.copy(tkimgPath,
            #    f'savedData/{Objects.__share.title}/costume/'
            #    f'{self.nameofObject[self.indexofCurrentlySelectedObj]}/{os.path.basename(tkimgPath)}')
            img.save(f'savedData/{Objects.__share.title}/costume/'
                f'{self.nameofObject[self.indexofCurrentlySelectedObj]}/{os.path.splitext(os.path.basename(tkimgPath))[0]}.png')
        except:
            usefull.printWarning(f'画像ファイル({tkimgPath})のsavedData/'
                f'{self.__share.title}/costume/{Objects.nameofObject[self.indexofCurrentlySelectedObj]}/{os.path.basename(tkimgPath)}'
                'へのコピーに失敗しました')
        return True
    def deleteObject(self, OBJECTINDEX=None):
        #if messagebox.askokcancel('オブジェクトの削除', 'このオブジェクトを削除します。よろしいですか？'):
        if OBJECTINDEX == 0:
            print('[ERROR] Incorrect object index: Window object cannot be deleted')
            return
        elif OBJECTINDEX == None:
            OBJECTINDEX = self.indexofCurrentlySelectedObj
        #Objects.objects['border'][OBJECTINDEX].grid_forget()
        Objects.objects['border'][OBJECTINDEX].destroy()
        Objects.objects['border'].remove(Objects.objects['border'][OBJECTINDEX])
        Objects.objects['name'].remove(Objects.objects['name'][OBJECTINDEX])
        Objects.objects['preview'].remove(Objects.objects['preview'][OBJECTINDEX])
        Objects.objects['previewPath'].remove(Objects.objects['previewPath'][OBJECTINDEX])
        Objects.actors['nameCard'].remove(Objects.actors['nameCard'][OBJECTINDEX])
        for i in range(len(Objects.objects['border'])):
            if i != 0:
                Objects.objects['border'][i].grid(row=((i - 1) // self.numberofRows + 1), column=((i - 1) % self.numberofRows))
        self.objectSwitch(Objects.objects['border'][OBJECTINDEX - 1])
        self.relocateAdder()
        if self.exceptWindow(self.numberofObj) < self.numberofRows:
            for i in range(self.numberofRows - self.exceptWindow(self.numberofObj) - 1):
                Objects.space[i].grid(column=self.exceptWindow(self.numberofObj) + i + 1)
        for function in Objects.funcs['<object deleted>']:
            function(OBJECTINDEX)
        return
    def bind(self, sequence, func, add=False):
        for seq in Objects.funcs:
            if sequence == seq:
                if add == '+':
                    Objects.funcs[seq].append(func)
                else:
                    Objects.funcs[seq] = [func]
                return True
        print(f'[ERROR] {sequence} is a sequence that does not exist')
        return False
    def setName(self, name, OBJECTINDEX=None):
        if OBJECTINDEX == None:
            OBJECTINDEX = self.indexofCurrentlySelectedObj
        if OBJECTINDEX == 0:
            print('[ERROR] Incorrect object index: Window object cannot change its name')
            return False
        Objects.objects['name'][OBJECTINDEX] = name
        Objects.actors['nameCard'][OBJECTINDEX]['text'] = self.nameofObject[OBJECTINDEX]
        return True
    '''--------------
    |  property set  |
    ---------------'''
    @property
    def objectWidth(self):
        return 160
    @property
    def numberofRows(self):
        return Objects.parent.winfo_width() // (self.objectWidth + 10)
    @property
    def numberofObj(self):
        return len(Objects.objects['border'])
    @property
    def numberofActor(self):
        return len(Objects.objects['border'])
    @property
    def nameofObject(self):
        return Objects.objects['name']
    @property
    def pathofPreviewofObj(self):
        return Objects.objects['previewPath']
    @property
    def indexofCurrentlySelectedObj(self):
        return Objects.indexofCurrentlySelectedObj
    @property
    def windowSelected(self):
        return self.indexofCurrentlySelectedObj == 0
