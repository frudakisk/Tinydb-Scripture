from tinydb import TinyDB, Query
import requests
import re
from difflib import SequenceMatcher
import random
import tkinter as tk

#add scripture into database (DONE)
#make sure scripture does not already exist in the database before adding it (DONE)
#give a flow of creating scripture untill user is done (DONE)
#instead of mapping, try to use a class (DONE)

#I think I should be using a bible api so that the user does not have to write out the entire verse each time (DONE)

#API needs translation, bookId, chapter number, and verse number
#I should allow people to input multiple verses such as John 3:16-18

'''
TODO:

'''

translationsBook = "https://bolls.life/static/bolls/app/views/translations_books.json"

class Scripture:
    def __init__(self, reference: str, bookName: str, chapter: int, verse: int, text: str, translation: str):
        self.reference = reference
        self.bookName = bookName
        self.chapter = chapter
        self.verse = verse
        self.text = text
        self.translation = translation
        
    def __str__ (self):
        return f"{self.reference} | {self.translation} - {self.text}"


#init a database and store is as a JSON file
db = TinyDB("scriptures.json")


#Insert scripture into the database
#make sure it is not already there
def InsertScripture(s: Scripture) -> bool:
    """Insert scripture into the database and
    makes sure that it is not already in the database

    Args:
        s (Scripture): of type Scripture and is just some
        information about a certain verse

    Returns:
        bool: returns true if we can add it to database, false if it cant
    """
    scripture = Query()
    if len(db.search(scripture.reference == s.reference)) <= 0:
        print(f"Scripture is:\n{s.text}\nAre you sure you want to add this scripture? (Y/N)")
        decision = input()
        if decision.upper().strip() == 'Y':   
            db.insert(s.__dict__)
            print("Scripture has been added to the database")
            return True
        else:
            print("Scripture was not added to the database")
            False
    else:
        print("This scripture already exist in our database")
        return False
    
def InsertScriptureGUI(s: Scripture):
    scripture = Query()
    if len(db.search(scripture.reference == s.reference)) <= 0: 
        db.insert(s.__dict__)
    else:
        print("This scripture already exist in our database")

#Cuts reference into its three parts: Book name, chapter number, verse number
#returns a list of these items in the respective order
def SpliceScripture(reference: str) -> list:
    """Cuts reference into its three parts: Book name, chapter number,
    and verse number. Returns a list of these items in the respective order

    Args:
        reference (str): A string that represents a scripture reference like John 3:16

    Returns:
        list: A list that contains the book name, chapter number, and verse number
    """
    #expecting something like 'John 3:16'
    items = reference.split(' ')
    if len(items) >= 3:
        #for things like 2 Kings or 1 Corinthians
        #join items[0] and items[1], then remove items[1]
        items[0] = items[0] + ' ' + items[1]
        items.pop(1)
    temp = items[1].split(":")
    items = [items[0], int(temp[0]),int(temp[1])]
    return items


#Replaces <br> tags with newlines, and all other html tags with ''
def RemoveHtmlTags(text:str) -> str:
    """Replaces <br> tags with newlines, and all other html tags with ''

    Args:
        text (str): text to clean. usually a verse

    Returns:
        str: the cleaned up version of the verse
    """
    clean = re.sub(r'<br.*?>', '\n', text)
    clean = re.sub(r'<.*?>', '', clean)
    clean = clean.replace("\u2019", "'")
    clean = clean.replace("\u201c", '"')
    clean = clean.replace("\u201d" , '"')
    return clean

def CleanReference(reference: str) -> str:
    """Cleans the users reference by capatalizing the book name and
    removing any whitespace outside of the text

    Args:
        reference (str): the reference the user input

    Returns:
        str: a cleaned version of the reference that is capitilized and no extra whitespce
    """
    cleanedReference = reference.title().strip()
    return cleanedReference

def CreateAPIVerse(translation: str, bookId: int, scriptureItems: list) -> dict:
    """Request a verse from our API using the translation, book id, and verse information
    and returns a json of that verse

    Args:
        translation (str): The translation we use to find the verse
        bookId (int): and ID that represents the name of a book in the bible in the current
        translation
        scriptureItems (list): contains verse number information

    Returns:
        dict: a dict in JSON format that contains info about the requested verse
    """
    url = f"https://bolls.life/get-verse/{translation}/{bookId}/{scriptureItems[1]}/{scriptureItems[2]}/"
    response = requests.get(url)
    apiData = response.json()
    return apiData


def GetTranslationBookData() -> dict:
    """Gets data from the constant url about translations and the books in that bible translation

    Returns:
        dict: a json format dictionary that contains bible book information for all kinds of translations
    """
    response = requests.get(translationsBook)
    data = response.json()
    return data


