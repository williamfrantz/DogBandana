#!/usr/local/bin/python
import os
import sys
# For some reason TextMate needs this in order to import tkinter
# sys.path.append(os.path.abspath('/usr/local/opt/python-tk@3.11/libexec'))

# Imports
import math
import random
import tkinter as tk
import tkinter.font
from PIL import Image, ImageTk, ImageFont, ImageDraw, ImageOps
from functools import partial


class Graphic():
    ## Private Constants
    DEFAULTSIZE = (16*30, 9*30)
    DEFAULTTHUMBNAILSIZE = (128, 128)
    SCALEFACTOR = 0.60
    

    ## Creator
    def __init__(self, givenFilename=None, givenText=None, givenSize=None):
        # Private attributes
        self.filename = None
        self.image = None
        self.thumbnail = None
        self.thumbnailSize = None
        self.text = None
        self.font = None
        self.fontSize = None
        self.targetSize = None
        self.basename = None

        if (givenFilename):
            self.setFilename(givenFilename)
        if (givenText):
            self.setText(givenText)
        if (givenSize):
            self.setSize(givenSize)


    def __getFont(self, givenSize):
        assert(givenSize > 0)        
        assert(os.path.isfile(self.getFilename()))
        
        if (givenSize == self.fontSize):
            # This font has already be loaded in this size
            return(self.font)
        # Else a new size was requested, load it up
        self.fontSize = givenSize
        try:
            self.font = ImageFont.truetype(self.getFilename(), self.fontSize)
        except Exception as e:
            print(e)
            print('Cannot read font file:', self.filename)
            self.fontSize = None
            self.font = None
        assert(self.font)
        return(self.font)
    
    
    def getFilename(self):
        return(self.filename)

        
    def setFilename(self, givenFilename):
        self.filename = givenFilename
        if (givenFilename):
            self.basename = os.path.basename(givenFilename)
        else:
            self.basename = None
            

    def getName(self):
        return(self.basename)


    def getText(self):
        return(self.text)


    def setText(self, givenText):
        assert(givenText)
        if (self.text != givenText):
            self.text = givenText
            self.image = None
    
        
    def getSize(self):
        return(self.getImage().size)


    def setSize(self, givenSize = None):
        if (not givenSize):
            givenSize = self.DEFAULTSIZE
        if (self.targetSize != givenSize):
            self.targetSize = givenSize
            self.image = None

            
    def getImage(self, givenSize=None):
        if (givenSize):
            self.setSize(givenSize)
        if (self.image):
            return(self.image)
        # Else no image exists so create one        
        if (self.text):
            # Text was given so return a text image
            return(self.__getTextImage())
        # Else
        # No text was given so this must be an image
        return(self.__getImage())
        
    
    def __getImage(self):
        assert(self.filename)
        if (self.image):
            return(self.image)
        # Else
        try:
            self.image = Image.open(self.filename)
        except Exception as e:
            print(e)
            print('Cannot read image file:', self.filename)
        return(self.image)


    def __textCanFit(self, givenFontSize):
        assert(givenFontSize > 0)
        assert(self.text)
        assert(self.targetSize)
        _, _, w, h = self.__getFont(givenFontSize).getbbox(self.text)
        # Use SCALEFACTOR to make the text smaller than the targetSize
        return(w <= self.SCALEFACTOR * self.targetSize[0] and h <= self.SCALEFACTOR * self.targetSize[1])
        

    def __getTextImage(self):
        assert(self.text)
        assert(self.targetSize)
        assert(self.filename)

        # TODO: Implement a more efficient binary search algorithm to find the perfect font size
        fontSize = 500
        while (not self.__textCanFit(fontSize)):
            fontSize = fontSize - 10
        # The best font size has been found
        
        self.image = Image.new("RGBA", self.targetSize, (255, 255, 255, 0))
        assert(self.image)

        myDrawing = ImageDraw.Draw(self.image)
        assert(myDrawing)
        
        _, _, w, h = self.__getFont(fontSize).getbbox(self.text)
        myDrawing.text(((self.targetSize[0]-w)/2, (self.targetSize[1]-h)/2), self.getText(), font=self.__getFont(fontSize), fill=(0,0,0,255))
        return(self.image)


    def getThumbnail(self, givenSize = None):
        if (givenSize):
            self.setThumbnailSize(givenSize)
        if (self.thumbnail):
            return(self.thumbnail)
        if (not self.thumbnailSize):
            self.thumbnailSize = self.DEFAULTTHUMBNAILSIZE
        if (not self.targetSize):
            self.targetSize = self.DEFAULTSIZE
        self.thumbnail = self.getImage()
        self.image = None # Memory efficient!
        self.thumbnail.thumbnail(self.thumbnailSize)
        return(self.thumbnail)


    def getThumbnailSize(self):
        return(self.getThumbnail().size)
        
    
    def setThumbnailSize(self, givenSize=None):
        if (not givenSize):
            givenSize = self.DEFAULTTHUMBNAILSIZE
        if (self.thumbnailSize != givenSize):
            self.thumbnailSize = givenSize
            self.thumbnail = None

        
    def show(self):
        self.getImage().show()
        


