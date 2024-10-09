import scriptureDb as sdb
import tkinter as tk

frames = []

def hideAllFrames():
    for frame in frames:
        frame.pack_forget()

def showScriptureList():
    """Shows the screen that gives all the scripture on the window
    """
    hideAllFrames()
    scriptureFrame.pack(fill='both', expand=True)
    #insert scripture list into the text box
    scriptureTextBox.config(state=tk.NORMAL)
    scriptureTextBox.delete(1.0, tk.END) #clear the box
    index = 1
    table = sdb.db.all()
    
    for item in table:
        scriptureTextBox.insert(tk.END, f"{index}. {item['reference']} | {item['translation']} - {item['text']}\n\n")
        index += 1
        
    scriptureTextBox.config(state=tk.DISABLED)
    
def showAddScripture():
    """SHows the screen where you can add scripture to your list
    """
    hideAllFrames()
    addScriptureFrame.pack(fill='both', expand=True)

def showMainMenu():
    """Shows the Main Menu Screen in the GUI
    """
    hideAllFrames()
    mainFrame.pack(fill='both', expand=True)
    
def ShowScripture():
    """Takes information from the userScriptureRef and userTranslation
    to find the scripture they are looking for from the API. Once we gather
    the information, we display it on a new text box and repacked some items
    in the screen
    """
    #unpack the back button to make room for new widgets
    showScripture.pack_forget()
    submitButton.pack_forget()
    backButton_AddScriptureFrame.pack_forget()
    #get information and find scripture with it
    scriptureRef = userScriptureRef.get()
    translation = userTranslation.get()
    scripture = sdb.FindScripture(scriptureRef, translation)
    #assign scripture to global variable - it will be used in different functions
    global currentScripture
    currentScripture = scripture
    #configure the showScripture textbox - clear any text in it and add new scripture text
    showScripture.config(state=tk.NORMAL)
    showScripture.delete(1.0, tk.END) #clear the box
    showScripture.insert(tk.END, scripture) #the scripture object needs to go here so we can save object, not just text
    showScripture.config(state=tk.DISABLED)
    #pack everything - including backButton
    showScripture.pack(pady=20)
    submitButton.pack(pady=10)
    backButton_AddScriptureFrame.pack(pady=10)
    
    
    
def SubmitScripture():
    global currentScripture
    sdb.InsertScriptureGUI(currentScripture)
    currentScripture = None
    


root = tk.Tk()


#size of window
root.geometry("1000x800")
root.title("Memorize Scripture")

#create main frame (initial window)
mainFrame = tk.Frame(root)
frames.append(mainFrame)

listButton = tk.Button(mainFrame, text="List Scripture", command=showScriptureList)
addButton = tk.Button(mainFrame, text="Add Scripture", command=showAddScripture)
quizButton = tk.Button(mainFrame, text="Quiz Scripture")

#pack the buttons
listButton.pack()
addButton.pack()
quizButton.pack()

mainFrame.pack(fill='both', expand=True)

#---------------------------------------------------------------------------------------------

#create the scripture List frame
scriptureFrame = tk.Frame(root)
frames.append(scriptureFrame)
#create the things that will live in this frame
scriptureTextBox = tk.Text(scriptureFrame, width=200, height=50)
scriptureTextBox.pack(pady=20)

#back button to return to main menu
backButton = tk.Button(scriptureFrame, text="Back", command=showMainMenu)
backButton.pack(pady=10)

#---------------------------------------------------------------------------------------------

#Create the Add Scripture frame
addScriptureFrame = tk.Frame(root)
frames.append(addScriptureFrame)
#Create the things that will live in this frame
#text box for inserting scripture reference
userScriptureRefLabel = tk.Label(addScriptureFrame, text="Scripture Reference:")
userScriptureRef = tk.Entry(addScriptureFrame)
userScriptureRefLabel.pack(pady=5)
userScriptureRef.pack(pady=5)
#text box for inserting scripture translation
userTranslationLabel = tk.Label(addScriptureFrame, text="Translation:")
userTranslation = tk.Entry(addScriptureFrame)
userTranslationLabel.pack(pady=5)
userTranslation.pack(pady=5)
#Show scripture button
currentScripture = None #changed locally in ShowScripture and SubmitScripture
showButton = tk.Button(addScriptureFrame, text="Show Scripture", command=ShowScripture)
showButton.pack(pady=20)
#Submit Panel - only shows when the showButton has been clicked
showScripture = tk.Text(addScriptureFrame, width=200, height=3)
submitButton = tk.Button(addScriptureFrame, text="Add Scripture", command=SubmitScripture)


#Back button
backButton_AddScriptureFrame = tk.Button(addScriptureFrame, text="Back", command=showMainMenu)
backButton_AddScriptureFrame.pack(pady=10)

#---------------------------------------------------------------------------------------------

#start the Tkinter event loop
root.mainloop()