def IsTranslationReal(data: dict, translation: str) -> bool:
    """Checks if translation is an item in data

    Args:
        data (dict): a JSON format dictionary that contains bible translations and books in that translation
        translation (str): translation user wants verse in

    Returns:
        bool: True if translation is in data, false if not
    """
    if translation in data:
        return True
    else:
        return False

def GetLikelyBookID(data: dict, scriptureItems: list) -> int:
    """This function is to be used when we cannot find the input bookName in the
    translation that the user requested. So, we take the input bookName and try
    to find it in the WEB translation. we are returned a bookid if we can find 
    a close match, otherwise we are returned -1.

    Args:
        data (dict): a JSON format dictonary that contains bible translations and books in that translation
        scriptureItems (list): A scripture reference split up by book name, chapter number, and verse number

    Returns:
        int: _description_
    """
    #try to find book. If for whatever reason we cant find it (translation not real), just return false
    try:
        #check if the book name is even a real one within the translation
        bookName = scriptureItems[0]
            
        #if we haven't found a match, maybe we are in a translation with long book names
        #compare bookName to the book names in WEB to see if it's there
        for item in data['WEB']:
            if bookName == item['name']:
                return item['bookid']
            
        return -1
    except:
        return -1

def IsBookReal(data: dict, scriptureItems: list, translation: str) -> bool:
    """Checks if the book name is a real book in the current decided translation.
    The translation variable should already be varified as true before using this method

    Args:
        data (dict): a JSON format dictonary that contains bible translations and books in that translation
        scriptureItems (list): A scripture reference split up by book name, chapter number, and verse number
        translation (str): translation user wants verse in

    Returns:
        bool: returns True if book is in translation, false otherwise
    """
    #try to find book. If for whatever reason we cant find it (translation not real), just return false
    try:
        #check if the book name is even a real one within the translation
        bookName = scriptureItems[0]

        for item in data[translation]: #Translation might not be real
            if bookName == item['name']:
                return True
            
        #if we haven't found a match, maybe we are in a translation with long book names
        #compare bookName to the book names in WEB to see if it's there
        for item in data['WEB']:
            if bookName == item['name']:
                return True
            
        return False
    except:
        return False


def IsChapterReal(data: dict, scriptureItems: list, translation: str) -> bool:
    """Checks if the chapter number of the scripture reference is a real chapter

    Args:
        data (dict): a JSON format dictonary that contains bible translations and books in that translation
        scriptureItems (list): A scripture reference split up by book name, chapter number, and verse number
        translation (str): translation user wants verse in

    Returns:
        bool: returns True if chapter is real (depends on if the translation is real), false otherwise
    """
    try:
        bookName = scriptureItems[0]
        chapterNumber = scriptureItems[1]

        for item in data[translation]: #translation might not be real
            if bookName == item['name']: #user bookName might not be suitable for current translation
                maxChapters = item['chapters']
                if chapterNumber <= maxChapters:
                    return True
                
        for item in data['WEB']:
            if bookName == item['name']:
                maxChapters = item['chapters']
                if chapterNumber <= maxChapters:
                    return True
        
        return False
    except:
        return False



def IsVerseReal(data: dict, scriptureItems: list, translation: str) -> bool:
    """Checks if the verse number of the scripture reference is real

    Args:
        data (dict): a JSON format dictonary that contains bible translations and books in that translation
        scriptureItems (list): A scripture reference split up by book name, chapter number, and verse number
        translation (str): translation user wants verse in

    Returns:
        bool: returns True if verse is real (also depends on if the Book and Chapter are real), false otherwise
    """
    #make a book id
    bookId = GetBookId(data, scriptureItems, translation)
    
    if bookId == -1:
        return False
    
    url = f"https://bolls.life/get-text/{translation}/{bookId}/{scriptureItems[1]}/"
    #create json from url
    response = requests.get(url)
    #check if info was found
    if response.status_code == 404:
        print(f"Data for reference {scriptureItems} could not be found")
        return False
    chapterData = response.json()
    #now we check if the verse number is an item in this chapterData
    for item in chapterData:
        if scriptureItems[2] == item['verse']:
            return True
        
    return False

def GetBookId(data: dict, scriptureItems: list, translation: str) -> int:
    """Given a book name, we get the book id in the current translation. Or we
    give a likely book id

    Args:
        data (dict): a JSON format dictonary that contains bible translations and books in that translation
        scriptureItems (list): A scripture reference split up by book name, chapter number, and verse number
        translation (str): translation user wants verse in

    Returns:
        int: the id of the book, or -1 if we cannot find the book
    """
    try:
        bookName = scriptureItems[0] #this is the bookName the user input, might not be correct book name for translation
        for item in data[translation]: #we should be checking if this translation is even real FIRST
            if bookName == item['name']:
                return item['bookid']
        return GetLikelyBookID(data, scriptureItems)
    except:
        return -1