class Overlay():
    ## Private Constants
    DEFAULTSIZE = (16*30, 9*30)
    
    ### Creator
    def __init__(self, givenBackground, givenText, givenSize=None):
        ## Private Attributes
        self.size = None
        self.background = None
        self.text = None
        self.image = None

        if (not givenSize):
            givenSize = self.DEFAULTSIZE
        self.background = givenBackground
        self.text = givenText
        self.size = givenSize

    def setSize(self, givenSize=None):
        if (not givenSize):
            givenSize = self.DEFAULTSIZE
        if (givenSize != self.size):
            self.size = givenSize
            self.image = None

    def getImage(self, givenSize=None):
        if (givenSize):
            self.setSize(givenSize)
        if (self.image):
            return(self.image)
        # Make the image
        # Start by scaling up the background to the desired size
        self.image = ImageOps.contain(self.background.getImage(), self.size)
        # Get the foreground text in the same size as the background        
        myForeground = self.text.getImage(self.image.size)
        self.image.paste(myForeground, (0,0), mask=myForeground)
        
        return(self.image)
        

    def getPrintImage(self):
        return(ImageOps.mirror(self.getImage()))


class ImageLibrary():

    ### Private Constants
    IMAGEEXTENSIONS = ('.png', '.jpg', '.jpeg', '.tiff', '.bmp', '.gif')
    FONTEXTENSIONS = ('.ttf', '.otf', 'ttc')

    
    ### Creator
    def __init__(self, givenDirectory, givenText=None, givenSize=None):

        self.directory = givenDirectory
        self.graphicList = []
        self.currentItem = None
        self.thumbnailSize = (128,128)
        
        for filename in os.listdir(self.directory):
            if (givenText):
                if (filename.lower().endswith(self.FONTEXTENSIONS)):
                    self.graphicList.append(Graphic(os.path.join(self.directory, filename), givenText, givenSize))
            else:
                if (filename.lower().endswith(self.IMAGEEXTENSIONS)):
                    self.graphicList.append(Graphic(os.path.join(self.directory, filename)))

    def __iter__(self):
        self.currentItem = 0
        return(self)
        
    def __next__(self):
        if (self.currentItem < len(self.graphicList)):
            item = self.graphicList[self.currentItem]
            self.currentItem = self.currentItem + 1
            return(item)
        else:
            raise StopIteration

    ### Methods
    
    def setThumbnailSize(self, givenSize):
        self.thumbnailSize = givenSize
        for i in self.graphicList:
            i.setThumbnailSize(givenSize)
        
    def getSize(self):
        return(len(self.graphicList))
        
    
    def getRandom(self):
        return(random.choice(self.graphicList))


