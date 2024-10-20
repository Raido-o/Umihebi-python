import ctypes
import tkinter as tk
import tkinter.ttk as ttk
import tkinter.filedialog
import time
import threading
import re
import os
import colorama
from colorama import Fore
from colorama import Style
'''
These colors can be used:
BLACK, RED, GREEN, YELLOW, BLUE, MAGENTA, CYAN, WHITE
'''

import Pallet.manipulationBS as mBS
import Objects
import usefull
from Share import *
import thumbnailCache

colorama.init()

class Pallet:
    __share = Share()
    style = None
    objects = None
    root = None
    topFrame = None
    __header = None
    objectName = None
    objectNameEntry = None
    notebook = None
    blocks = []
    blockPalletsParent = None
    __scrollOnblockPallet = {'canvas': None, 'trueYbar': None, 'fakeYbar': None}
    blockPallets = {
        'window': None, 'object': None, 'sack': {'window': None, 'object': None},
        'scroll': {
            'window': {'canvas': None, 'trueYbar': None, 'fakeYbar': None},
            'object': {'canvas': None, 'trueYbar': None, 'fakeYbar': None}
        }
    }
    blockChanged = None
    starterBlocks = []
    generalBlocks = []
    objectOnlyBlocks = []
    windowOnlyBlocks = []
    variableBlocks = []
    blocks2controlVariables = []
    widgetsOnBlockZone = {'window': [], 'object': []}
    blocksOnBlockZone = {'window': [], 'object': []}
    __originalPositionOfBlock = {'x': None, 'y': None}
    codes = []
    __codeCanvas = None
    codeFrame = None
    blockCursor = None
    widgetsOnCodeZone = []
    fitTermsOnCodeZone = []
    entryOnCodeZoneInfo = {'frame': [], 'numberInBlock': []}
    draggingBlock = {'widget': None, 'blockscript': None, 'isTerm': None}
    funcs = {'<block drop>': []}
    '''-----------------
    |  for costume tab  |
    ------------------'''
    costumePreview = []
    frameofWardrobe = None
    wordrobe = []
    costumeTkPhotoImageThumnail = []
    costumeInWorkName = None
    costumeInWorkOriginalName = None
    indexofSelectedCostume = None
    costumeName = []
    costumeNameChangeThread = None
    costumeCondition = None
    '''-------------------------
    |  for transformable block  |
    --------------------------'''
    transformableParent = None
    costumeBlockCreated = False
    '''---------------
    |  for code menu  |
    ----------------'''
    codeMenu = None
    indexofCode2delete = None
    '''-------------
    |  block types  |
    --------------'''
    normal = 'normal'
    nest = 'nest'
    def __init__(self, root, parent):
        '''
        Palletを初期化する

        Parameters
        ----------
        root : <class 'tkinter.Tk'>
            Palletの要素を作成する時のメインウィンドウ
        parent : <class 'tkinter.Frame'>
            Palletの要素を作成する時の、すべてのPallet要素の親要素

        Returns
        -------
        None
        '''
        Pallet.objects = Objects.Objects()
        Pallet.objects.bind('<after init>', self.initAfterObjInit)

        Pallet.style = ttk.Style()
        Pallet.style.theme_use('classic')

        Pallet.root = root
        Pallet.topFrame = tk.Frame(
            parent,
            width=self.width, height=self.height
        )
        Pallet.topFrame.pack_propagate(False)
        Pallet.topFrame.pack(fill=tk.BOTH, expand=True)

        self.initHeader()

        Pallet.notebook = ttk.Notebook(Pallet.topFrame, width=self.width, padding=0)
        Pallet.style.configure('TNotebook', background=Pallet.style.lookup('header.TFrame', 'background'), borderwidth=0)
        Pallet.notebook.pack()
        Pallet.style.configure('TNotebook.Tab', background='#555', foreground='#ccc', font=('tkDefaeultFont', 10),
            lightcolor='#333', borderwidth=0)
        Pallet.style.map('TNotebook.Tab', background=[('selected', self.selectedTabColor)])

        # ブロックフレーム, コードフレームを格納
        self.__blockAndCodeParent = tk.Frame(Pallet.topFrame, width=self.width, height=self.height)
        Pallet.notebook.add(self.__blockAndCodeParent, text='プログラム')
        # いろんなブロックを置く場所
        Pallet.blockPalletsParent = tk.Frame(self.__blockAndCodeParent, width=self.blockAreaWidth,
            height=self.height-Pallet.__header.winfo_height()-65)
        Pallet.blockPalletsParent.grid_propagate(False)
        Pallet.blockPalletsParent.pack(side=tk.LEFT)

        Pallet.style.configure('pallet.Vertical.TScrollbar',
            troughcolor='#888')
        Pallet.style.map('pallet.Vertical.TScrollbar',
            background=[('focus', '#555'), ('!focus', '#555')])
        Pallet.style.configure('pallet.Horizontal.TScrollbar',
            troughcolor='#888')
        Pallet.style.map('pallet.Horizontal.TScrollbar',
            background=[('focus', '#555'), ('!focus', '#555')])

        self.addblock('{*上|下|右|左|w|s}キーが離されたとき', type='starter')
        self.addblock('[3]回~~する', type='box')
        self.addblock('ずっと~~する', type='box')
        self.addblock('もし<>なら~~する', type='box')
        self.addblock('[[] + []]')
        self.addblock('[[] x []]')
        self.addblock('#コメントをここに入力')
        self.addblock('[0から1までの乱数]')
        self.addblock('ウィンドウの幅を[300]pxに、高さを[300]pxにする', WINDOWONLY=True)
        self.addblock('ウィンドウの背景色を[#000]にする', WINDOWONLY=True)
        self.addblock('分身の動き', OBJECTONLY=True, type='starter')
        self.addblock('x座標を[200]に、y座標を[200]にする', OBJECTONLY=True)
        self.addblock('上に[10]px動く', OBJECTONLY=True)
        self.addblock('下に[10]px動く', OBJECTONLY=True)
        self.addblock('右に[10]px動く', OBJECTONLY=True)
        self.addblock('左に[10]px動く', OBJECTONLY=True)
        self.addblock('隠れる', OBJECTONLY=True)
        self.addblock('自分自身の分身を作る', OBJECTONLY=True)
        self.addblock('<[] = []>', OBJECTONLY=True, type='term')
        self.addblock('<[]が[]以上>', OBJECTONLY=True, type='term')
        self.addblock('<<>かつ<>>', OBJECTONLY=True, type='term')
        self.addblock('[この物体のX座標]', OBJECTONLY=True)
        self.addblock('[この物体のY座標]', OBJECTONLY=True)
        Pallet.blockPalletsParent.update()
        Pallet.style.configure('blockSack.TFrame', background=self.selectedTabColor)
        Pallet.blockPallets['window'] = tk.Frame(Pallet.blockPalletsParent, width=self.blockAreaWidth,
            height=self.height-Pallet.__header.winfo_height()-21)
        Pallet.blockPallets['window'].pack_propagate(False)
        Pallet.blockPallets['window'].grid(row=0, column=0, sticky=tk.NSEW)

        Pallet.blockPallets['scroll']['window']['canvas'] = tk.Canvas(Pallet.blockPallets['window'],
            width=self.blockAreaWidth-self.scrollbarWidth,
            height=Pallet.blockPalletsParent.winfo_height(),
            bd=0, highlightthickness=0, bg=self.selectedTabColor)
        Pallet.blockPallets['scroll']['window']['canvas'].pack(side=tk.LEFT, anchor=tk.N)
        Pallet.blockPallets['scroll']['window']['trueYbar'] = ttk.Scrollbar(Pallet.blockPallets['window'], orient=tk.VERTICAL,
            command=Pallet.blockPallets['scroll']['window']['canvas'].yview, style='pallet.Vertical.TScrollbar')
        Pallet.blockPallets['scroll']['window']['trueYbar'].pack(side=tk.RIGHT, fill=tk.Y)
        Pallet.blockPallets['scroll']['window']['canvas'].configure(yscrollcommand=Pallet.blockPallets['scroll']['window']['trueYbar'].set)

        fakeYbarOnBlockPalletBackground = tk.Frame(Pallet.blockPallets['window'], width=16, bg='#888')
        fakeYbarOnBlockPalletBackground.pack_propagate(False)
        Pallet.blockPallets['scroll']['window']['fakeYbar'] = tk.Frame(fakeYbarOnBlockPalletBackground,
            width=16, height=20, bg='#77d')
        #fakeYbarOnBlockPalletBackground.pack(side=tk.LEFT, fill=tk.Y)

        Pallet.blockPallets['sack']['window'] = ttk.Frame(Pallet.blockPallets['window'],
            padding=(10,10,0,0), style='blockSack.TFrame')
        Pallet.blockPallets['sack']['window'].bind(
            '<Configure>', lambda e: Pallet.blockPallets['scroll']['window']['canvas'].configure(scrollregion=Pallet.blockPallets['scroll']['window']['canvas'].bbox('all'))
        )
        #Pallet.blockPallets['sack']['window'].bind('<MouseWheel>', self.__mouseWheelOnBlockZone)
        Pallet.blockPallets['scroll']['window']['canvas'].create_window((0, 0), window=Pallet.blockPallets['sack']['window'],
            width=Pallet.blockPallets['scroll']['window']['canvas']['width'], anchor='nw')

        Pallet.blockPallets['object'] = tk.Frame(Pallet.blockPalletsParent, width=self.blockAreaWidth,
            height=self.height-Pallet.__header.winfo_height()-21)
        Pallet.blockPallets['object'].pack_propagate(False)
        Pallet.blockPallets['object'].grid(row=0, column=0, sticky=tk.NSEW)

        Pallet.blockPallets['scroll']['object']['canvas'] = tk.Canvas(Pallet.blockPallets['object'],
            width=self.blockAreaWidth-self.scrollbarWidth,
            height=Pallet.blockPalletsParent.winfo_height(),
            bd=0, highlightthickness=0, bg=self.selectedTabColor)
        Pallet.blockPallets['scroll']['object']['canvas'].pack(side=tk.LEFT, anchor=tk.N)
        Pallet.blockPallets['scroll']['object']['trueYbar'] = ttk.Scrollbar(Pallet.blockPallets['object'], orient=tk.VERTICAL,
            command=Pallet.blockPallets['scroll']['object']['canvas'].yview,
            style='pallet.Vertical.TScrollbar')
        Pallet.blockPallets['scroll']['object']['trueYbar'].pack(side=tk.RIGHT, fill=tk.Y)
        Pallet.blockPallets['scroll']['object']['canvas'].configure(yscrollcommand=Pallet.blockPallets['scroll']['object']['trueYbar'].set)

        fakeYbarOnBlockPalletBackground = tk.Frame(Pallet.blockPallets['object'], width=16, bg='#888')
        fakeYbarOnBlockPalletBackground.pack_propagate(False)
        Pallet.blockPallets['scroll']['object']['fakeYbar'] = tk.Frame(fakeYbarOnBlockPalletBackground,
            width=16, height=20, bg='#77d')
        #fakeYbarOnBlockPalletBackground.pack(side=tk.LEFT, fill=tk.Y)

        Pallet.blockPallets['sack']['object'] = ttk.Frame(Pallet.blockPallets['object'],
            padding=(10,10,0,0), style='blockSack.TFrame')
        Pallet.blockPallets['sack']['object'].bind(
            '<Configure>',
            lambda e: Pallet.blockPallets['scroll']['object']['canvas'].configure(
                scrollregion=Pallet.blockPallets['scroll']['object']['canvas'].bbox('all'))
        )
        #Pallet.blockPallets['sack']['object'].bind('<MouseWheel>', self.__mouseWheelOnBlockZone)
        Pallet.blockPallets['scroll']['object']['canvas'].create_window((0, 0), window=Pallet.blockPallets['sack']['object'],
            width=Pallet.blockPallets['scroll']['object']['canvas']['width'], anchor='nw')

        Pallet.transformableParent = tk.Frame(Pallet.blockPallets['sack']['object'], bg=self.selectedTabColor)
        Pallet.transformableParent.pack(fill=tk.X)

        Pallet.blockPallets['window'].tkraise()
        for blockscript in Pallet.generalBlocks:
            self.drawblock(blockscript)
        for blockscript in Pallet.windowOnlyBlocks:
            self.drawblock(blockscript, WINDOWONLY=True)
        for blockscript in Pallet.objectOnlyBlocks:
            self.drawblock(blockscript, OBJECTONLY=True)
        Pallet.blockChanged = False

        variableSeparator = ttk.Separator(Pallet.blockPallets['sack']['window'])
        Pallet.style.configure('TSeparator', background='#222')
        self.packWidgetOnBlockArea(variableSeparator, 'both', fill=tk.BOTH, pady=(5, 15))
        def makeVariable(e):
            res = tk.simpledialog.askstring('新しく変数をつくる', '新しくつくる変数の名前を入力してください')
            if res != None and res != '':
                self.addblock(f'[{res}]', type='variable')
                self.reloadBlockArea()
        variableMakerBorder = tk.Frame(Pallet.blockPallets['sack']['window'], padx=3, pady=3, background=self.variableBlockColor)
        variableMaker = tk.Label(
            variableMakerBorder, text='新しく変数をつくる', font=('tkDefaeultFont', 12),
            padx=self.blockPadx, pady=self.blockPady + 2, fg='#ccc', bg='#2e5200', cursor='hand2'
        )
        variableMaker.pack()
        variableMaker.bind('<ButtonRelease-1>', makeVariable)
        self.packWidgetOnBlockArea(variableMakerBorder, 'window', anchor=tk.W, pady=(0, 10))
        variableMakerOnObject = usefull.cloneWidget(variableMakerBorder, master=Pallet.blockPallets['sack']['object'])
        variableMakerOnObject.winfo_children()[0].bind('<ButtonRelease-1>', makeVariable)
        self.packWidgetOnBlockArea(variableMakerOnObject, 'object', anchor=tk.W, pady=(0, 10))

        Pallet.style.configure('block.TCombobox', foreground='#ccc', borderwidth=0, arrowsize=10)
        Pallet.style.map('block.TCombobox', background=[('readonly','#999')], fieldbackground=[('readonly','#444')],
            selectbackground=[('readonly', '#444')], selectforeground=[('readonly', '#ccc')])
        root.option_add('*TCombobox*Listbox*Background', '#aaa')
        root.option_add('*TCombobox*Listbox*selectForeground', '#ccc')
        root.option_add('*TCombobox*Listbox*selectBackground', '#333')
        Pallet.style.configure('nestblock.TCombobox', foreground='#ccc', borderwidth=0, arrowsize=10)
        Pallet.style.map('nestblock.TCombobox', background=[('readonly','#999')], fieldbackground=[('readonly','#0a5520')],
            selectbackground=[('readonly', '#444')], selectforeground=[('readonly', '#ccc')])

        # 実際にコードを組み立てる場所
        codePallet = tk.Frame(self.__blockAndCodeParent, width=(self.width - self.blockAreaWidth),
            height=self.height-Pallet.__header.winfo_height()-21, bg='blue')
        codePallet.pack_propagate(False)
        codePallet.pack(side=tk.LEFT, anchor=tk.N)
        Pallet.__codeCanvas = tk.Canvas(codePallet, width=(self.width - self.blockAreaWidth - 19),
            height=self.height-Pallet.__header.winfo_height()-21-19,
            bd=0, highlightthickness=0, background='#555')
        Pallet.__codeCanvas.pack_propagate(False)
        Pallet.__codeCanvas.place(x=0, y=0)
        xbar = ttk.Scrollbar(codePallet, orient=tk.HORIZONTAL, command=Pallet.__codeCanvas.xview,
            style='pallet.Horizontal.TScrollbar')
        xbar.pack(side=tk.BOTTOM, fill=tk.X)
        Pallet.__codeCanvas.configure(xscrollcommand=xbar.set)
        ybar = ttk.Scrollbar(codePallet, orient=tk.VERTICAL, command=Pallet.__codeCanvas.yview,
            style='pallet.Vertical.TScrollbar')
        self.__ybar = ybar
        ybar.pack(side=tk.RIGHT, fill=tk.Y)
        Pallet.__codeCanvas.configure(yscrollcommand=ybar.set)

        fakeYbarBackground = tk.Frame(self.__blockAndCodeParent, width=16, height=Pallet.__codeCanvas['height'], bg='#888')
        fakeYbarBackground.pack_propagate(False)
        self.fakeYbar = tk.Frame(fakeYbarBackground, width=16, height=200, bg='#77d')
        self.fakeYbar.place()
        #fakeYbarBackground.pack(side=tk.LEFT)

        Pallet.codeFrame = tk.Frame(
            self.__blockAndCodeParent,
            width=(self.width - self.blockAreaWidth - 30), height=self.height,
            background='#555', padx=10, pady=10
        )
        Pallet.codeFrame.bind(
            '<Configure>', lambda e: Pallet.__codeCanvas.configure(scrollregion=Pallet.__codeCanvas.bbox('all'))
        )
        Pallet.__codeCanvas.create_window((0, 0), window=Pallet.codeFrame, anchor='nw')

        self.initCodeMenu()

        ''' init block cursor '''
        Pallet.style.configure('blockCursor.TFrame', background='#666')
        Pallet.blockCursor = self.createBlockCursor(parent=self.codeFrame)
        self.codeInsertPosition = None

        self.__drag_start_x = 0
        self.__drag_start_y = 0

        '''block parts style'''
        Pallet.style.configure('contentsBorder.TFrame', background=self.nestblockcolor)

        '''init costume tab'''
        graphicFrame = tk.Frame(
            Pallet.topFrame, width=self.width, height=self.height, bg='#555'
        )
        Pallet.notebook.add(graphicFrame, text='衣裳', state=tk.HIDDEN)

        Pallet.frameofWardrobe = tk.Frame(graphicFrame, width=170, height=self.bodyHeight)
        Pallet.frameofWardrobe.grid_propagate(False)
        Pallet.frameofWardrobe.pack(side=tk.LEFT, anchor=tk.N)

        Pallet.costumeInWorkName = tk.StringVar()
        costumeNameEntry = tk.Entry(graphicFrame, bd=0,
            insertwidth=1, insertbackground='#ccc', foreground='#ccc', background='#666',
            width=16, justify=tk.LEFT, font=('tkDefaeultFont', 24), textvariable=Pallet.costumeInWorkName
        )
        def changeCostumeName():
            time.sleep(1)
            print(Pallet.costumeInWorkOriginalName, ' -> ', Pallet.costumeInWorkName.get())
            Pallet.costumeCondition.set('更新完了!')
            if os.path.isfile(f'savedData/{Pallet.__share.title}/costume/{Pallet.objects.nameofObject[Pallet.objects.indexofCurrentlySelectedObj]}/{Pallet.costumeInWorkName.get()}.png') and \
                Pallet.costumeInWorkOriginalName != Pallet.costumeInWorkName.get():
                tk.messagebox.showwarning(title='衣裳名の間違い', message=f'既にその名前({Pallet.costumeInWorkName.get()})は他の衣裳で使用されています。\n他の名前を試してください。')
                #costumeNameEntry.delete(0, tk.END)
                #costumeNameEntry.insert(tk.END, )
            else:
                os.rename(f'savedData/{Pallet.__share.title}/costume/{Pallet.objects.nameofObject[Pallet.objects.indexofCurrentlySelectedObj]}/{Pallet.costumeInWorkOriginalName}.png',
                    f'savedData/{Pallet.__share.title}/costume/'
                    f'{Pallet.objects.nameofObject[Pallet.objects.indexofCurrentlySelectedObj]}/{Pallet.costumeInWorkName.get()}.png')
                self.updateCostumePreview()
        def keyReleasedOnCostumeName():
            Pallet.costumeName[Pallet.indexofSelectedCostume]['text'] = Pallet.costumeInWorkName.get()
            if Pallet.costumeNameChangeThread != None:
                threadId = Pallet.costumeNameChangeThread.native_id
                if ctypes.pythonapi.PyThreadState_SetAsyncExc(threadId, ctypes.py_object(SystemExit)) > 1:
                    ctypes.pythonapi.PyThreadState_SetAsyncExc(threadId, 0)
                    print('Failure in raising exception')
            Pallet.costumeNameChangeThread = threading.Thread(target=changeCostumeName)
            Pallet.costumeNameChangeThread.daemon = True
            Pallet.costumeNameChangeThread.start()
            Pallet.costumeCondition.set('更新中・・・')
        costumeNameEntry.bind('<KeyRelease>', lambda e: keyReleasedOnCostumeName())
        costumeNameEntry.pack(side=tk.LEFT, anchor=tk.N, padx=(10, 0), pady=10)

        Pallet.costumeCondition = tk.StringVar()
        tk.Label(
            graphicFrame, textvariable=Pallet.costumeCondition, font=('tkDefaeultFont', 12),
            padx=self.blockPadx, pady=self.blockPady + 2, fg='#ccc', bg='#555'
        ).pack(side=tk.LEFT, anchor=tk.N, padx=(3, 0), pady=16)
        Pallet.costumeCondition.set('問題なし')
    def initHeader(self):
        Pallet.__header = ttk.Frame(Pallet.topFrame, width=self.width, padding=(0, 10, 10, 0), style='header.TFrame')
        Pallet.style.configure('header.TFrame', background='#777')
        Pallet.objectName = tk.StringVar()
        def changeObjectName(event):
            Pallet.objects.setName(Pallet.objectName.get())
        Pallet.objectNameEntry = tk.Entry(Pallet.__header, bd=0, width=30, justify=tk.RIGHT,
            insertwidth=2, insertbackground='black', state='readonly',
            foreground='black', background=Pallet.style.lookup('header.TFrame', 'background'),
            readonlybackground=Pallet.style.lookup('header.TFrame', 'background'),
            font=('tkDefaeultFont', 24), textvariable=Pallet.objectName
        )
        Pallet.objectNameEntry.bind('<KeyRelease>', changeObjectName)
        Pallet.objectNameEntry.pack(side=tk.RIGHT)
        Pallet.__header.pack(fill=tk.X)
    def initAfterObjInit(self):
        for i in range(Pallet.objects.numberofObj):
            Pallet.codes.append([])

        Pallet.codeFrame.update()
        self.isFirstStarterBlock = True
        self.addcode('プログラムが始まったら')
        self.addcode('ウィンドウの幅を[1000]pxに、高さを[618]pxにする')
        self.addcode('ウィンドウの背景色を[#000]にする')

        Pallet.objects.bind('<focus shift>', self.objFocusShiftHandler)
        Pallet.objects.bind('<object added>', self.objAddedHandler)
        Pallet.objects.bind('<object deleted>', self.objDeletedHandler)

        Pallet.objectName.set(Pallet.objects.nameofObject[Pallet.objects.indexofCurrentlySelectedObj])
        self.objFocusShiftHandler()
    def reset(self):
        '''新しいプロジェクトを読み込む前に初期化'''
        for code in Pallet.widgetsOnCodeZone:
            code.destroy()
        Pallet.widgetsOnCodeZone = []
        for i in range(len(Pallet.codes)):
            Pallet.codes[i] = []
        self.isFirstStarterBlock = True
        Pallet.variableBlocks = []
        Pallet.blocks2controlVariables = []
    def setup(self):
        '''新しいプロジェクトを読み込んだ後に設定'''
        self.addblock(f'+variableSetter[0]>{Pallet.variableBlocks[0][1:-1]}', type='blocks2controlVariables')
    '''-----------------
    |  object handlers  |
    ------------------'''
    def objAddedHandler(self):
        Pallet.codes.append([])
        Pallet.wordrobe.append(None)
    def objDeletedHandler(self, objectIndex):
        Pallet.codes.remove(Pallet.codes[objectIndex])
        Pallet.wordrobe.remove(Pallet.wordrobe[objectIndex])
    def objFocusShiftHandler(self):
        Pallet.objectName.set(Pallet.objects.nameofObject[Pallet.objects.indexofCurrentlySelectedObj])
        self.reloadBlockArea()
        for area in ['window', 'object']:
            Pallet.blockPallets['scroll'][area]['fakeYbar'].place_forget()
            if int(Pallet.blockPallets['sack'][area].winfo_height()) > Pallet.blockPalletsParent['height']:
                if area == 'window':
                    Pallet.blockPallets['sack'][area].bind('<MouseWheel>', self.__mouseWheelOnWindowBlockZone)
                else:
                    Pallet.blockPallets['sack'][area].bind('<MouseWheel>', self.__mouseWheelOnObjectBlockZone)
            else:
                Pallet.blockPallets['sack'][area].unbind('<MouseWheel>')
        #print(Pallet.blockPalletsParent['height'])
        #print(Pallet.blockPallets['sack']['window'].winfo_height())
        '''if int(Pallet.blockPallets['sack']['object'].winfo_height()) == Pallet.blockPalletsParent['height']:
            print('need scroll')
            print(Pallet.__scrollOnblockPallet['trueYbar'].get())
            print(Pallet.__scrollOnblockPallet['canvas']['height'])
            Pallet.__scrollOnblockPallet['fakeYbar']['height'] = int(
                int(Pallet.__scrollOnblockPallet['canvas']['height']) * Pallet.__scrollOnblockPallet['trueYbar'].get()[1]
                )
            print(Pallet.__scrollOnblockPallet['fakeYbar']['height'])
            Pallet.__scrollOnblockPallet['fakeYbar'].place(relx=0, rely=Pallet.__scrollOnblockPallet['trueYbar'].get()[0])
        else:
            print('not need scroll')
            Pallet.__scrollOnblockPallet['fakeYbar'].place_forget()
        print(Pallet.blockPalletsParent['height'])'''
        for code in Pallet.widgetsOnCodeZone:
            code.destroy()
        Pallet.widgetsOnCodeZone = []
        Pallet.fitTermsOnCodeZone = []
        Pallet.entryOnCodeZoneInfo['frame'] = []
        Pallet.entryOnCodeZoneInfo['numberInBlock'] = []
        self.isFirstStarterBlock = True
        if Pallet.codes[Pallet.objects.indexofCurrentlySelectedObj] == []:
            self.addcode('幕が上がったとき')
        else:
            for loopi, blockscript in enumerate(Pallet.codes[Pallet.objects.indexofCurrentlySelectedObj]):
                self.addcode(blockscript, insertPosition=loopi, DRAWONLY=True)
        usefull.bindAllChildren(Pallet.__codeCanvas, '<MouseWheel>', self.__mouseWheelOnCodeZone)
        if Pallet.objects.indexofCurrentlySelectedObj == 0:
            Pallet.objectNameEntry['state'] = 'readonly'
            Pallet.notebook.tab(Pallet.notebook.tabs()[1], state = tk.HIDDEN)
        else:
            Pallet.objectNameEntry['state'] = tk.NORMAL
            Pallet.notebook.tab(Pallet.notebook.tabs()[1], state = tk.NORMAL)
            self.updateCostumePreview()
            Pallet.wordrobe[Pallet.objects.indexofCurrentlySelectedObj - 1].tkraise()
    def updateCostumePreview(self, ACTORINDEX=None):
        if ACTORINDEX == 0:
            print('[ERROR] Incorrect actor index: Stage does not wear costumes.')
            return False
        if ACTORINDEX == None:
            ACTORINDEX = Pallet.objects.indexofCurrentlySelectedObj
        Pallet.costumeName = []
        wardrobe = tk.Frame(Pallet.frameofWardrobe, padx=10, pady=10, width=Pallet.frameofWardrobe['width'], height=self.bodyHeight, background=self.selectedTabColor)
        wardrobe.pack_propagate(False)
        wardrobe.grid(row=0, column=0)
        def switchCostume(selectedBorder, index):
            for costume in wardrobe.winfo_children()[:-1]:
                costume['bg'] = '#777'
            selectedBorder['bg'] = Share.maincolor
            Pallet.costumeInWorkName.set(selectedBorder.winfo_children()[0].winfo_children()[1]['text'])
            Pallet.costumeInWorkOriginalName = selectedBorder.winfo_children()[0].winfo_children()[1]['text']
            Pallet.indexofSelectedCostume = index
            Pallet.objects.actors['indexofDefaultCostume'][Pallet.objects.indexofCurrentlySelectedObj] = index
        def bindSwicthing(costumeBorder, index):
            usefull.bindAllChildren(costumeBorder, '<ButtonRelease-1>', lambda e: switchCostume(costumeBorder, index))
        Pallet.indexofSelectedCostume = 0
        for loopi, i in enumerate(os.listdir(f'savedData/{Pallet.__share.title}/costume/{Pallet.objects.nameofObject[ACTORINDEX]}')):
            costumeBorder = tk.Frame(wardrobe, width=150, height=150, bg='#777')
            costumeBorder.pack_propagate(False)
            costume = tk.Frame(costumeBorder, width=10, height=10, pady=10, bg='#444')
            thumbnail = tk.PhotoImage(file=
                thumbnailCache.cache(f'savedData/{Pallet.__share.title}/costume/{Pallet.objects.nameofObject[ACTORINDEX]}/' + i)
            )
            Pallet.costumeTkPhotoImageThumnail.append(thumbnail)
            tk.Label(costume, background=costume['bg'],
                image=Pallet.costumeTkPhotoImageThumnail[Pallet.costumeTkPhotoImageThumnail.index(thumbnail)], width=100, height=100,).pack()
            costumeName = ttk.Label(costume, text=os.path.splitext(i)[0], foreground='#ccc', background='#444',
                font=('tkDefaeultFont', 12))
            costumeName.pack()
            Pallet.costumeName.append(costumeName)
            #if loopi == Pallet.objects.actors['indexofDefaultCostume'] and Pallet.objects.indexofCurrentlySelectedObj == ACTORINDEX:
            #    Pallet.costumeInWorkName.set(costumeName['text'])
            costume.pack(padx=3, pady=3, fill=tk.BOTH, expand=True)
            costumeBorder.pack(anchor=tk.NW, pady=(0, 10))
            if loopi == Pallet.objects.actors['indexofDefaultCostume'][Pallet.objects.indexofCurrentlySelectedObj]:
                switchCostume(costumeBorder, loopi)
                if Pallet.objects.indexofCurrentlySelectedObj == ACTORINDEX:
                    Pallet.costumeInWorkName.set(costumeName['text'])
            bindSwicthing(costumeBorder, loopi)
        def importCostumeImage(ACTORINDEX):
            imagePath = tk.filedialog.askopenfilename()
            if imagePath != '':
                Pallet.objects.addCostume(imagePath, ACTORINDEX)
                self.updateCostumePreview(ACTORINDEX)
        dressmaker = tk.Frame(wardrobe, width=150, height=150, bg='#666', cursor='hand2')
        dressmaker.pack_propagate(False)
        dressmakerLabel = tk.Label(dressmaker, text='衣裳を追加', foreground='#ccc', bg=dressmaker['bg'],
            font=('tkDefaeultFont', 15))
        dressmakerLabel.pack(expand=True)
        usefull.bindAllChildren(dressmaker, '<ButtonRelease-1>', lambda e: importCostumeImage(Pallet.objects.indexofCurrentlySelectedObj))
        dressmaker.pack(anchor=tk.NW)
        Pallet.wordrobe[ACTORINDEX - 1] = wardrobe
    def __mouseWheelOnWindowBlockZone(self, event):
        Pallet.blockPallets['scroll']['window']['canvas'].yview_scroll(-(event.delta // 120), 'units')
        Pallet.blockPallets['scroll']['window']['fakeYbar']['height'] = int(
            int(Pallet.blockPallets['scroll']['window']['canvas']['height']) *
            Pallet.blockPallets['scroll']['window']['trueYbar'].get()[1]
            )
        Pallet.blockPallets['scroll']['window']['fakeYbar'].place(relx=0, rely=Pallet.blockPallets['scroll']['window']['trueYbar'].get()[0])
    def __mouseWheelOnObjectBlockZone(self, event):
        Pallet.blockPallets['scroll']['object']['canvas'].yview_scroll(-(event.delta // 120), 'units')
        Pallet.blockPallets['scroll']['object']['fakeYbar']['height'] = int(
            int(Pallet.blockPallets['scroll']['object']['canvas']['height']) *
            Pallet.blockPallets['scroll']['object']['trueYbar'].get()[1]
            )
        Pallet.blockPallets['scroll']['object']['fakeYbar'].place(relx=0, rely=Pallet.blockPallets['scroll']['object']['trueYbar'].get()[0])
    def __mouseWheelOnCodeZone(self, event):
        Pallet.__codeCanvas.yview_scroll(-(event.delta // 120), 'units')
        self.fakeYbar.place(relx=0, rely=self.__ybar.get()[0])
        self.fakeYbar['height'] = int(int(Pallet.__codeCanvas['height']) * self.__ybar.get()[1])
    '''------------------------------
    |  Block manipulation functions  |
    -------------------------------'''
    def addblock(self, blockscript, WINDOWONLY=False, OBJECTONLY=False, type='normal'):
        Pallet.blocks.append(blockscript)

        if type == 'transformableBlock':
            Pallet.transformableBlock.append(blockscript)
        elif WINDOWONLY == True:
            Pallet.windowOnlyBlocks.append(blockscript)
        elif OBJECTONLY == True:
            Pallet.objectOnlyBlocks.append(blockscript)
        elif type == 'variable':
            Pallet.variableBlocks.append(blockscript)
        elif type == 'blocks2controlVariables':
            Pallet.blocks2controlVariables.append(blockscript)
        else:
            Pallet.generalBlocks.append(blockscript)

        if type == 'starter':
            Pallet.starterBlocks.append(blockscript)
        Pallet.blockChanged = True
        return
    def drawblock(self, blockscript, WINDOWONLY=False, OBJECTONLY=False, **kwargs):
        area = None
        if WINDOWONLY:
            self.__drawblock(blockscript, area='window', **kwargs)
        elif OBJECTONLY:
            self.__drawblock(blockscript, area='object', **kwargs)
        else:
            self.__drawblock(blockscript, area='window', **kwargs)
            self.__drawblock(blockscript, area='object', **kwargs)
    def bindEntry(self, entry, blockindex):
        def synchroofChanges(blockI, entry, index):
            blockscript = Pallet.blocks[blockI]
            isValue = self.isValue(blockscript)
            if isValue:
                blockscript = blockscript[1:-1]
            for loopIdx, i in enumerate(re.finditer('\[', blockscript)):
                if loopIdx == index:
                    blockscript = blockscript[:i.end()] + entry.get() + blockscript[blockscript.find(']', i.end()):]
            if isValue:
                Pallet.blocks[blockI] = '[' + blockscript + ']'
            else:
                Pallet.blocks[blockI] = blockscript
            return
        INDEX = self.numberofEntry
        entry.bind('<KeyPress>', lambda e: synchroofChanges(blockindex, entry, INDEX))
        entry.bind('<KeyRelease>', lambda e: synchroofChanges(blockindex, entry, INDEX))
        self.numberofEntry += 1
    def bindCombobox(self, combobox, blockindex):
        def synchroofChanges(blockI, combobox, index):
            combobox.selection_clear()
            blockscript = Pallet.blocks[blockI]
            for loopi, i in enumerate(re.finditer('\{', blockscript)):
                if loopi == index:
                    contents = blockscript[i.end():blockscript.find('}', i.end())].split('|')
                    for loopi in range(len(contents)):
                        if contents[loopi][0] == '*':
                            contents[loopi] = contents[loopi][1:]
                        if contents[loopi] == combobox.get():
                            contents[loopi] = '*' + contents[loopi]
                    blockscript = blockscript[:i.end()] + '|'.join(contents) + blockscript[blockscript.find('}', i.end()):]
            Pallet.blocks[blockI] = blockscript
            return
        INDEX = self.numberofCombobox
        combobox.bind('<<ComboboxSelected>>', lambda e: synchroofChanges(blockindex, combobox, INDEX))
        self.numberofCombobox += 1
    def __drawblock(self, blockscript, area=None, **kwargs):
        self.numberofEntry = 0
        self.numberofCombobox = 0
        BLOCKINDEX = Pallet.blocks.index(blockscript)
        def bindVariableSetter(variableSetter, blockindex):
            def synchroofChanges(variableSetter, blockI):
                variableSetter.selection_clear()
                Pallet.blocks[blockI] = Pallet.blocks[blockI].split('>')[0] + '>' + variableSetter.get()
                return
            variableSetter.bind('<<ComboboxSelected>>', lambda e: synchroofChanges(variableSetter, blockindex))
        def bindWidget(widget):
            if widget.widgetName == 'entry':
                self.bindEntry(widget, BLOCKINDEX)
            elif widget.widgetName == 'ttk::combobox':
                if blockscript[:15] == '+variableSetter':
                    bindVariableSetter(widget, BLOCKINDEX)
                else:
                    self.bindCombobox(widget, BLOCKINDEX)
            else:
                self.prepareToDragWidget(widget, BLOCKINDEX, blockPosition, **kwargs)
        blockPosition = len(Pallet.blocksOnBlockZone[area])
        block = None
        if blockscript[0] == '#':
            block = self.analyzeBlockScript(blockscript, parent=Pallet.blockPallets['sack'][area], **kwargs)
            self.prepareToDragWidget(block.winfo_children()[0], BLOCKINDEX, blockPosition, **kwargs)
            def commentEntryChanged(event):
                Pallet.blocks[BLOCKINDEX] = '#' + event.widget.get()
                event.widget['width'] = usefull.getEastAsianWidthCount(event.widget.get())
            block.winfo_children()[0].winfo_children()[0].bind('<KeyRelease>', commentEntryChanged)
        else:
            block = self.analyzeBlockScript(blockscript, parent=Pallet.transformableParent if blockscript == '衣裳を{}にする' else Pallet.blockPallets['sack'][area],
                packHandler=bindWidget, **kwargs)
        block.pack(anchor=tk.W, pady=(0, 10))
        Pallet.blocksOnBlockZone[area].append(block)
        return
    def packWidgetOnBlockArea(self, widget, area, **kwargs):
        '''
        ブロック置き場に置くブロック以外のwidgetを
        初めてブロック置き場にpackするのに使う

        Parameters
        ----------
        widget :
            ブロック置き場に置くブロック以外のwidget
        area: char
            このwidgetをpackする場所
            'window' か 'object' か 'both' ('window'と'object'両方) か
        **kwargs : dict
            packのオプション

        Returns
        -------
        None
        '''
        if area == 'both':
            copiedWidget = usefull.cloneWidget(widget)
            copiedWidget.pack(**kwargs)
            Pallet.widgetsOnBlockZone['window'].append(
                {'widget': copiedWidget, 'packPosition': len(Pallet.blocksOnBlockZone['window']) - 1, 'packOption': kwargs}
            )
            copiedWidget2 = usefull.cloneWidget(widget, Pallet.blockPallets['sack']['object'])
            Pallet.widgetsOnBlockZone['object'].append(
                {'widget': copiedWidget2, 'packPosition': len(Pallet.blocksOnBlockZone['object']) - 1, 'packOption': kwargs}
            )
        else:
            widget.pack(**kwargs)
            Pallet.widgetsOnBlockZone[area].append(
                {'widget': widget, 'packPosition': len(Pallet.blocksOnBlockZone[area]) - 1, 'packOption': kwargs}
            )
    def reloadBlockArea(self):
        if Pallet.objects.indexofCurrentlySelectedObj != 0:
            if Pallet.costumeBlockCreated:
                for block in Pallet.transformableParent.winfo_children():
                    block.destroy()
                self.drawblock('衣裳を{}にする', OBJECTONLY=True, type='transformable')
            else:
                Pallet.costumeBlockCreated = True
                self.addblock('衣裳を{}にする', OBJECTONLY=True, type='transformable')
        if Pallet.blockChanged:
            for block in Pallet.blocksOnBlockZone['window']:
                block.destroy()
            for block in Pallet.blocksOnBlockZone['object']:
                block.destroy()
            Pallet.blocksOnBlockZone['window'] = []
            Pallet.blocksOnBlockZone['object'] = []
            for widget in Pallet.widgetsOnBlockZone['window']:
                widget['widget'].pack_forget()
            for widget in Pallet.widgetsOnBlockZone['object']:
                widget['widget'].pack_forget()
            for blockscript in Pallet.generalBlocks:
                self.drawblock(blockscript)
            for blockscript in Pallet.windowOnlyBlocks:
                self.drawblock(blockscript, WINDOWONLY=True)
            for blockscript in Pallet.objectOnlyBlocks:
                self.drawblock(blockscript, OBJECTONLY=True)
            for widget in Pallet.widgetsOnBlockZone['window']:
                widget['widget'].pack(widget['packOption'])
            for widget in Pallet.widgetsOnBlockZone['object']:
                widget['widget'].pack(widget['packOption'])
            for blockscript in Pallet.variableBlocks:
                self.drawblock(blockscript, type='variable')
            for blockscript in Pallet.blocks2controlVariables:
                self.drawblock(blockscript)
            Pallet.blockChanged = False
        if Pallet.objects.windowSelected:
            Pallet.blockPallets['window'].tkraise()
        else:
            Pallet.blockPallets['object'].tkraise()
    '''--------------
    |  Drag a block  |
    ---------------'''
    def prepareToDragWidget(self, widget, blockindex, blockPosition, **kwargs):
        widget.bind('<ButtonPress-1>', lambda event: self.__blockdragstart(event, blockindex, blockPosition, **kwargs))
        if self.isTerm(Pallet.blocks[blockindex]):
            widget.bind('<B1-Motion>', lambda event: self.termBlockDragging(event))
            widget.bind('<ButtonRelease-1>', lambda event: self.termBlockDragFinish(event))
        elif self.isValue(Pallet.blocks[blockindex]):
            widget.bind('<B1-Motion>', lambda event: self.valueBlockDragging(event))
            widget.bind('<ButtonRelease-1>', lambda event: self.valueBlockDragFinish(event))
        else:
            widget.bind('<B1-Motion>', lambda event: self.__blockdragging(event))
            widget.bind('<ButtonRelease-1>', lambda event: self.__blockdragfinish(event))
    def __blockdragstart(self, event, blockid, blockPosition, **kwargs):
        Pallet.draggingBlock['blockscript'] = Pallet.blocks[blockid]
        widget = None
        if Pallet.objects.windowSelected:
            widget = Pallet.blocksOnBlockZone['window'][blockPosition]
        else:
            widget = Pallet.blocksOnBlockZone['object'][blockPosition]
        self.__drag_start_x = event.x
        self.__drag_start_y = event.y
        Pallet.draggingBlock['widget'] = self.analyzeBlockScript(Pallet.draggingBlock['blockscript'],
            self.__blockAndCodeParent, dragging=True, **kwargs)

        Pallet.__originalPositionOfBlock['x'] = widget.winfo_x()
        Pallet.draggingBlock['widget'].update()
        if Pallet.objects.windowSelected:
            Pallet.__originalPositionOfBlock['y'] = widget.winfo_y()
        else:
            Pallet.__originalPositionOfBlock['y'] = widget.winfo_y() - Pallet.blockPallets['scroll']['object']['canvas'].canvasy(0)
        Pallet.draggingBlock['widget'].place(
            x=Pallet.__originalPositionOfBlock['x'],
            y=Pallet.__originalPositionOfBlock['y'])
        return
    def __blockdragging(self, event):
        Pallet.draggingBlock['widget'].place(x = Pallet.__originalPositionOfBlock['x'] + event.x - self.__drag_start_x,
            y = Pallet.__originalPositionOfBlock['y'] + event.y - self.__drag_start_y)
        if event.x_root > Pallet.codeFrame.winfo_rootx():
            if event.y_root > Pallet.widgetsOnCodeZone[-1].winfo_rooty():
                '''一番下にブロックカーソルを表示する場合'''
                self.displayBlockCursor(insertPosition=len(Pallet.widgetsOnCodeZone))
            else:
                for roopi, code in enumerate(Pallet.widgetsOnCodeZone):
                    if (abs(code.winfo_rooty() - event.y_root) < self.blockHeight // 2):
                        self.displayBlockCursor(insertPosition=roopi)
    def termBlockDragging(self, event):
        Pallet.draggingBlock['widget'].place(x = Pallet.__originalPositionOfBlock['x'] + event.x - self.__drag_start_x,
            y = Pallet.__originalPositionOfBlock['y'] + event.y - self.__drag_start_y)
        if Pallet.fitTermsOnCodeZone != [] and event.x_root > Pallet.codeFrame.winfo_rootx():
            for fitTerm in Pallet.fitTermsOnCodeZone:
                if (
                Pallet.draggingBlock['widget'].winfo_rootx() > fitTerm.winfo_rootx() and
                fitTerm.winfo_rootx() + fitTerm.winfo_width() > Pallet.draggingBlock['widget'].winfo_rootx() and
                Pallet.draggingBlock['widget'].winfo_rooty() > fitTerm.winfo_rooty() and
                fitTerm.winfo_rooty() + fitTerm.winfo_height() > Pallet.draggingBlock['widget'].winfo_rooty()
                ):
                    fitTerm['width'] = Pallet.draggingBlock['widget'].winfo_width()
                    fitTerm.coords('fitTermDent', 10, 0, 0, fitTerm.winfo_height() // 2, 10, fitTerm.winfo_height(),
                        fitTerm.winfo_width()-10, fitTerm.winfo_height(), fitTerm.winfo_width(), fitTerm.winfo_height() // 2,
                        fitTerm.winfo_width()-10, 0)
    def valueBlockDragging(self, event):
        Pallet.draggingBlock['widget'].place(x = Pallet.__originalPositionOfBlock['x'] + event.x - self.__drag_start_x,
            y = Pallet.__originalPositionOfBlock['y'] + event.y - self.__drag_start_y)
        if event.x_root > Pallet.codeFrame.winfo_rootx():
            for entry in Pallet.entryOnCodeZoneInfo['frame']:
                if self.areBlockAndSomethingOverlapping(entry):
                    entry.winfo_children()[0]['width'] = 8
                else:
                    entry.winfo_children()[0]['width'] = 4
    def __blockdragfinish(self, event):
        widget = Pallet.draggingBlock['widget']
        for func in Pallet.funcs['<block drop>']:
            func()
        if (
        widget.winfo_rootx() + widget.winfo_width() > Pallet.blockCursor.winfo_rootx() and
        Pallet.blockCursor.winfo_rootx() + Pallet.blockCursor.winfo_width() > widget.winfo_rootx() and
        widget.winfo_rooty() + widget.winfo_height() > Pallet.blockCursor.winfo_rooty() and
        Pallet.blockCursor.winfo_rooty() + Pallet.blockCursor.winfo_height() > widget.winfo_rooty() and
        Pallet.funcs['<block drop>'] == []
        ):
            self.addcode(Pallet.draggingBlock['blockscript'], insertPosition=self.codeInsertPosition)

        widget.destroy()
        self.hiddenBlockCursor()
        return
    def termBlockDragFinish(self, event):
        widget = Pallet.draggingBlock['widget']
        for func in Pallet.funcs['<block drop>']:
            func()
        changed = False
        for fitTerm in Pallet.fitTermsOnCodeZone:
            if (
            event.x_root > fitTerm.winfo_rootx() and
            fitTerm.winfo_rootx() + fitTerm.winfo_width() > event.x_root and
            event.y_root > fitTerm.winfo_rooty() and
            fitTerm.winfo_rooty() + fitTerm.winfo_height() > event.y_root
            ):
                parent = fitTerm._nametowidget(fitTerm.winfo_parent())
                grandP = parent._nametowidget(parent.winfo_parent())
                codeIdx = Pallet.widgetsOnCodeZone.index(grandP._nametowidget(grandP.winfo_parent()))
                codeScript = Pallet.codes[Pallet.objects.indexofCurrentlySelectedObj][codeIdx]
                codeScript = codeScript.replace('<>', f"{Pallet.draggingBlock['blockscript']}")
                Pallet.codes[Pallet.objects.indexofCurrentlySelectedObj][codeIdx] = codeScript
                changed = True
        widget.destroy()
        if changed:
            self.objFocusShiftHandler()
        #for fitTerm in Pallet.fitTermsOnCodeZone:
            #fitTerm['width'] = 40
            #fitTerm.coords('fitTermDent', 10, 0, 0, fitTerm.winfo_height() // 2, 10, fitTerm.winfo_height(),
            #    self.fitTermDefaultWidth-10, fitTerm.winfo_height(), self.fitTermDefaultWidth, fitTerm.winfo_height() // 2,
            #    self.fitTermDefaultWidth-10, 0)
        return
    def valueBlockDragFinish(self, event):
        widget = Pallet.draggingBlock['widget']
        for func in Pallet.funcs['<block drop>']:
            func()
        if widget.winfo_rootx() > self.blockAreaWidth:
            changed = False
            for i in range(len(Pallet.entryOnCodeZoneInfo['frame'])):
                Pallet.entryOnCodeZoneInfo['frame'][i].winfo_children()[0]['width'] = 4
                if self.areBlockAndSomethingOverlapping(Pallet.entryOnCodeZoneInfo['frame'][i]):
                    #Pallet.entryOnCodeZoneInfo['frame'][i].winfo_children()[0]['bg'] = 'yellow'
                    codeWidgetofEntry = Pallet.entryOnCodeZoneInfo['frame'][i]
                    while str(Pallet.codeFrame).count('.!') != str(codeWidgetofEntry).count('.!') - 1:
                        codeWidgetofEntry = codeWidgetofEntry._nametowidget(codeWidgetofEntry.winfo_parent())
                    codeIdx = Pallet.widgetsOnCodeZone.index(codeWidgetofEntry)
                    codeScript = Pallet.codes[Pallet.objects.indexofCurrentlySelectedObj][codeIdx]
                    #print(Pallet.entryOnCodeZoneInfo['numberInBlock'][i])
                    entrys = []
                    readingEntry = {'start': None, 'end': None, 'appended': False}
                    for loopi, char in enumerate(codeScript):
                        if char == '[':
                            readingEntry['start'] = loopi
                            readingEntry['appended'] = False
                        elif char == ']' and not readingEntry['appended']:
                            readingEntry['end'] = loopi + 1
                            entrys.append({'start': readingEntry['start'], 'end': readingEntry['end']})
                            readingEntry['appended'] = True
                    for loopi, entry in enumerate(entrys):
                        if loopi + 1 == Pallet.entryOnCodeZoneInfo['numberInBlock'][i]:
                            codeScript = (
                                codeScript[:entry['start']] +
                                Pallet.draggingBlock['blockscript'][0] + '*' + Pallet.draggingBlock['blockscript'][1:] +
                                codeScript[entry['end']:])
                    Pallet.codes[Pallet.objects.indexofCurrentlySelectedObj][codeIdx] = codeScript
                    changed = True
            widget.destroy()
            if changed:
                self.objFocusShiftHandler()
        else:
            widget.destroy()
    def areBlockAndSomethingOverlapping(self, something):
        return (
            (Pallet.draggingBlock['widget'].winfo_rootx() - something.winfo_rootx()) ** 2 +
            (Pallet.draggingBlock['widget'].winfo_rooty() - something.winfo_rooty()) ** 2
            < 100
            )
    '''--------------
    |  block cursor  |
    ---------------'''
    def createBlockCursor(self, parent):
        return ttk.Frame(parent, style='blockCursor.TFrame')
    def displayBlockCursor(self, insertPosition=0):
        if insertPosition == self.codeInsertPosition:
            return
        Pallet.blockCursor.destroy()
        Pallet.blockCursor = self.createBlockCursor(parent=self.codeFrame)
        Pallet.blockCursor['width'] = Pallet.draggingBlock['widget'].winfo_width()
        Pallet.blockCursor['height'] = Pallet.draggingBlock['widget'].winfo_height()
        if insertPosition != len(Pallet.widgetsOnCodeZone):
            codes = []
            self.isFirstStarterBlock = True
            for roopi, code in enumerate(Pallet.widgetsOnCodeZone):
                code.pack_forget()
                codes.append(code)
            for i in range(len(Pallet.widgetsOnCodeZone)):
                if i == insertPosition:
                    Pallet.blockCursor.pack(anchor=tk.W, pady=3)
                self.packCode(i)
        else:
            Pallet.blockCursor.pack(anchor=tk.W)
        self.codeInsertPosition = insertPosition
        return
    def hiddenBlockCursor(self):
        Pallet.blockCursor.pack_forget()
    '''-----------------------------
    |  Code manipulation functions  |
    ------------------------------'''
    def addcode(self, blockscript, insertPosition=None, **kwargs):
        if type(insertPosition) is int == False:
            print('[ERROR] The value of argument "insertPosition" must be of type int')
            return
        nestDepth = 0
        for bs in Pallet.codes[Pallet.objects.indexofCurrentlySelectedObj][:insertPosition]:
            if bs[-1] == '~':
                nestDepth += 1
            elif bs[0] == '~':
                nestDepth -= 1
        if '~~' in blockscript:
            ip = insertPosition
            for roopi, bs in enumerate(blockscript.split('~~')):
                if roopi == 0:
                    bs = bs + '~'
                elif roopi == len(blockscript.split('~~')) - 1:
                    bs = '~' + bs
                self.__addcode(bs, insertPosition=ip, nestDepth=nestDepth, **kwargs)
                ip += 1
        else:
            self.__addcode(blockscript, insertPosition=insertPosition, nestDepth=nestDepth, **kwargs)
    def __addcode(self, blockscript, DRAWONLY=False, OBJECTINDEX=None, TYPE='normal', insertPosition=None, nestDepth=0):
        if OBJECTINDEX == None:
            OBJECTINDEX = Pallet.objects.indexofCurrentlySelectedObj

        CODEID = insertPosition
        self.numberofEntry = 0
        def bindEntry(entry, CODEID):
            def synchroofChanges(event, CODEID, entry, index):
                blockscript = Pallet.codes[OBJECTINDEX][CODEID]
                blockscript = blockscript.replace('[*', '**')
                for roopIdx, i in enumerate(re.finditer('\[', blockscript)):
                    if roopIdx == index:
                        blockscript = blockscript[:i.end()] + entry.get() + blockscript[blockscript.find(']', i.end()):]
                blockscript = blockscript.replace('**', '[*')
                Pallet.codes[OBJECTINDEX][CODEID] = blockscript
                return
            INDEX = self.numberofEntry
            entry.bind('<KeyPress>', lambda event: synchroofChanges(event, CODEID, entry, INDEX))
            entry.bind('<KeyRelease>', lambda event: synchroofChanges(event, CODEID, entry, INDEX))
            self.numberofEntry += 1
        self.numberofCombobox = 0
        def bindCombobox(combobox, codeid):
            def synchroofChanges(codeid, combobox, index):
                combobox.selection_clear()
                blockscript = Pallet.codes[OBJECTINDEX][codeid]
                for roopi, i in enumerate(re.finditer('\{', blockscript)):
                    if roopi == index:
                        contents = blockscript[i.end():blockscript.find('\}', i.end())].split('|')
                        for roopi in range(len(contents)):
                            if contents[roopi][0] == '*':
                                contents[roopi] = contents[roopi][1:]
                            if contents[roopi] == combobox.get():
                                contents[roopi] = '*' + contents[roopi]
                        blockscript = blockscript[:i.end()] + '|'.join(contents) + blockscript[blockscript.find(')', i.end()):]
                Pallet.codes[OBJECTINDEX][codeid] = blockscript
                return
            INDEX = self.numberofCombobox
            combobox.bind('<<ComboboxSelected>>', lambda e: synchroofChanges(codeid, combobox, INDEX))
            self.numberofCombobox += 1
        def bindVariableSelector(variableSetter, codeid):
            def synchroofChanges(codeid, variableSetter):
                variableSetter.selection_clear()
                Pallet.codes[OBJECTINDEX][codeid] = Pallet.codes[OBJECTINDEX][codeid].split('>')[0] + '>' + variableSetter.get()
                return
            variableSetter.bind('<<ComboboxSelected>>', lambda e: synchroofChanges(codeid, variableSetter))

        if insertPosition == None:
            insertPosition = len(Pallet.codes[OBJECTINDEX])
        def bindWidget(widget):
            widget.bind('<ButtonPress-3>', lambda e: self.showCodeMenu(e, insertPosition))
            if widget.widgetName == 'entry':
                bindEntry(widget, CODEID)
            elif widget.widgetName == 'ttk::combobox':
                if blockscript[:15] == '+variableSetter':
                    bindVariableSelector(widget, CODEID)
                else:
                    bindCombobox(widget, CODEID)
        code = None
        if blockscript[0] == '#':
            '''comment block'''
            code = self.analyzeBlockScript(blockscript, parent=Pallet.codeFrame,
                changeable=True, nestDepth=nestDepth)
            code.winfo_children()[0].bind('<ButtonPress-3>', lambda e: self.showCodeMenu(e, insertPosition))
            def commentEntryChanged(event):
                Pallet.codes[OBJECTINDEX][CODEID] = '#' + event.widget.get()
                event.widget['width'] = usefull.getEastAsianWidthCount(event.widget.get())
                self.printCodes()
            code.winfo_children()[0].winfo_children()[0].bind('<KeyRelease>', commentEntryChanged)
        else:
            '''everything else'''
            code = self.analyzeBlockScript(blockscript, parent=Pallet.codeFrame,
                packHandler=bindWidget, changeable=True, nestDepth=nestDepth)
        '''elif len(Pallet.codes[Pallet.objects.indexofCurrentlySelectedObj]) > insertPosition:
            if '~' == Pallet.codes[Pallet.objects.indexofCurrentlySelectedObj][insertPosition][0]:
                code = self.analyzeBlockScript(blockscript, parent=Pallet.codeFrame,
                    packHandler=bindWidget, changeable=True, nestDepth=nestDepth)'''
        if DRAWONLY == False:
            Pallet.codes[OBJECTINDEX].insert(insertPosition, blockscript)
        if OBJECTINDEX == Pallet.objects.indexofCurrentlySelectedObj:
            Pallet.widgetsOnCodeZone.insert(insertPosition, code)
            if insertPosition == len(Pallet.widgetsOnCodeZone) - 1:
                self.packCode(insertPosition)
            else:
                self.isFirstStarterBlock = True
                for roopi, code in enumerate(Pallet.widgetsOnCodeZone):
                    code.pack_forget()
                for i in range(len(Pallet.widgetsOnCodeZone)):
                    self.packCode(i)
        return
    def removeCode(self, indexofCode):
        Pallet.codes[Pallet.objects.indexofCurrentlySelectedObj].pop(indexofCode)
        Pallet.widgetsOnCodeZone.pop(indexofCode).destroy()
        self.objFocusShiftHandler()
    '''---------------
    |  For code menu  |
    ----------------'''
    def initCodeMenu(self):
        Pallet.codeMenu = tk.Frame(Pallet.root, width=20, height=20, padx=2, pady=2,
            bg='#ddd')
        Pallet.root.bind_all('<ButtonPress-1>', lambda e: self.hideCodeMenu())
        deleter = tk.Label(
            Pallet.codeMenu, text='このブロックを削除する', font=('tkDefaeultFont', 12),
            padx=10, pady=2, fg='#000', bg=Pallet.codeMenu['bg'], cursor='hand2'
        )
        deleter.bind('<Enter>', lambda e: e.widget.config(background='#ccc'))
        deleter.bind('<Leave>', lambda e: e.widget.config(background=Pallet.codeMenu['bg']))
        deleter.bind('<ButtonPress-1>', lambda e: self.removeCode(Pallet.indexofCode2delete))
        deleter.pack()
    def showCodeMenu(self, event, indexofCode2delete):
        Pallet.indexofCode2delete = indexofCode2delete
        Pallet.codeMenu.place(x=event.x_root, y=event.y_root - 21)
    def hideCodeMenu(self):
        Pallet.codeMenu.place_forget()
    '''-------------
    |  Code packer  |
    --------------'''
    def packCode(self, codei):
        # 'codei' means 'code index'
        if self.isStarterBlock(Pallet.codes[Pallet.objects.indexofCurrentlySelectedObj][codei]):
            if self.isFirstStarterBlock and codei == 0:
                Pallet.widgetsOnCodeZone[codei].pack(anchor=tk.W)
                self.isFirstStarterBlock = False
            else:
                Pallet.widgetsOnCodeZone[codei].pack(anchor=tk.W, pady=(10, 0))
        else:
            Pallet.widgetsOnCodeZone[codei].pack(anchor=tk.W)
    '''---------------------------------------
    |  Functions to manipulate block scripts  |
    ----------------------------------------'''
    def analyzeBlockScript(self, blockscript, parent, packHandler=None, changeable=False, nestDepth=0, type='normal', dragging=False, recursion=False):
        '''
        blockscriptを解析しparentを親としたブロックウィジェットを返す
        '''
        def packWidget(widget, **kwargs):
            widget.pack(**kwargs)
            if packHandler != None:
                packHandler(widget)
        if blockscript[0] == '#':
            divFrame = tk.Frame(parent)
            commentBlock = tk.Frame(divFrame, background='#666')
            commentEntry = tk.Entry(commentBlock, border=0,
                insertwidth=1, insertbackground='#ccc',
                fg='#aaa', width=usefull.getEastAsianWidthCount(blockscript[1:]), justify=tk.LEFT,
                bg='#666', font=('tkDefaeultFont', 12))
            commentEntry.insert(0, blockscript[1:])
            packWidget(commentEntry, padx=self.blockPadx, pady=self.blockPady)
            packWidget(commentBlock)
            return divFrame
        boxFrame = None
        contentsoChangeableBlock = None
        block = {
            'isNest': None,
            'type': None,
            'background': None,
            'entryBackground': None,
            'widget': tk.Frame(parent), # 返す方はこっち
            'contents': None,           # 子ウィジェットを入れる方はこっち
            'nestHead': None
        }
        if '~' in blockscript:
            block['isNest'] = True
            block['type'] = 'nest'
            block['contents'] = tk.Frame(block['widget'], background=self.selectedTabColor)
            if blockscript == '~する':
                block['background'] = self.nestblockcolor2 if not nestDepth%2 else self.nestblockcolor
            else:
                block['background'] = self.nestblockcolor2 if nestDepth%2 else self.nestblockcolor
        elif self.isTerm(blockscript):
            block['type'] = 'term'
            block['isNest'] = False
            block['background'] = '#613c86'
            block['contents'] = tk.Frame(block['widget'], background=block['background'], padx=self.blockPadx, pady=self.blockPady)
            leftCap = tk.Canvas(block['widget'], width=10, height=self.blockHeight, highlightthickness=False,
                bg=self.nestblockcolor if isinstance(parent, tk.Canvas) else self.selectedTabColor)
            leftCap.pack(side=tk.LEFT)
            blockscript = blockscript[1:-1]
        elif self.isValue(blockscript):
            block['type'] = 'value'
            block['isNest'] = False
            if type == 'variable' or self.isVariable(blockscript):
                block['background'] = self.variableBlockColor
            else:
                block['background'] = '#717a30'
            if recursion:
                blockBorder = tk.Frame(block['widget'], background='#888', padx=1, pady=1)
                block['contents'] = tk.Frame(blockBorder, background=block['background'], padx=self.blockPadx, pady=self.blockPady)
                blockBorder.pack()
            else:
                block['contents'] = tk.Frame(block['widget'], background=block['background'], padx=self.blockPadx, pady=self.blockPady)
            blockscript = blockscript[1:-1]
        else:
            block['isNest'] = False
            if self.isControlVariables(blockscript):
                block['background'] = '#286900'
                block['entryBackground'] = self.variableBlockColor
                if blockscript[:15] == '+variableSetter':
                    variablesName = []
                    for variable in Pallet.variableBlocks:
                        if blockscript.split('>')[1] == variable[1:-1]:
                            variablesName.append('*' + variable[1:-1])
                        else:
                            variablesName.append(variable[1:-1])
                    blockscript = f'変数{{{"|".join(variablesName)}}}の値を[{mBS.getEntryfromBlockscript(blockscript, 0)}]にする'
            elif mBS.baseofBlock(blockscript) == '衣裳を{}にする':
                block['background'] = self.blockcolor
                costumeList = '{*'
                for i in [os.path.splitext(i)[0] for i in os.listdir(f'savedData/{Pallet.__share.title}/costume/{Pallet.objects.nameofObject[Pallet.objects.indexofCurrentlySelectedObj]}')]:
                    costumeList += i + '|'
                costumeList = costumeList[:-1] + '}'
                blockscript = f'衣裳を{costumeList}にする'
            else:
                block['background'] = self.blockcolor
            block['contents'] = tk.Frame(block['widget'], background=block['background'], padx=self.blockPadx, pady=self.blockPady)
        if parent == Pallet.codeFrame:
            for i in range(nestDepth):
                tk.Frame(block['widget'], background=self.nestblockcolor2 if i%2 else self.nestblockcolor, width=self.blockIndentWidth).pack(side=tk.LEFT, fill=tk.Y)
        if block['isNest']:
            block['nestHead'] = tk.Frame(block['contents'], background=block['background'],
                padx=self.blockPadx, pady=self.blockPady)
            block['nestHead'].pack(side=tk.TOP, anchor=tk.W)

        temp2analyze = ''
        previousString = None
        blockScriptType = '?'
        readingTerm = False
        readingValue = False
        numberofBrackets = 0
        if not recursion:
            self.numberofNormalEntry = 0
        for loopi, char in enumerate(blockscript):
            if char != '>' and readingTerm:
                temp2analyze += char
                previousString = char
                continue
            if readingValue:
                if char != ']' or numberofBrackets != 0:
                    if char == '[':
                        numberofBrackets += 1
                    elif char == ']':
                        numberofBrackets -= 1
                    temp2analyze += char
                    previousString = char
                    continue
            if char == '[' or char == '{' or char == '<':
                if temp2analyze != '':
                    packWidget(
                        tk.Label(
                            block['nestHead'] if block['isNest'] else block['contents'],
                            text=temp2analyze, font=('tkDefaeultFont', 12),
                            foreground='#ccc', background=block['background']
                        ), side=tk.LEFT
                    )
                    temp2analyze = ''
                    if char == '<':
                        readingTerm = True
            elif char == '~':
                if previousString == '~':
                    # if~~then
                    packWidget(
                        tk.Label(
                            block['nestHead'], text=temp2analyze, font=('tkDefaeultFont', 12),
                            foreground='#ccc', background=block['background']
                        ), side=tk.LEFT
                    )
                    contentsBorder = ttk.Frame(block['contents'], height=12, padding=(self.blockIndentWidth, 0, 0, 0), style='contentsBorder.TFrame')
                    packWidget(contentsBorder, anchor=tk.W)
                    contentsofChangeableBlock = tk.Frame(contentsBorder, background=self.selectedTabColor)
                    packWidget(contentsofChangeableBlock)
                    packWidget(
                        tk.Label(
                            contentsofChangeableBlock, text='いろいろ', font=('tkDefaeultFont', 12),
                            foreground='#ccc', background=self.blockcolor, padx=self.blockPadx, pady=self.blockPady
                        ), side=tk.TOP, anchor=tk.W
                    )
                    temp2analyze = ''
                elif loopi == len(blockscript) - 1:
                    # if~
                    packWidget(
                        tk.Label(
                            block['nestHead'], text=temp2analyze, font=('tkDefaeultFont', 12),
                            foreground='#ccc', background=block['background']
                        ), side=tk.LEFT, anchor=tk.W
                    )
                    temp2analyze = ''
                elif loopi == 0:
                    # ~then
                    blockScriptType = 'bottomofNest'
            elif char == '*':
                if previousString == '[':
                    readingValue = True
                temp2analyze += char
            elif char == ']':
                if readingValue:
                    packWidget(
                        self.analyzeBlockScript(f'[{temp2analyze[1:]}]', block['contents'], packHandler=packHandler,
                            dragging=dragging, recursion=True),
                        side=tk.LEFT)
                    readingValue = False
                    self.numberofNormalEntry += 1
                else:
                    entryFrame = tk.Frame(block['nestHead'] if block['isNest'] else block['contents'])
                    entry = tk.Entry(entryFrame, border=2, relief=tk.FLAT,
                        insertwidth=1, insertbackground='#ccc',
                        foreground='#ccc', width=4, justify=tk.RIGHT,
                        background='#444' if block['entryBackground'] == None else self.variableBlockColor,
                        font=('tkDefaeultFont', 12)
                    )
                    entry.insert(0, temp2analyze)
                    packWidget(entry, fill=tk.BOTH)
                    packWidget(entryFrame, side=tk.LEFT)
                    self.numberofNormalEntry += 1
                    if parent != Pallet.blockPallets['window'] and parent != Pallet.blockPallets['object'] and not dragging:
                        Pallet.entryOnCodeZoneInfo['frame'].append(entryFrame)
                        Pallet.entryOnCodeZoneInfo['numberInBlock'].append(self.numberofNormalEntry)
                temp2analyze = ''
            elif char == '}':
                dropDownList = temp2analyze.split('|')
                current = 0
                for roopi, item in enumerate(dropDownList):
                    if item[0] == '*':
                        dropDownList[dropDownList.index(item)] = item[1:]
                        current = roopi
                def comboboxSelected():
                    combobox.current(dropDownList.index(selecting.get()))
                selecting = tk.StringVar()
                combobox = ttk.Combobox(block['nestHead'] if block['isNest'] else block['contents'],
                    justify=tk.RIGHT, width=usefull.getEastAsianWidthCount(max(dropDownList, key=len)),
                    font=('tkDefaeultFont', 12), state='readonly', takefocus=False,
                    exportselection=False, values=dropDownList,
                    postcommand=comboboxSelected, textvariable=selecting,
                    style='nestblock.TCombobox' if block['isNest'] else 'block.TCombobox',
                )
                combobox.selection_clear()
                combobox.current(current)
                temp2analyze = ''
                packWidget(combobox, side=tk.LEFT)
            elif char == '>':
                fitTermHeight = self.blockHeight
                fitTerm = None
                if block['type'] == 'nest':
                    fitTerm = tk.Canvas(block['nestHead'], width=40, height=fitTermHeight,
                        bg=block['background'], highlightthickness=False)
                    fitTerm.create_polygon(10, 0, 0, fitTermHeight // 2, 10, fitTermHeight,
                        30, fitTermHeight, self.fitTermDefaultWidth, fitTermHeight // 2, 30, 0, fill='#275c36', tag='fitTermDent')
                else:
                    fitTerm = tk.Canvas(block['contents'], width=40, height=fitTermHeight,
                        bg=block['background'], highlightthickness=False)
                    fitTerm.create_polygon(10, 0, 0, fitTermHeight // 2, 10, fitTermHeight,
                        30, fitTermHeight, self.fitTermDefaultWidth, fitTermHeight // 2, 30, 0, fill='#463454', tag='fitTermDent')
                packWidget(fitTerm, side=tk.LEFT)
                if temp2analyze != '':
                    term = self.analyzeBlockScript(f'<{temp2analyze}>', fitTerm, packHandler=packHandler, recursion=True)
                    fitTerm.create_window(0, 0, anchor=tk.NW, window=term)
                    term.update()
                    def adapt2internalExtension(e):
                        fitTerm['width'] = term.winfo_width()
                    fitTerm['width'] = term.winfo_width()
                    fitTerm['height'] = term.winfo_height()
                    term.bind('<Configure>', adapt2internalExtension)
                if parent == Pallet.codeFrame:
                    Pallet.fitTermsOnCodeZone.append(fitTerm)
                temp2analyze = ''
                readingTerm = False
            else:
                temp2analyze += char
            previousString = char
            continue
        if temp2analyze != '':
            if blockScriptType == 'bottomofNest':
                packWidget(
                    tk.Label(
                        block['contents'], text=temp2analyze, font=('tkDefaeultFont', 12),
                        foreground='#ccc', background=block['background'], padx=self.blockPadx, pady=self.blockPady
                    ), side=tk.TOP, anchor=tk.W
                )
            else:
                if '~~' in blockscript:
                    packWidget(
                        tk.Label(
                            block['contents'], text=temp2analyze, font=('tkDefaeultFont', 12),
                            foreground='#ccc', background=block['background'], padx=self.blockPadx, pady=self.blockPady
                        ), side=tk.TOP, anchor=tk.W
                    )
                else:
                    packWidget(
                        tk.Label(block['contents'], text=temp2analyze, font=('tkDefaeultFont', 12),
                            foreground='#ccc', background=block['background'], justify='left'
                        ), side=tk.LEFT
                    )
        block['contents'].pack(side=tk.LEFT)
        if block['type'] == 'term':
            block['contents'].update_idletasks()
            leftCap.config(height=block['contents'].winfo_reqheight())
            leftCap.create_polygon(10, 0, 0, block['contents'].winfo_reqheight() // 2,
                10, block['contents'].winfo_reqheight(), fill=block['background'])
            rightCap = tk.Canvas(block['widget'], width=10, height=block['contents'].winfo_reqheight(), highlightthickness=False,
                bg=self.nestblockcolor if isinstance(parent, tk.Canvas) else self.selectedTabColor)
            rightCap.create_polygon(0, 0, 10, block['contents'].winfo_reqheight() // 2,
                0, block['contents'].winfo_reqheight(), fill=block['background'])
            rightCap.pack()
        return block['widget']
    def isStarterBlock(self, blockscript):
        for starterBlock in Pallet.starterBlocks:
            if self.sameBlock(blockscript, starterBlock):
                return True
        return False
    def isTerm(self, blockscript):
        return blockscript[0] == '<' and blockscript[-1] == '>'
    def isValue(self, blockscript):
        return blockscript[0] == '[' and blockscript[-1] == ']'
    def isVariable(self, blockscript):
        return blockscript in Pallet.variableBlocks
    def isControlVariables(self, blockscript):
        return blockscript[:15] == '+variableSetter'
    def sameBlock(self, blockscript1, blockscript2):
        #deviation = 0
        #for entry in entrys:
        #    blockscript = (blockscript[:entry['start'] + 1 - deviation] +
        #        blockscript[entry['end'] - deviation:])
        #    deviation += entry['end'] - entry['start'] - 1
        return self.formofBlock(blockscript1) == self.formofBlock(blockscript2)
    def formofBlock(self, blockscript):
        blockscript = re.sub('{[^}]*}', '{}', blockscript)
        '''blockscript = re.sub('\[[^*\]]*\]', '[]', blockscript)
        for entry in re.finditer('\[\*', blockscript):
            bs = blockscript[entry.start():]
            for loopi, char in enumerate(bs):
                if char == ']' and bs[loopi - 1] != '[':
                    blockscript = blockscript[:entry.start() + 1] + bs[loopi:]
                    break'''
        entrys = []
        readingEntry = {'start': None, 'end': None, 'appended': None}
        for loopi, char in enumerate(blockscript):
            if char == '[':
                readingEntry['start'] = loopi
                readingEntry['appended'] = False
            elif char == ']' and not readingEntry['appended']:
                readingEntry['end'] = loopi
                entrys.append({'start': readingEntry['start'], 'end': readingEntry['end']})
                readingEntry['appended'] = True
        deviation = 0
        for entry in entrys:
            blockscript = (blockscript[:entry['start'] + 1 - deviation] +
                blockscript[entry['end'] - deviation:])
            deviation += entry['end'] - entry['start'] - 1
        return blockscript
    def getEntryfromBlockscript_old(self, blockscript, index):
        for loopi, entry in enumerate(re.findall('\[[^\]]*\]', blockscript)):
            if loopi == index:
                return entry[1:-1]

        print('[ERROR] we cannot get entry from blockscript.')
        return None
    def getSuperEntryfromBlockscript(self, blockscript, index):
        for loopi, entry in enumerate(re.finditer('\[\*', blockscript)):
            if loopi == index:
                bs = blockscript[entry.start() + 2:]
                numberofBrackets = 0
                for i, char in enumerate(bs):
                    if char == '[':
                        numberofBrackets += 1
                    elif char == ']':
                        if numberofBrackets > 0:
                            numberofBrackets -= 1
                        else:
                            return bs[:i]

        print('[ERROR] we cannot get super entry from blockscript.')
        return None
    def getDropdownfromBlockscript(self, blockscript, index):
        for loopi, combobox in enumerate(re.findall('{[^}]*}', blockscript)):
            if loopi == index:
                contents = combobox[1:-1].split('|')
                for loopi in range(len(contents)):
                    if contents[loopi][0] == '*':
                        return contents[loopi][1:]
        print('[ERROR] we cannot get dropdown from blockscript.')
        return None
    def getTermsfromBlockscript(self, blockscript, index):
        for loopi, entry in enumerate(re.findall('<[^>]*>', blockscript)):
            if loopi == index:
                return entry

        print('[ERROR] we cannot get entry from blockscript.')
        return None
    def bind(self, sequence, func):
        for seq in Pallet.funcs:
            if sequence == seq:
                Pallet.funcs[seq].append(func)
                return True
        print(f'[ERROR] {sequence} is a sequence that does not exist')
        return False
    '''--------------
    |  property set  |
    ---------------'''
    @property
    def width(self):
        return Pallet.root.winfo_width() // 2
    @property
    def height(self):
        return Pallet.root.winfo_height() - 50
    @property
    def bodyHeight(self):
        return self.height - Pallet.__header.winfo_height() - 21
    @property
    def blockAreaWidth(self):
        return self.width / 2.5
    @property
    def selectedTabColor(self):
        return '#444'
    @property
    def blockHeight(self):
        '''ブロック1個分の高さをpxで返す'''
        return 22 + self.blockPady * 2
    @property
    def blockPadx(self):
        '''ブロックの水平方向の内部パディングをpxで返す'''
        return 7
    @property
    def blockPady(self):
        '''ブロックの垂直方向の内部パディングをpxで返す'''
        return 4
    @property
    def blockIndentWidth(self):
        return 8
    @property
    def blockcolor(self):
        return '#343434'
    @property
    def nestblockcolor(self):
        return '#052d11'
    @property
    def nestblockcolor2(self):
        return '#00450b'
    @property
    def variableBlockColor(self):
        return '#478000'
    @property
    def fitTermDefaultWidth(self):
        return 40
    @property
    def scrollbarWidth(self):
        return 16
    '''------------
    |  debug tool  |
    -------------'''
    def printBlocks(self):
        print(
            '---' '\n'
            'List of currently available blocks' '\n')
        for blockScript in Pallet.windowOnlyBlocks:
            print('window only blocks> ' + blockScript)
        for blockScript in Pallet.objectOnlyBlocks:
            print('object only blocks) ' + blockScript)
        for blockScript in Pallet.generalBlocks:
            print('general blocks    : ' + blockScript)
        for blockScript in Pallet.blocks2controlVariables:
            print('variable blocks   ] ' + blockScript)
        print('---')
        return
    def printCodes(self):
        print('---Codes that each object has---')
        for roopi, codes in enumerate(Pallet.codes):
            if roopi == 0:
                print(f'object {roopi} ( = window)')
            else:
                print(f'object {roopi}')
            for code in codes:
                print(f'\t{code}')
        print('--------------------------------')
        return
    def printWidgetTree(self):
        print(Fore.GREEN + Style.BRIGHT + '---widget tree on pallet---' + Style.RESET_ALL)
        self.__printWidgetTree(Pallet.topFrame)
        print(Fore.GREEN + Style.BRIGHT + '---------------------------' + Style.RESET_ALL)
        return
    def __printWidgetTree(self, widget):
        if widget == Pallet.blockPallets['window']:
            print(Fore.CYAN + Style.BRIGHT + '< window block pallet >' + Style.RESET_ALL)
        elif widget == Pallet.blockPallets['object']:
            print(Fore.CYAN + Style.BRIGHT + '< object block pallet >' + Style.RESET_ALL)
        print(widget)
        for child in widget.winfo_children():
            self.__printWidgetTree(child)
