import glob
import threading
import subprocess

import Pallet.manipulationBS as mBS
import usefull
import Share

share = Share.Share()

blockprogram = ''
starterBlock = ''
finishCodes = {'inside': [], 'outside': []}
numberofTab = 0
isInCloneChunk = None
tkimgSetup = 'photoImages = []'
cachedTkimg = []
#runningProgram = False
def exePy():
    global programRunning
    global programProcess
    #programProcess = subprocess.Popen(['python', 'temp/program.py'], stdout=PIPE, stderr=PIPE)
    programRunning = True
    programProcess = subprocess.Popen(['python','temp/program.py'], shell=True)
    programProcess.wait()
    programRunning = False
def addCodeSnippet(codeSnippet):
    global blockprogram
    global starterBlock
    global numberofTab
    if starterBlock == 'keyPress' or starterBlock == 'while':
        for i in range(numberofTab):
            blockprogram += '\t'
        blockprogram += codeSnippet
    else:
        blockprogram += codeSnippet
    blockprogram += '\n'
    return True
programVariables = []
thisObjectIndex = None
def superEntry2code(superEntry):
    global programVariables
    global thisObjectIndex
    if superEntry[0] != '*':
        return superEntry
    if superEntry[1:] in programVariables:
        return f"programVariables['{superEntry[1:]}']"
    elif superEntry == '*この物体のX座標':
        return f"canvas.bbox(actor{thisObjectIndex})[0]"
    elif superEntry == '*この物体のY座標':
        return f"canvas.bbox({getActorCurrentlyEligible()})[1]"
    elif superEntry == '*0から1までの乱数':
        return f'random.random()'
    elif mBS.baseofBlock(superEntry) == '*[] + []':
        return f'{superEntry2code(mBS.getEntryfromBlockscript(superEntry, 0))} + {mBS.getEntryfromBlockscript(superEntry, 1)}'
    else:
        usefull.printWarning(f'Could not convert "{superEntry}" to code.\n')
        return ''
def translateEntryfromBlockscript(blockscript, index):
    entry = mBS.getEntryfromBlockscript(blockscript, index)
    if mBS.baseofBlock(entry) == '*[] x []':
        return f"{translateEntryfromBlockscript(entry, 0)}*{translateEntryfromBlockscript(entry, 1)}"
    else:
        return superEntry2code(entry) if entry[0] == '*' else entry
def getActorCurrentlyEligible():
    global thisObjectIndex
    return f'cloneActor{thisObjectIndex}[indexofCloneActor{thisObjectIndex}]' if isInCloneChunk else f'actor{thisObjectIndex}'
def tkPhotoImage(tkimgPath):
    global cachedTkimg
    global tkimgSetup
    if not tkimgPath in cachedTkimg:
        tkimgSetup += f"photoImages.append(tk.PhotoImage(file=r'{tkimgPath}'))\n"
        cachedTkimg.append(tkimgPath)
    return f'photoImages[{cachedTkimg.index(tkimgPath)}]'