class ImageGallery(tk.Frame):
    BUTTONWIDTH = 15
    
    
    ### Creator
    def __init__(self, givenParent, givenLibrary):
        ### Private attributes
        self.selectedItem = None
        self.resizeTimer = None
        self.library = givenLibrary
        self.parent = givenParent
        self.size = (givenParent.winfo_reqwidth(), givenParent.winfo_reqheight())
        
        tk.Frame.__init__(self, self.parent)
        
        self.configure(background='white')
        
        self.parent.bind('<Configure>', self.__configure)


    def __configure(self, event):
        if (event.widget != self.parent):
            # It's an event for some widget inside this frame. Ignore it.
            return()
            
        if (self.size == (self.parent.winfo_width(), self.parent.winfo_height())):
            # The size didn't change. Ignore it.
            return()
        # Else
        self.size = (self.parent.winfo_width(), self.parent.winfo_height())

        if (self.resizeTimer):
            # There was already a timer running. Cancel it.
            self.after_cancel(self.resizeTimer)
            self.resizeTimer = None

        # No timer is running. Start one.
        self.__clear()
        self.resizeTimer = self.after(300, self.__fill)
        

    def getLibrary(self):
        return(self.library)


    def getParent(self):
        return(self.parent)
    
    
    def getSize(self):
        return((self.getParent().winfo_width(), self.getParent().winfo_height()))
        
    def __clear(self):
        # Delete everything that currently exists in the frame
        for widget in self.winfo_children():
            widget.destroy()
            
    
    def __fill(self):
        # Remove any resize timer that might exist
        self.resizeTimer = None
        self.__clear()
        self.getParent().update()
        w, h = self.getSize()
        parent = self.getParent()
        library = self.getLibrary()

        assert(w > 1)
        assert(h > 1)
        # Sanity check
        #if (w <= 1 or h <= 1):
        #    return()

        aspect = w / h
        
        if (aspect > 1):
            thumbnailSize = w / (library.getSize() * aspect)**0.5
        else:
            thumbnailSize = h / (library.getSize() / aspect)**0.5
            
        thumbnailSize = int(0.75 * thumbnailSize) # a bit smaller than necessary
        numCol = int(w/thumbnailSize)
        columnCount = 0
        rowCount = 0
        library.setThumbnailSize((thumbnailSize, thumbnailSize))

        # Cancel Button
        row = tk.Frame(self)
        row.grid(row=rowCount, column=0, columnspan=numCol)
        cancelButton = tk.Button(row, width=self.BUTTONWIDTH, text='Cancel', command=self.__cancel, bg='white')
        cancelButton.pack(side = tk.LEFT, padx = 5, pady = 5)
        rowCount = rowCount + 1
                
        for i in library:
            myPhoto = ImageTk.PhotoImage(i.getThumbnail())
            myButton = tk.Button(self, image=myPhoto, command=partial(self.__click, i), bg='white', width=thumbnailSize, height=thumbnailSize, padx=0, pady=0, borderwidth=0, highlightthickness=0, relief='flat')
            myButton.imgref = myPhoto
            myButton.grid(row=rowCount, column=columnCount)
            columnCount = columnCount + 1
            if (columnCount >= numCol):
                columnCount = 0
                rowCount = rowCount + 1
        self.parent.geometry(str(self.size[0])+'x'+str(self.size[1]))
        

    def __click(self, clickedImage):
        self.selectedItem = clickedImage
        self.parent.nextFrame(self)
    
    def __cancel(self):
        self.selectedItem = None
        self.parent.nextFrame(self)

    def getSelected(self):
        return(self.selectedItem)
        
    
    def pack(self):
        self.__fill()
        super().pack(fill=tk.BOTH, expand=tk.FALSE)
        

