'''昔キャンバスでパレットを実装してみたときのコード。念のためとっておく。'''
"""
class Canvas:
    def __init__(self):
        self.__tkcanvas = tk.Canvas(
            root,
            width=self.width, height=self.height,
            highlightthickness=False,
            background = '#555'
        )
        self.__tkcanvas.create_rectangle((0, 0), (self.blockAreaWidth, self.height), fill='#444', width=0)
        self.__tkcanvas.grid(row=1, column=0)

        self.__numberofBlock = 0
        self.__numberofCode = 0
        self.__listofLabelsforBlocks = []

        self.addcode('プログラムが始まったら')
    @property
    def width(self):
        return root.winfo_width() / 2
    @property
    def height(self):
        return root.winfo_height() - 50
    @property
    def blockAreaWidth(self):
        return self.width / 3;
    @property
    def blockHeight(self):
        '''ブロック1個分の高さをpxで返す'''
        return 32
    @property
    def blockPady(self):
        '''ブロックの垂直方向の内部パディングをpxで返す'''
        return 10
    @property
    def blockcolor(self):
        return '#343434';
    def addblock(self, label):
        dragarea = self.__tkcanvas.create_rectangle(
            (10, 10 + self.__numberofBlock * (self.blockHeight + 10)),
            (10 + 10 + font.Font(self.__tkcanvas,font=("tkDefaeultFont", 12)).measure(label) + 10,
                10 + self.__numberofBlock * (self.blockHeight + 10) + self.blockHeight),
            fill = self.blockcolor,
            width = 1,
            outline = '#444',
            tag=f"block{self.__numberofBlock + 1}")
        self.__tkcanvas.tag_bind(dragarea, "<ButtonPress-1>", self.__blockdragstart)
        self.__tkcanvas.tag_bind(dragarea, "<Button1-Motion>", self.__blockdragging)
        self.__tkcanvas.tag_bind(dragarea, "<ButtonRelease>", self.__blockdragfinish)

        self.__tkcanvas.create_text(
            (10 + 10, 10 + self.blockPady + self.__numberofBlock * 42),
            anchor="nw",
            text=label,
            fill="#aaa",
            font='tkDefaeultFont 12',
            tag=f"block{self.__numberofBlock + 1}label"
        )
        self.__tkcanvas.tag_bind(f"block{self.__numberofBlock + 1}label", "<ButtonPress-1>", self.__blockdragstart)
        self.__tkcanvas.tag_bind(f"block{self.__numberofBlock + 1}label", "<Button1-Motion>", self.__blockdragging)
        self.__tkcanvas.tag_bind(f"block{self.__numberofBlock + 1}label", "<ButtonRelease>", self.__blockdragfinish)
        self.__listofLabelsforBlocks.append(label)
        self.__numberofBlock += 1
        return
    def __blockdragstart(self, event):
        self.x = event.x
        self.y = event.y
        #self.draggingblock = self.__tkcanvas.find_closest(event.x, event.y)
        #print(self.__tkcanvas.gettags("current"))
        #self.__tagofbraggingblock = self.__tkcanvas.gettags("current")
        if re.match(r'block..*label', self.__tkcanvas.gettags("current")[0]):
            self.__tagofbraggingblock = self.__tkcanvas.gettags("current")[0].rstrip('label')
        elif re.match(r'block..*', self.__tkcanvas.gettags("current")[0]):
            self.__tagofbraggingblock = self.__tkcanvas.gettags("current")[0]
        else:
            print('[ERROR] unkown tag name at __blockdragstart() in Canvas class')
        self.__originalPositionOfBlock = {
            'x': self.__tkcanvas.coords(self.__tagofbraggingblock)[0],
            'y': self.__tkcanvas.coords(self.__tagofbraggingblock)[1]
        }
        #print([self.__tkcanvas.itemcget(obj, 'tags') for obj in self.__tkcanvas.find_overlapping(self.x,self.y,self.x,self.y)])
        #self.__tkcanvas.move("block1", 100, 100)
        #self.__tkcanvas.move("block1label", 100, 100)
        return
    def __blockdragging(self, event):
        if event.x < 0 or event.y < 0 or event.x > self.width or event.y > self.height:
            return
        self.__tkcanvas.move(self.__tagofbraggingblock, event.x - self.x, event.y - self.y)
        self.__tkcanvas.move(self.__tagofbraggingblock + "label", event.x - self.x, event.y - self.y)
        self.__tkcanvas.tag_raise(self.__tagofbraggingblock)
        self.__tkcanvas.tag_raise(self.__tagofbraggingblock + "label")
        self.x = event.x
        self.y = event.y
        return
    def __blockdragfinish(self, event):
        currentBlockPosition = {
            'x': self.__tkcanvas.coords(self.__tagofbraggingblock)[0],
            'y': self.__tkcanvas.coords(self.__tagofbraggingblock)[1]
        }
        self.__tkcanvas.move(self.__tagofbraggingblock,
            self.__originalPositionOfBlock['x'] - currentBlockPosition['x'],
            self.__originalPositionOfBlock['y'] - currentBlockPosition['y'])
        self.__tkcanvas.move(self.__tagofbraggingblock + "label",
            self.__originalPositionOfBlock['x'] - currentBlockPosition['x'],
            self.__originalPositionOfBlock['y'] - currentBlockPosition['y'])
        #print(self.__tkcanvas.coords(self.__tagofbraggingblock))
        #self.__tkcanvas.delete(self.__tagofbraggingblock)
        #self.__tkcanvas.delete(self.__tagofbraggingblock + "label")
        self.addcode(self.__listofLabelsforBlocks[int(self.__tagofbraggingblock.lstrip('block')) - 1])
        #print((self.__tagofbraggingblock+"label").cget("text"))
        return
    def addcode(self, name):
        dragarea = self.__tkcanvas.create_rectangle(
            (self.blockAreaWidth + 10, 10 + self.__numberofCode * self.blockHeight),
            (self.blockAreaWidth + 10 + 10 + font.Font(self.__tkcanvas,font=("tkDefaeultFont", 12)).measure(name) + 10,
                10 + self.__numberofCode * self.blockHeight + self.blockHeight),
            fill = self.blockcolor,
            width = 1,
            outline = '#444',
            tag=f"code{self.__numberofCode + 1}")
        self.__tkcanvas.create_text(
            (self.blockAreaWidth + 10 + 10, 10 + self.blockPady + self.__numberofCode * self.blockHeight),
            anchor="nw",
            text=name,
            fill="#aaa",
            font='tkDefaeultFont 12',
            tag=f"code{self.__numberofCode + 1}label"
        )
        self.__numberofCode += 1
        return"""