def IsReferenceRealInTranslation(data: dict, scriptureItems: list, translation: str, reference: str) -> bool:
    """Takes into account every item in a scripture reference and makes sure that the
    reference does exist within the translation the user selected

    Args:
        data (dict): a JSON format dictonary that contains bible translations and books in that translation
        scriptureItems (list): A scripture reference split up by book name, chapter number, and verse number
        translation (str): translation user wants verse in

    Returns:
        bool: True if the scripture is real, False otherwise
    """
    failureResponse = ""
    myBool = True

    isTranslationReal = IsTranslationReal(data, translation)
    isBookReal = IsBookReal(data, scriptureItems, translation)
    isChapterReal = IsChapterReal(data, scriptureItems, translation)
    isVerseReal = IsVerseReal(data, scriptureItems, translation)

    if not isTranslationReal:
        failureResponse += f"Translation {translation} is not real or not supported\n"
        myBool = False

    if not isBookReal:
        failureResponse += f"Book name {scriptureItems[0]} is not real in reference '{reference}'\n"
        myBool = False

    if not isChapterReal:
        failureResponse += f"Chapter {scriptureItems[1]} is not real in reference '{reference}'."
        if  not isBookReal:
            failureResponse += f" Make sure book name is correct\n"
        else:
            failureResponse += "\n"
        myBool = False

    if not isVerseReal:
        failureResponse += f"Verse {scriptureItems[2]} is not real in reference '{reference}'."
        if not isChapterReal and not isBookReal:
            failureResponse += f" Make sure book name and/or chapter number are correct\n"
        elif not isChapterReal and isBookReal:
            failureResponse += f" Make sure chapter number is correct\n"
        else:
            failureResponse += "\n"
        myBool = False

    if myBool:
        return True
    else:
        print(failureResponse)
        return False
    
def AddLoop():
    """Looping process for adding scripture into the tinyDB
    """
    isOn = True
    data = GetTranslationBookData()
    while(isOn):
        print("enter 'done' to end process")
        reference = input("Reference: ")

        if reference.lower().strip() == 'done':
            isOn = False
            break

        translation = input("Translation: ")

        #format reference
        reference = CleanReference(reference)
        #parse input to grab book name, chapter num and verse num
        scriptureItems = SpliceScripture(reference)
        #format translation
        translation = translation.upper().strip()
        
        #check if the book is real. If it is real, check if chapter is real. If it is real, check if the verse is real
        #if any of these are not real, than stop the process 
        #1. Check if the reference is real in the current translation
        bookId = None
        if not IsReferenceRealInTranslation(data, scriptureItems, translation, reference):
            temp = GetBookId(data, scriptureItems, translation)
            print(f"The book id of {scriptureItems[0]} is {temp}") #returns -1
            continue
        else:
            bookId = GetBookId(data, scriptureItems, translation)

        #2. insert into url
        apiData = CreateAPIVerse(translation, bookId, scriptureItems)

        #3. Grab the text from the url and clean it of html poison
        verse = RemoveHtmlTags(apiData['text'])

        #4. Create Scripture object and try to insert to JSON file
        newScripture = Scripture(reference, scriptureItems[0], scriptureItems[1], scriptureItems[2], verse, translation)
        myBool = InsertScripture(newScripture)

def FindScripture(reference: str, translation: str) -> Scripture:
    data = GetTranslationBookData()

    #format reference
    reference = CleanReference(reference)
    #parse input to grab book name, chapter num and verse num
    scriptureItems = SpliceScripture(reference)
    #format translation
    translation = translation.upper().strip()
    
    #check if the book is real. If it is real, check if chapter is real. If it is real, check if the verse is real
    #if any of these are not real, than stop the process 
    #1. Check if the reference is real in the current translation
    bookId = None
    if not IsReferenceRealInTranslation(data, scriptureItems, translation, reference):
        print("Scripture Not Real")
        return
    else:
        bookId = GetBookId(data, scriptureItems, translation)

    #2. insert into url
    apiData = CreateAPIVerse(translation, bookId, scriptureItems)

    #3. Grab the text from the url and clean it of html poison
    verse = RemoveHtmlTags(apiData['text'])

    #4. Create Scripture object and try to insert to JSON file
    newScripture = Scripture(reference, scriptureItems[0], scriptureItems[1], scriptureItems[2], verse, translation)
    return newScripture