class OrderForm(tk.Frame):
    
    LOGOSIZE = (196, 196)
    BUTTONWIDTH = 15
    LABELWIDTH = 15
    ENTRYWIDTH = 30
    FONTSIZE = 24
    
    ### Creator
    def __init__(self, givenParent, givenPreview, givenLogo):
        ### Private attributes
        self.name = None
        self.phone = None
        self.petName = None
        self.image = None
        self.logoLabel = None
        self.parent = givenParent
        self.fieldList = ('Name', 'Phone Number', 'Pet Name')
        tk.Frame.__init__(self, self.parent)
        
        self.configure(background='white')

        tk.font.nametofont("TkDefaultFont").config(size=self.FONTSIZE)
        
        row = tk.Frame(self, bg='white')
        row.pack(side = tk.TOP, fill = tk.X, padx = 5 , pady = 5)
        self.logoLabel = tk.Label(row, bg='white')
        self.logoLabel.pack(side = tk.TOP, padx = 5, pady = 5)
        self.setLogo(givenLogo)
        
        row = tk.Frame(self, bg='white')
        row.pack(side = tk.TOP, padx = 5 , pady = 5)
        clearButton = tk.Button(row, width=self.BUTTONWIDTH, text='Clear', command=self.parent.clear, bg='white')
        clearButton.pack(side = tk.LEFT, padx = 5, pady = 5)
        fontButton = tk.Button(row, width=self.BUTTONWIDTH, text='Change Font', command=self.parent.changeFont, bg='white')
        fontButton.pack(side = tk.LEFT, fill = tk.X, padx = 5 , pady = 5)
        backgroundButton = tk.Button(row, width=self.BUTTONWIDTH, text='Background', command=self.parent.changeBackground, bg='white')
        backgroundButton.pack(side = tk.LEFT, padx = 5 , pady = 5)
        printButton = tk.Button(row, width=self.BUTTONWIDTH, text='Print', command=self.parent.printImage, bg='white')
        printButton.pack(side = tk.LEFT, fill = tk.X, padx = 5 , pady = 5)

        row = tk.Frame(self, bg='white', highlightbackground='grey80', highlightthickness=2)
        row.pack(side = tk.TOP, padx = 5 , pady = 5)
        self.entryList = self.makeform(row, self.fieldList)
        self.parent.bind('<Return>', self.parent.changeEntries)

        row = tk.Frame(self, bg='white')
        row.pack(side = tk.TOP, fill = tk.X, padx = 5 , pady = 5)
        col = tk.Frame(row, bg='white')
        col.pack(side = tk.LEFT, fill=tk.Y, padx=0, pady=0)

        col = tk.Frame(row, bg='white')
        col.pack(side = tk.TOP, fill=tk.Y, padx=0, pady=0)
        self.previewLabel = tk.Label(col, bg='white')
        self.previewLabel.pack(side = tk.TOP, padx = 0, pady = 0)

        self.setPreview(givenPreview)
        
        # Set up the bindings
        for i in self.entryList:
            self.entryList[i].bind('<FocusOut>', self.parent.changeEntries)
        

    def setLogo(self, givenLogo):
        myPhoto = ImageTk.PhotoImage(givenLogo.getThumbnail(self.LOGOSIZE))        
        self.logoLabel.configure(image=myPhoto)
        self.logoLabel.imgref = myPhoto
        
        
    def setPreview(self, givenPreview):
        self.preview = givenPreview
        myPhoto = ImageTk.PhotoImage(givenPreview.getImage())        
        self.previewLabel.configure(image=myPhoto)
        self.previewLabel.imgref = myPhoto
        

    def makeform(self, parent, fields):
        entries = {}
        for field in fields:
            row = tk.Frame(parent, bg='white')
            lab = tk.Label(row, width=self.LABELWIDTH, text=field+": ", anchor='e', bg='white')
            ent = tk.Entry(row, width=self.ENTRYWIDTH, font=('Georgia 30'), bg='grey95')
            row.pack(side = tk.TOP, padx = 5 , pady = 5)
            lab.pack(side = tk.LEFT)
            ent.pack(side = tk.LEFT, expand = tk.NO, fill = tk.X)
            entries[field] = ent
        return(entries)


    def getEntryList(self):
        return(self.entryList)


