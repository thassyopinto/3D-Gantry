"3D Gantry System v1.0"
"by Thassyo Pinto thassyo@ieee.org"

# Import Standard Libraries
import csv
import math
import time

# Import External Libraries
import tkinter
import vpython as vs

# Application Specs
APP_NAME = "3D Gantry System v1.0"
UPDATE_TIME = 10 # ms
WIN_X = 800
WIN_Y = 600

# Gantry Specs
GAN_W = 63 # cm
GAN_D = 57 # cm
GAN_H = 66 # cm
GAN_T = 4 # cm
BAR_W = 4 # cm
BAR_D = 4 # cm
BAR_H = GAN_H - GAN_T # cm
TOP_W = BAR_W # cm
TOP_D = GAN_D - (BAR_D*2) # cm
TOP_H = 10 # cm
XAXIS_W = TOP_H # cm
XAXIS_D = 5 # cm
XAXIS_H = 15 # cm
YAXIS_W = GAN_W - (BAR_W*2) # cm
YAXIS_D = 5 # cm
YAXIS_H = TOP_H # cm
ZAXIS_L = 25
ZAXIS_R = 2
AAXIS_L = 10
AAXIS_R = 1

# Main Application
class Application(tkinter.Tk):
    def __init__(self):
        tkinter.Tk.__init__(self)
        self.title(APP_NAME)

        self.systemTime = 0
        self.moveState = False
        self.gantryAxis = []
        self.gantryPosition = []
        self.gantryTarget = []
        self.currentPosition = []

        self.x_yoffset = XAXIS_D/2 + ZAXIS_R
        self.y_yoffset = YAXIS_D/2 + XAXIS_D + ZAXIS_R
        self.x_zoffset = GAN_H - (GAN_T/2 + TOP_H/2)
        self.y_zoffset = self.x_zoffset
        self.z_zoffset = GAN_H - (GAN_T/2 + TOP_H/2) + XAXIS_H/2
        self.a_zoffset = self.z_zoffset - ZAXIS_L +AAXIS_L/2

        self.sizeXAxis = GAN_W - ((BAR_D*2) + XAXIS_W)
        self.sizeYAxis = GAN_D - ((BAR_D*2) + XAXIS_D + YAXIS_D + ZAXIS_R)
        self.sizeZAxis = XAXIS_H/2
        self.sizeAAxis = AAXIS_L/2

        self.minXAxis = -self.sizeXAxis/2
        self.minYAxis = -self.sizeYAxis/2
        self.minZAxis = 0
        self.minAAxis = 0
        self.maxXAxis = self.sizeXAxis/2
        self.maxYAxis = self.sizeYAxis/2
        self.maxZAxis = self.sizeZAxis
        self.maxAAxis = self.sizeAAxis

        self.minAxis = [self.minXAxis,self.minYAxis,self.minZAxis,self.minAAxis]
        self.maxAxis = [self.maxXAxis,self.maxYAxis,self.maxZAxis,self.maxAAxis]
        self.axisName = ["X-Axis","Y-Axis","Z-Axis","A-Axis"]
        print(self.minAxis)
        print(self.maxAxis)

        self.createMenu()
        self.createCanvas()
        self.createScene()
        self.updateApp()

    def createMenu(self):
        self.menuFrame = tkinter.Frame(self, bg='grey')
        self.menuFrame.pack(fill='x')
        self.buttonRun = tkinter.Button(self.menuFrame, text='Home', command=self.homeGantry)
        self.buttonRun.pack(side='left')
        self.buttonRun = tkinter.Button(self.menuFrame, text='Move', command=self.moveGantry)
        self.buttonRun.pack(side='left')
        self.buttonRun = tkinter.Button(self.menuFrame, text='Export')
        self.buttonRun.pack(side='left')
        self.buttonQuit = tkinter.Button(self.menuFrame, text='Quit', command=self.quitApp)
        self.buttonQuit.pack(side='right')

    def createCanvas(self):
        # self.canvas = tkinter.Canvas(self, width=WIN_X, height=WIN_Y)
        # self.canvas.pack()
        self.gantryFrame = []
        self.gantryLabelAxis = []
        self.gantryLabelUnits = []
        self.gantryEntry = []
        self.gantrySlider = []
        self.sliderState = []

        self.modeState = tkinter.StringVar()
        self.modeFrame = tkinter.Frame(self)
        self.modeFrame.pack(fill='x')
        self.autoMode = tkinter.Radiobutton(self.modeFrame, text=" Autonomous Mode ", variable=self.modeState, value='A')
        self.autoMode.pack(side='left')
        self.manualMode = tkinter.Radiobutton(self.modeFrame, text=" Manual Mode ", variable=self.modeState, value='M')
        self.manualMode.pack(side='right')
        self.modeState.set('M')

        for i in range(len(self.axisName)):
            self.gantryFrame.append(tkinter.Frame(self))
            self.gantryFrame[i].pack(fill='x')
            self.gantryLabelAxis.append(tkinter.Label(self.gantryFrame[i], text=self.axisName[i]))
            self.gantryLabelAxis[i].pack(side='left')
            self.gantryEntry.append(tkinter.Entry(self.gantryFrame[i], bd=5))
            self.gantryEntry[i].insert(0, '0')
            self.gantryEntry[i].pack(side='left')
            self.gantryLabelUnits.append(tkinter.Label(self.gantryFrame[i], text="cm"))
            self.gantryLabelUnits[i].pack(side='left')
            self.sliderState.append(tkinter.IntVar())
            self.gantrySlider.append(tkinter.Scale(self.gantryFrame[i], from_=self.minAxis[i], to=self.maxAxis[i], variable=self.sliderState[i], orient='horizontal'))
            self.gantrySlider[i].pack(side='right')
            self.gantryPosition.append(float(self.gantrySlider[i].get()))
            self.gantryTarget.append(float(self.gantrySlider[i].get()))
            self.currentPosition.append(float(self.gantrySlider[i].get()))

        self.speedEntryState = tkinter.StringVar(value="1.0")
        self.speedFrame = tkinter.Frame(self)
        self.speedFrame.pack(fill='x')
        self.speedLabel = tkinter.Label(self.speedFrame, text="Motor Speed")
        self.speedLabel.pack(side='left')
        self.speedEntry = tkinter.Entry(self.speedFrame, textvariable=self.speedEntryState, bd=5)
        self.speedEntry.pack(side='left')
        self.speedLabelUnits = tkinter.Label(self.speedFrame, text="cm/s")
        self.speedLabelUnits.pack(side='left')

    def createScene(self):
        vs.scene.title = APP_NAME
        vs.scene.fullscreen = True
        vs.scene.width = WIN_X
        vs.scene.height = WIN_Y
        vs.scene.camera.pos = vs.vector(0, 60, -60)
        vs.scene.camera.rotate(angle=math.radians(180), axis=vs.vector(0, 1, 0))
        vs.scene.camera.rotate(angle=math.radians(30), axis=vs.vector(1, 0, 0))
        self.createSupport()
        self.createGantry()

    def createSupport(self):
        ### cube = box( pos=vector(x0,y0,z0), axis=vector(a,b,c), size=vector(L,H,W) )
        self.supportBase = vs.box(pos=vs.vector(0, 0, 0), size=vs.vector(GAN_W, GAN_T, GAN_D), color=vs.color.white)
        self.supportBarLL = vs.box(pos=vs.vector(-GAN_W/2 + BAR_W/2, GAN_H/2, GAN_D/2 - BAR_D/2), size=vs.vector(BAR_W, BAR_H, BAR_D), color=vs.color.orange)
        self.supportBarUL = vs.box(pos=vs.vector(-GAN_W/2 + BAR_W/2, GAN_H/2, -GAN_D/2 + BAR_D/2), size=vs.vector(BAR_W, BAR_H, BAR_D), color=vs.color.orange)
        self.supportBarLR = vs.box(pos=vs.vector(GAN_W/2 - BAR_W/2, GAN_H/2, -GAN_D/2 + BAR_D/2), size=vs.vector(BAR_W, BAR_H, BAR_D), color=vs.color.orange)
        self.supportBarUR = vs.box(pos=vs.vector(GAN_W/2 - BAR_W/2, GAN_H/2, GAN_D/2 - BAR_D/2), size=vs.vector(BAR_W, BAR_H, BAR_D), color=vs.color.orange)
        self.supportTopL = vs.box(pos=vs.vector(-GAN_W/2 + TOP_W/2, GAN_H - (GAN_T/2 + TOP_H/2), 0), size=vs.vector(TOP_W, TOP_H, TOP_D), color=vs.color.white)
        self.supportTopR = vs.box(pos=vs.vector(GAN_W/2 - TOP_W/2, GAN_H - (GAN_T/2 + TOP_H/2), 0), size=vs.vector(TOP_W, TOP_H, TOP_D), color=vs.color.white)

    def createGantry(self):
        ### rod = cylinder( pos=vector(0,2,1), axis=vector(5,0,0), radius=1 )
        # gantry X-axis
        self.gantryAxis.append(vs.box(pos=vs.vector(0, self.x_zoffset, self.x_yoffset), size=vs.vector(XAXIS_W, XAXIS_H, XAXIS_D), color=vs.color.green))
        # gantry Y-axis
        self.gantryAxis.append(vs.box(pos=vs.vector(0, self.y_zoffset, self.y_yoffset), size=vs.vector(YAXIS_W, YAXIS_H, YAXIS_D), color=vs.color.red))
        # gantry Z-axis
        self.gantryAxis.append(vs.cylinder(pos=vs.vector(0, self.z_zoffset, 0), axis=vs.vector(0, -ZAXIS_L, 0), radius=ZAXIS_R, color=vs.color.blue))
        # gantry A-axis
        self.gantryAxis.append(vs.cylinder(pos=vs.vector(0, self.a_zoffset, 0), axis=vs.vector(0, -AAXIS_L, 0), radius=AAXIS_R, color=vs.color.yellow))

    def getGantry(self):
        for i in range(len(self.gantryPosition)):
            if self.modeState.get() == 'M':
                self.gantryTarget[i] = float(self.gantrySlider[i].get())
            if self.modeState.get() == 'A':
                self.gantryTarget[i] = float(self.gantryEntry[i].get())
        return self.gantryTarget

    def updateGantry(self, position):
        self.xPos = position[0]
        self.yPos = position[1]
        self.zPos = position[2]
        self.aPos = position[3]
        self.gantryAxis[0].pos = vs.vector(self.xPos, self.x_zoffset, self.x_yoffset + self.yPos)
        self.gantryAxis[1].pos = vs.vector(0, self.y_zoffset, self.y_yoffset + self.yPos)
        self.gantryAxis[2].pos = vs.vector(self.xPos, self.z_zoffset - self.zPos, self.yPos)
        self.gantryAxis[3].pos = vs.vector(self.xPos, self.a_zoffset - (self.zPos + self.aPos), self.yPos)
        for i in range(len(position)):
            self.gantryPosition[i] = position[i]

    def moveGantry(self):
        self.moveState = True
        self.motorSpeed = float(self.speedEntry.get())
        self.currentPosition = self.gantryPosition

    def manualGantry(self):
        self.updateGantry(self.getGantry())

    def autoGantry(self):
        self.getGantry()
        if self.moveState:
            for i in range(len(self.gantryPosition)):
                if self.gantryTarget[i] > 0:
                    if self.currentPosition[i] <= self.gantryTarget[i]:
                        self.currentPosition[i] = self.currentPosition[i] + self.motorSpeed*(UPDATE_TIME/1000.0)
                elif self.gantryTarget[i] < 0:
                    if self.currentPosition[i] >= self.gantryTarget[i]:
                        self.currentPosition[i] = self.currentPosition[i] - self.motorSpeed*(UPDATE_TIME/1000.0)
                self.updateGantry(self.currentPosition)

        new_position = [round(elem) for elem in self.currentPosition]
        if new_position == self.gantryTarget:
            self.moveState = False

    def homeGantry(self):
        for i in range(len(self.gantryPosition)):
            self.gantrySlider[i].set(0)
            self.gantryTarget[i] = 0
        self.updateGantry(self.gantryTarget)

    def updateSelect(self):
        if self.modeState.get() == 'M':
            self.manualGantry()
        if self.modeState.get() == 'A':
            self.autoGantry()

    def updateTime(self):
        self.systemTime = self.systemTime + UPDATE_TIME/1000.0
        self.systemTime = round(self.systemTime, 2)
        # print(self.systemTime)

    def quitApp(self):
        self.destroy()

    def updateApp(self):
        self.updateTime()
        self.updateSelect()
        self.after(UPDATE_TIME, self.updateApp)

# Run Application
if __name__=="__main__":
    app = Application()
    app.mainloop()
