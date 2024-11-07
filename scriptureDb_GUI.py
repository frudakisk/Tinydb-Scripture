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
    
def showQuizFrame():
    """Show the quiz frame in the GUI and generates quiz questions
    """
    global quizList
    global quizCurrentIndex
    hideAllFrames()
    quizScriptureFrame.pack(fill='both', expand=True)
    quizList = sdb.GetScriptureForQuiz()
    print(len(quizList))
    #show the first verse
    verseString = quizList[quizCurrentIndex]['reference']
    verseBox_quizScriptureFrame.config(text=verseString)
    quizCurrentIndex += 1

    

def NextQuizQuestion():
    """When the user clicks the next button in the quiz frame,
    we should calculate the percentage of how correct they were
    and at the same time show the next question

    So when i click this button, i need to grab the text from the entry box

    """
    global quizCurrentIndex
    if quizCurrentIndex < len(quizList):
        #collect answer first
        userAnswer = userInput_quizScriptureFrame.get()
        versePercentage = sdb.StringPercentageMatch(userAnswer, quizList[quizCurrentIndex]['text'])
        correctnessLabel_quizScriptureFrame.config(text=f"You were {sdb.FormatFloatToPercentage(versePercentage)} correct!")
        userInput_quizScriptureFrame.delete(0, tk.END) #clear the user input box
        #add new verse
        verseString = quizList[quizCurrentIndex]['reference']
        verseBox_quizScriptureFrame.config(text=verseString)
        quizCurrentIndex += 1
        print(quizCurrentIndex)
    
    if quizCurrentIndex == len(quizList):
        nextButton_quizScriptureFrame.config(state=tk.DISABLED)
    
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
quizButton = tk.Button(mainFrame, text="Quiz Scripture", command=showQuizFrame)

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
scriptureTextBox = tk.Text(scriptureFrame, width=200, height=30)
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
#create the quiz frame
quizCurrentIndex = 0
quizList = None
quizScriptureFrame = tk.Frame(root)
frames.append(quizScriptureFrame)
#create the things that will live in this frame
#need a text box to show the verse we want the user to write - noneditable
verseBox_quizScriptureFrame = tk.Label(quizScriptureFrame)
verseBox_quizScriptureFrame.pack(pady=5)
#need a text box for the user to insert their answer
userInput_quizScriptureFrame = tk.Entry(quizScriptureFrame)
userInput_quizScriptureFrame.pack(pady=5)
#How correct they were
correctnessLabel_quizScriptureFrame = tk.Label(quizScriptureFrame)
correctnessLabel_quizScriptureFrame.pack(pady=5)
#Next Button
nextButton_quizScriptureFrame = tk.Button(quizScriptureFrame, text="Next Verse", command=NextQuizQuestion)
nextButton_quizScriptureFrame.pack(pady=5)
#submit button
submitQuizButton_quizScriptureFrame = tk.Button(quizScriptureFrame, text="Submit")
submitQuizButton_quizScriptureFrame.pack(pady=5)
#quit quiz button (like a back button)
quitButton_quizScriptureFrame = tk.Button(quizScriptureFrame, text="Quit", command=showMainMenu)
quitButton_quizScriptureFrame.pack(pady=20)




#start the Tkinter event loop
root.mainloop()