### 
class App(tk.Tk):
    ## Private constants
    ASSETDIR = './Assets'
    MAINPAGE = 1
    ORDERFORM = 2
    BACKGROUNDGALLERY = 3
    FONTGALLERY = 4
    IMAGEPREVIEW = 5    
    PREVIEWSIZE = (450, 450)
    WINDOWSIZE = (1280, 800)

    ## Creator
    def __init__(self, *args, **kwargs):
        # __init__ function for class Tk
        tk.Tk.__init__(self, *args, **kwargs)
        
        # Private attributes
        self.mode = None
        self.background = None
        self.name = None
        self.text = None
        self.fontFilename = None
        self.orderForm = None
        self.backgroundGallery = None
        self.fontGallery = None
        self.backgroundLibrary = None
        self.fontLibrary = None
        self.preview = None
        self.petName = None
        self.currentFrame = None
        self.size = None
        
        #self.geometry('1280x720')
        self.configure(background='white')
        self.title('NextGen')
        self.showMode(App.ORDERFORM) 


    def clear(self):
        self.petName = None
        self.background = None
        self.fontFilename = None
        self.preview = None
        self.text = None
        self.fontLibrary = None
        self.fontGallery = None
        
        if (self.orderForm):
            entryList = self.orderForm.getEntryList()
            entryList['Name'].delete(0, tk.END)
            entryList['Phone Number'].delete(0, tk.END)
            entryList['Pet Name'].delete(0, tk.END)
            self.orderForm.setPreview(self.getPreview())
            
    def changeBackground(self):
        self.orderForm.pack_forget()
        self.showMode(App.BACKGROUNDGALLERY)
        
    def changeFont(self):
        self.orderForm.pack_forget()
        self.showMode(App.FONTGALLERY)
        
    def printImage(self):
        print('App', 'printImage')
        
    
    def changeEntries(self, event):
        entryList = self.orderForm.getEntryList()
        if (entryList['Pet Name'].get()):
            self.setPetName(entryList['Pet Name'].get())
        

    def getPetName(self):
        if (self.petName):
            return(self.petName)
        # Else
        randomName = random.choice(['Rover', 'Fido', 'Champ', 'Princess', 'Spot', 'Bandit', 'Lucky', 'Lassie', 'Rex', 'King', 'Peanut', 'Sugar', 'Cookie', 'Cosmo', 'Pluto', 'Checkers', 'Rocky', 'Storm'])
        self.setPetName(randomName)
        return(self.petName)
        
        
    def setPetName(self, givenName):
        if (givenName == self.petName):
            return()
        # Else
        self.petName = givenName
        if (self.text):
            self.text = Graphic(self.text.getFilename(), givenName)
        self.preview = None
        self.fontLibrary = None
        self.fontGallery = None
        if (self.orderForm):
            self.orderForm.setPreview(self.getPreview())
        self.update()
        

    def getBackgroundLibrary(self):
        if (self.backgroundLibrary):
            return(self.backgroundLibrary)
        # Else
        self.backgroundLibrary = ImageLibrary(os.path.join(self.ASSETDIR, 'Background'))
        return(self.backgroundLibrary)


    def getBackgroundGallery(self):
        if (self.backgroundGallery):
            return(self.backgroundGallery)
        # Else
        self.backgroundGallery = ImageGallery(self, self.getBackgroundLibrary())
        return(self.backgroundGallery)


    def getFontLibrary(self):
        if (self.fontLibrary):
            return(self.fontLibrary)
        # Else
        self.fontLibrary = ImageLibrary(os.path.join(self.ASSETDIR, 'Font'), self.getPetName())
        return(self.fontLibrary)


    def getFontGallery(self):
        if (self.fontGallery):
            return(self.fontGallery)
        # Else
        self.fontGallery = ImageGallery(self, self.getFontLibrary())
        return(self.fontGallery)

    
    def getBackground(self):
        if (self.background):
            return(self.background)
        # Else
        self.setBackground(self.getBackgroundLibrary().getRandom())
        return(self.background)
        
        
    def setBackground(self, givenBackground):
        self.background = givenBackground
        self.preview = None
        if (self.orderForm):
            self.orderForm.setPreview(self.getPreview())
        self.update()


    def getText(self):
        if (self.text):
            return(self.text)
        # Else
        self.text = self.getFontLibrary().getRandom()
        return(self.text)
        
        
    def setText(self, givenText):
        self.text = givenText
        self.preview = None
        if (self.orderForm):
            self.orderForm.setPreview(self.getPreview())
        self.update()        

    
    def getPreview(self):
        if (self.preview):
            return(self.preview)
        # Else
        self.preview = Overlay(self.getBackground(), self.getText(), self.PREVIEWSIZE)
        assert(self.preview)
        return(self.preview)
    

    def getOrderForm(self):
        if (self.orderForm):
            return(self.orderForm)
        self.orderForm = OrderForm(self, self.getPreview(), Graphic(os.path.join(self.ASSETDIR, 'logo.png')))
        return(self.orderForm)
        

    def showMode(self, givenMode):
        # Save the size of the current window!
        if (self.size):
            self.size = (self.winfo_width(), self.winfo_height())
        # Else ignore the initial size of the window!
        
        
        self.mode = givenMode
        if (self.currentFrame):
            self.currentFrame.pack_forget()
        if (self.mode == App.MAINPAGE):
            assert(False)
        if (self.mode == App.ORDERFORM):
            self.currentFrame = self.getOrderForm()
            self.currentFrame.pack(side=tk.TOP, expand=tk.YES, fill=tk.X)
        if (self.mode == App.BACKGROUNDGALLERY):
            self.currentFrame = self.getBackgroundGallery()
            self.currentFrame.pack()
            #self.getBackgroundGallery().pack(side=tk.TOP, expand=tk.YES, fill=tk.X)            
        if (self.mode == App.FONTGALLERY):
            #self.getFontGallery().pack(side=tk.TOP, expand=tk.YES, fill=tk.X)
            self.currentFrame = self.getFontGallery()
            self.currentFrame.pack()
        if (self.mode == App.IMAGEPREVIEW):
            # self.background is set
            # self.fontFilename is set

            self.text = Text(self.fontFilename, self.getPetName(), self.background.getSize()) # Could reduce text size here!
            
            myOverlay = Overlay(self.background, self.text, (16*100, 9*100))
            myPhoto = ImageTk.PhotoImage(myOverlay.getImage())
            myLabel = tk.Label(self, image=myPhoto)
            myLabel.imgref = myPhoto
            myLabel.pack()
            
        # Fix the window size!
        if (not self.size):
            self.size = self.WINDOWSIZE
        self.geometry(str(self.size[0])+'x'+str(self.size[1]))
        self.update()
        
            

    def nextFrame(self, lastFrame):
        
        if (self.mode == App.BACKGROUNDGALLERY):
            if (self.currentFrame.getSelected()):
                self.setBackground(self.currentFrame.getSelected())
            self.showMode(App.ORDERFORM)
            return()
            
        if (self.mode == App.FONTGALLERY):
            if (self.currentFrame.getSelected()):
                #self.text = lastFrame.getSelected()
                self.setText(self.currentFrame.getSelected())
            self.showMode(App.ORDERFORM)
            return()


    def showFrame(self, givenFrame):
        assert(True)



if __name__ == '__main__':
    myApp = App()
    myApp.mainloop()
    exit()