def DeleteLoop():
    """This loop will allow the user to delete whatever scripture they want from their database.
    They will be able to delete only by inserting the correct reference
    """
    while True:
        reference = input("Reference to delete: ")

        if reference.lower().strip() == 'done':
            break

        reference = CleanReference(reference)

        #look through tinyDB and check if reference exist in it
        scripture = Query()
        if db.contains(scripture.reference == reference):
            #get id of reference - there should only be one
            removed_ids = db.remove(scripture.reference == reference)
            print(f"{removed_ids} has been removed")

def ListScripture():
    """Looks into database and list out all scripture in it
    """
    index = 1
    table = db.all()
    for item in table:
        print(f"{index}. {item['reference']} | {item['translation']} - {item['text']}\n\n")
        index += 1

def StringPercentageMatch(inputString: str, scriptureString: str) -> float:
    """We takes the users input of a string and match it to what we have in the database.
    We are checking how close they got to having the scripture written down perfectly

    Args:
        inputString (str): user's inputted string
        scriptureString (str): actual stricpture from the bible

    Returns:
        float: a float that represents the percentage of how close they were to writing down
        the scripture correctly
    """
    return SequenceMatcher(None, inputString, scriptureString).ratio()
    

def FormatFloatToPercentage(floatPercentage: float) -> str:
    """Formats a float into a percentage

    Args:
        floatPercentage (float): float version of percentage

    Returns:
        str: the float but as a percentage string representation of the float we input
    """
    return f"{floatPercentage:.2%}"


def GetRandomDBVerse() -> dict:
    """Retrieves a random item from the JSON library

    Returns:
        dict: JSON object that represents scripture
    """
    maxNum = db.__len__()
    randIndex = random.randint(1, maxNum)
    doc = db.get(doc_id=randIndex)
    return doc

def Quiz():
    #keep track of percentage from each question
    #10 question quiz? might not be 10 items to be tested on
    #continuous quiz until the user says they are done?
    #Timed quiz?
    #pick a percentage of items based on how many verses we have stored in DB - max amount of questions is 10 but can be less

    #just do 10 question quiz and if we have less than 10 verses, we can just quiz them on all the scripture they saved.
    #if they have more than 10 verses saved, we randomly pick 10 and store in a set so we dont have repeating ones

    #return a JSON dict that contains the scriptures that will be tested in, but they are not presented as a test
    scriptList = GetScriptureForQuiz()
    #make a list to hold accuracy of each question
    percentages = []
    #grab reference and request input for verse
    for scripture in scriptList:
        ref = scripture['reference']
        translation = scripture['translation']
        text = scripture['text']
        print(f"Write the scripture for verse {ref} | {translation}")
        answer = input("Input Verse: ")
        versePercentage = StringPercentageMatch(answer, text)
        print(f"You are {FormatFloatToPercentage(versePercentage)} correct!")
        percentages.append(versePercentage)
    #when done, give a grade
    grade = sum(percentages) / len(scriptList)
    grade = FormatFloatToPercentage(grade)
    return grade


def GetScriptureForQuiz() -> list[dict]:
    """Provides a list of the JSON scripture that will be used for a quiz

    Returns:
        list[dict]: A list that contains dictionaries that contain scripture information from
        our tinyDB
    """
    dbList = db.all()
    maxScriptureNum = len(db)
    intSet = set()
    if maxScriptureNum <= 10:
        #return all scripture
        print(f"Dont have 10 verses, outputting {maxScriptureNum} verses")
        return dbList
    else:
        print(f"we have more than 10 verses, creating random quiz list")
        #start selecting scripture - need a set
        quizNum = 10
        i = 0
        while i < quizNum:
            randInt = random.randint(0, maxScriptureNum-1)
            if randInt not in intSet:
                intSet.add(randInt)
                i += 1 #increment only when success

        #now we have indexes of scripture, let's add those JSON dicts into a list and return it
        quizList = []
        for num in intSet:
            quizList.append(dbList[num])

        return quizList

def SearchLoop():
    """Look up any verse in any translation and have it printed back out to them
    """
    data = GetTranslationBookData()
    while True:
        print("enter 'done' to end process")
        reference = input("Reference: ")

        if reference.lower().strip() == 'done':
            isOn = False
            break

        translation = input("Translation: ")

        #format reference
        reference = CleanReference(reference)
        #parse input to grab book name, chapter num and verse num
        scriptureItems = SpliceScripture(reference)
        #format translation
        translation = translation.upper().strip()
        
        #1. Check if the reference is real in the current translation
        bookId = None
        if not IsReferenceRealInTranslation(data, scriptureItems, translation, reference):
            continue
        else:
            bookId = GetBookId(data, scriptureItems, translation)

        #2. insert into url
        apiData = CreateAPIVerse(translation, bookId, scriptureItems)

        #3. Print out verse if it exists
        print(apiData['text'])