def unveiling(pallet, objects, title):
    global blockprogram
    global starterBlock
    global finishCodes
    global numberofTab
    global programRunning
    global programProcess
    global programVariables
    '''現在作業しているオブジェクトのインデックス'''
    global thisObjectIndex
    '''現在のチャンクが「分身の動き」か'''
    global isInCloneChunk
    global tkimgSetup
    global cachedTkimg
    exePyPath = 'temp/program.py'
    #if platform.system() == 'Windows':
    #    exePyPath = exePyPath.replace('/', '\\')
    sourcefile = open(exePyPath, 'w', encoding='utf-8')

    blockprogram = (
        'keyPressFuncs = []\n'
        'def keyPressFunc(event):\n'
        '\tfor func in keyPressFuncs:\n'
        '\t\tfunc(event)\n'
        "root.bind('<KeyRelease>', keyPressFunc)\n"
        'programVariables = {}\n')
    numberofKeyPressFuncs = 0
    programVariables = []
    for variable in pallet.variableBlocks:
        programVariables.append(variable[1:-1])
    for variable in programVariables:
        addCodeSnippet(f"programVariables['{variable}'] = None")
    thisObjectIndex = 0
    numberofWhileLoop = 1
    blockprogram += (
        "'''------------------------------------\n"
        "|  Setup complete. Let's get started!  |\n"
        "-------------------------------------'''\n"
    )
    tkimgSetup = 'photoImages = []\n'
    cachedTkimg = []
    for loopi, code in enumerate(pallet.codes):
        chunks = []
        temp2splitIntoChunk = []
        for loopIdx, blockscript in enumerate(code):
            if pallet.isStarterBlock(blockscript):
                chunks.append(temp2splitIntoChunk)
                temp2splitIntoChunk = [blockscript]
            else:
                temp2splitIntoChunk.append(blockscript)
                if loopIdx == len(code) - 1:
                    chunks.append(temp2splitIntoChunk)
        for loopIdx, chunk in enumerate(chunks):
            if chunk[0] == '分身の動き':
                chunks.insert(0, chunks.pop(loopIdx))
        chunkHead = chunk[0]
        if loopi != 0:
            blockprogram += (
                f'actor{loopi} = canvas.create_image(100, 100, image='
                    f"{tkPhotoImage(glob.glob(f'savedData/{share.title}/costume/{objects.nameofObject[loopi]}/*')[objects.actors['indexofDefaultCostume'][loopi]])})\n"
            )
            if chunkHead == '分身の動き':
                blockprogram += (
                    f'cloneActor{loopi} = []\n'
                    f'numberofCloneActors{loopi} = 0\n'
                )
            thisObjectIndex += 1
        variables = {}
        ifDepth = 0
        for chunk in chunks:
            if chunk[0] == '分身の動き':
                isInCloneChunk = True
            else:
                isInCloneChunk = False
            for blockscript in chunk:
                #print(mBS.baseofBlock(blockscript))
                if '[*]' in pallet.formofBlock(blockscript):
                    superEntry = pallet.getSuperEntryfromBlockscript(blockscript, 0)
                    if pallet.formofBlock(superEntry) == '[] x []':
                        blockscript = blockscript.replace('*' + superEntry,
                            str(
                                int(pallet.getEntryfromBlockscript_old(superEntry, 0)) *
                                int(pallet.getEntryfromBlockscript_old(superEntry, 1))
                            )
                        )
                if mBS.baseofBlock(blockscript) == '{}キーが離されたとき':
                    numberofTab = 0
                    addCodeSnippet(f"def keyPress{numberofKeyPressFuncs}(event):")
                    starterBlock = 'keyPress'
                    finishCodes['outside'].append(f'keyPressFuncs.append(keyPress{numberofKeyPressFuncs})')

                    numberofTab = 1
                    typeofChar = None
                    if pallet.getDropdownfromBlockscript(blockscript, 0) == '上':
                        typeofChar = 'Up'
                    elif pallet.getDropdownfromBlockscript(blockscript, 0) == '下':
                        typeofChar = 'Down'
                    elif pallet.getDropdownfromBlockscript(blockscript, 0) == '右':
                        typeofChar = 'Right'
                    elif pallet.getDropdownfromBlockscript(blockscript, 0) == '左':
                        typeofChar = 'Left'
                    elif pallet.getDropdownfromBlockscript(blockscript, 0) == 'w':
                        typeofChar = 'w'
                    elif pallet.getDropdownfromBlockscript(blockscript, 0) == 's':
                        typeofChar = 's'
                    if typeofChar == None:
                        print(f"[ERROR] this program didn't support this type of char: {pallet.getDropdownfromBlockscript(blockscript, 0)}")
                    addCodeSnippet(f"if event.keysym == '{typeofChar}':")
                    numberofTab = 2
                    numberofKeyPressFuncs += 1
                elif blockscript == 'ずっと~':
                    addCodeSnippet(f'def loop{numberofWhileLoop}():')
                    numberofTab += 1
                    ifDepth += 1
                    starterBlock = 'while'
                    finishCodes['inside'].append(f'root.after(40, loop{numberofWhileLoop})')
                    finishCodes['outside'].append(f'root.after(40, loop{numberofWhileLoop})')
                    numberofWhileLoop += 1
                elif blockscript == '幕が上がったとき':
                    numberofTab = 0
                    addCodeSnippet('# 幕が上がったとき')
                elif mBS.baseofBlock(blockscript) == '衣裳を{}にする':
                    #print(pallet.getDropdownfromBlockscript(blockscript, 0))
                    addCodeSnippet(f"canvas.itemconfigure({getActorCurrentlyEligible()}, image={tkPhotoImage(r'savedData/ロケット一代/costume/小惑星/asteroid.png')})")
                elif mBS.baseofBlock(blockscript) == '[]回~':
                    addCodeSnippet(f'for i in range({translateEntryfromBlockscript(blockscript, 0)}):')
                    numberofTab += 1
                elif blockscript == '自分自身の分身を作る':
                    addCodeSnippet(f'clone()')
                elif blockscript == '分身の動き':
                    addCodeSnippet(f'def clone():')
                    numberofTab += 1
                    addCodeSnippet(f'global numberofCloneActors{loopi}')
                    addCodeSnippet(f'indexofCloneActor{loopi} = numberofCloneActors{loopi} - 1')
                    addCodeSnippet(f'numberofCloneActors{loopi} += 1')
                    addCodeSnippet(f"cloneActor{loopi}.append(canvas.create_image(100, 100, image={tkPhotoImage(glob.glob(f'savedData/{share.title}/costume/{objects.nameofObject[loopi]}/*')[0])}))")
                elif mBS.baseofBlock(blockscript) == 'ウィンドウの幅を[]pxに、高さを[]pxにする':
                    addCodeSnippet(f"root.geometry('{translateEntryfromBlockscript(blockscript, 0)}x{translateEntryfromBlockscript(blockscript, 1)}+0+0')")
                elif mBS.baseofBlock(blockscript) == 'ウィンドウの背景色を[]にする':
                    addCodeSnippet(f"canvas['background']='{pallet.getEntryfromBlockscript_old(blockscript, 0)}'")
                elif mBS.baseofBlock(blockscript) == '上に[]px動く':
                    movePx = mBS.getEntryfromBlockscript(blockscript, 0)
                    if movePx[0] == '*':
                        addCodeSnippet(f'canvas.move(actor{loopi}, 0, -{superEntry2code(movePx)})')
                    else:
                        addCodeSnippet(f'canvas.move(actor{loopi}, 0, -{movePx})')
                elif mBS.baseofBlock(blockscript) == '下に[]px動く':
                    addCodeSnippet(f'canvas.move({getActorCurrentlyEligible()}, 0, {translateEntryfromBlockscript(blockscript, 0)})')
                elif mBS.baseofBlock(blockscript) == '右に[]px動く':
                    movePx = mBS.getEntryfromBlockscript(blockscript, 0)
                    if movePx[0] == '*':
                        addCodeSnippet(f'canvas.move(actor{loopi}, {superEntry2code(movePx)}, 0)')
                    else:
                        addCodeSnippet(f'canvas.move(actor{loopi}, {movePx}, 0)')
                elif mBS.baseofBlock(blockscript) == '左に[]px動く':
                    addCodeSnippet(f'canvas.move(actor{loopi}, -{pallet.getEntryfromBlockscript_old(blockscript, 0)}, 0)')
                elif mBS.baseofBlock(blockscript) == 'x座標を[]に、y座標を[]にする':
                    addCodeSnippet(f'''canvas.move({getActorCurrentlyEligible()}, {translateEntryfromBlockscript(blockscript, 0)
                        } - canvas.bbox({getActorCurrentlyEligible()})[0], {
                        translateEntryfromBlockscript(blockscript, 1)} - canvas.bbox({getActorCurrentlyEligible()})[1])''')
                elif blockscript == '隠れる':
                    addCodeSnippet(f"canvas.itemconfigure(actor{loopi}, state='hidden')")
                elif mBS.baseofBlock(blockscript) == 'もし<[] = []>なら~':
                    terms = pallet.getTermsfromBlockscript(blockscript, 0)
                    if pallet.getEntryfromBlockscript_old(terms, 0)[0] == '*':
                        addCodeSnippet(f'if {superEntry2code(pallet.getEntryfromBlockscript_old(terms, 0))} == {pallet.getEntryfromBlockscript_old(terms, 1)}:')
                    else:
                        if mBS.baseofBlock(terms) == '<[] = []>':
                            addCodeSnippet(f'if {pallet.getEntryfromBlockscript_old(terms, 0)} == {pallet.getEntryfromBlockscript_old(terms, 1)}:')
                    ifDepth += 1
                    numberofTab += 1
                elif mBS.baseofBlock(blockscript) == 'もし<[]が[]以上>なら~':
                    terms = pallet.getTermsfromBlockscript(blockscript, 0)
                    if pallet.getEntryfromBlockscript_old(terms, 0)[0] == '*':
                        addCodeSnippet(f'if {superEntry2code(mBS.getEntryfromBlockscript(terms, 0))} >= ' +
                            f'{superEntry2code(mBS.getEntryfromBlockscript(terms, 1))}:')
                    else:
                        if mBS.baseofBlock(terms) == '<[]が[]以上>':
                            addCodeSnippet(f'if {pallet.getEntryfromBlockscript_old(terms, 0)} >= {pallet.getEntryfromBlockscript_old(terms, 1)}:')
                    ifDepth += 1
                    numberofTab += 1
                    finishCodes['inside'].append('')
                    finishCodes['outside'].append('')
                elif blockscript == '~する':
                    addCodeSnippet('# ~する')
                    if finishCodes['inside'] != []:
                        if finishCodes['inside'][-1] != '':
                            addCodeSnippet(finishCodes['inside'][-1])
                        finishCodes['inside'].pop(-1)
                    if ifDepth > 0:
                        numberofTab -= 1
                        ifDepth -= 1
                    if finishCodes['outside'] != []:
                        if finishCodes['outside'][-1] != '':
                            addCodeSnippet(finishCodes['outside'][-1])
                        finishCodes['outside'].pop(-1)
                elif blockscript[:15] == '+variableSetter':
                    addCodeSnippet(f"""programVariables['{blockscript.split(">")[1]}']=""" + superEntry2code(pallet.getEntryfromBlockscript_old(blockscript, 0)))
                else:
                    blockprogram += f'# {blockscript}\n'
            if finishCodes['inside'] != []:
                addCodeSnippet(finishCodes['inside'][-1])
                finishCodes['inside'] = []
            if finishCodes['outside'] != []:
                blockprogram += finishCodes['outside'][-1] + '\n'
                finishCodes['outside'] = []
            numberofTab = 0

    sourcefile.write(
        'import random\n'
        'import tkinter as tk\n'
        'root = tk.Tk()\n'
        f"root.title('{title.get()}')\n"
        'canvas = tk.Canvas(root, highlightthickness=False)\n'
        "canvas.pack(fill='both', expand=True)\n"
        + tkimgSetup
        + blockprogram
        + 'root.mainloop()')
    sourcefile.close()
    # run!
    #subprocess.call(exePyPath, shell=True)
    #programProcess = subprocess.Popen(['python', 'temp/program.py'], stdout=PIPE, stderr=PIPE)
    threading.Thread(target=exePy).start()
    #time.sleep(1)
    #programRunning = True
    #programProcess = subprocess.Popen(['python', 'temp/program.py'], shell=False)
    #programRunning = False
    #time.sleep(1)
    #print('killing...')
    return
