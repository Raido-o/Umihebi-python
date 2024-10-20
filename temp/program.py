import random
import tkinter as tk
root = tk.Tk()
root.title('ロケット一代')
canvas = tk.Canvas(root, highlightthickness=False)
canvas.pack(fill='both', expand=True)
photoImages = []
photoImages.append(tk.PhotoImage(file=r'savedData/ロケット一代/costume/ロケット\rocket.png'))
photoImages.append(tk.PhotoImage(file=r'savedData/ロケット一代/costume/小惑星/asteroid.png'))
photoImages.append(tk.PhotoImage(file=r'savedData/ロケット一代/costume/小惑星\asteroid.png'))
keyPressFuncs = []
def keyPressFunc(event):
	for func in keyPressFuncs:
		func(event)
root.bind('<KeyRelease>', keyPressFunc)
programVariables = {}
programVariables['ボールのY軸にすすむ向き'] = None
programVariables['ボールのX軸にすすむ向き'] = None
programVariables['プレイヤーのX座標'] = None
'''------------------------------------
|  Setup complete. Let's get started!  |
-------------------------------------'''
# プログラムが始まったら
root.geometry('600x800+0+0')
canvas['background']='#000'
actor1 = canvas.create_image(100, 100, image=photoImages[0])
# プログラムが始まったら
canvas.move(actor1, 200 - canvas.bbox(actor1)[0], 740 - canvas.bbox(actor1)[1])
programVariables['プレイヤーのX座標']=200
canvas.itemconfigure(actor1, image=photoImages[1])
def keyPress0(event):
	if event.keysym == 'Right':
		canvas.move(actor1, 50, 0)
		programVariables['プレイヤーのX座標']=canvas.bbox(actor1)[0]
keyPressFuncs.append(keyPress0)
def keyPress1(event):
	if event.keysym == 'Left':
		canvas.move(actor1, -50, 0)
		programVariables['プレイヤーのX座標']=canvas.bbox(actor1)[0]
keyPressFuncs.append(keyPress1)
actor2 = canvas.create_image(100, 100, image=photoImages[2])
cloneActor2 = []
numberofCloneActors2 = 0
def clone():
	global numberofCloneActors2
	indexofCloneActor2 = numberofCloneActors2 - 1
	numberofCloneActors2 += 1
	cloneActor2.append(canvas.create_image(100, 100, image=photoImages[2]))
	canvas.move(cloneActor2[indexofCloneActor2], random.random()*530 - canvas.bbox(cloneActor2[indexofCloneActor2])[0], 0 - canvas.bbox(cloneActor2[indexofCloneActor2])[1])
	def loop1():
		canvas.move(cloneActor2[indexofCloneActor2], 0, 5)
		if canvas.bbox(cloneActor2[indexofCloneActor2])[1] >= 800:
			canvas.move(cloneActor2[indexofCloneActor2], random.random()*530 - canvas.bbox(cloneActor2[indexofCloneActor2])[0], 0 - canvas.bbox(cloneActor2[indexofCloneActor2])[1])
			# ~する
		# ~する
		root.after(40, loop1)
	root.after(40, loop1)
# 幕が上がったとき
canvas.itemconfigure(actor2, state='hidden')
for i in range(3):
	clone()
	# ~する
root.mainloop()