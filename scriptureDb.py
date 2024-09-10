from tinydb import TinyDB, Query
import requests
import re

#add scripture into database (DONE)
#make sure scripture does not already exist in the database before adding it (DONE)
#give a flow of creating scripture untill user is done (DONE)
#instead of mapping, try to use a class (DONE)

#I think I should be using a bible api so that the user does not have to write out the entire verse each time (DONE)

#API needs translation, bookId, chapter number, and verse number
#I should allow people to input multiple verses such as John 3:16-18

'''
TODO:
string percentage matching
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
    return clean

def CleanReference(reference: str) -> str:
    """Cleans the users reference by capatalizing the book name and
    removing any whitespace outside of the text

    Args:
        reference (str): the reference the user input

    Returns:
        str: a cleaned version of the reference that is capitilized and no extra whitespce
    """
    cleanedReference = reference.capitalize().strip()
    return cleanedReference

def CreateAPIVerse(translation: str, bookId: int, scriptureItems: list) -> dict:
    """_summary_

    Args:
        translation (str): _description_
        bookId (int): _description_
        scriptureItems (list): _description_

    Returns:
        dict: _description_
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
    """Given a book name, we get the book id in the current translation

    Args:
        data (dict): a JSON format dictonary that contains bible translations and books in that translation
        scriptureItems (list): A scripture reference split up by book name, chapter number, and verse number
        translation (str): translation user wants verse in

    Returns:
        int: the id of the book, or -1 if we cannot find the book
    """
    try:
        bookName = scriptureItems[0]
        for item in data[translation]: #we should be checking if this translation is even real FIRST
            if bookName == item['name']:
                return item['bookid']
        return -1
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
            continue
        else:
            bookId = GetBookId(data, scriptureItems, translation)

        #2. insert into url
        apiData = CreateAPIVerse(translation, bookId, scriptureItems)

        #3. Grab the text from the url and clean it of html poison
        verse = RemoveHtmlTags(apiData['text'])
        print(verse)

        #4. Create Scripture object and try to insert to JSON file
        newScripture = Scripture(reference, scriptureItems[0], scriptureItems[1], scriptureItems[2], verse, translation)
        myBool = InsertScripture(newScripture)

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
        print(f"{index}. {item["reference"]} - {item["text"]}\n\n")
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
    #Case 1, they are exactly the same
    if inputString == scriptureString:
        print("perfect match!")
        return 100.00
    
    correctCount = 0
    inputStringList = inputString.split()
    scriptureStringList = scriptureString.split()
    print(inputStringList)
    print(scriptureStringList)

    for word in inputStringList:
        if word in scriptureStringList:
            #if found, word is spelt 100% the same
            #check if it is in the correct spot, if it is, they got it correct
            inputIndex = inputStringList.index(word)
            scriptureIndex = scriptureStringList.index(word)
            if(inputIndex == scriptureIndex):
                print("word was exactly the same")
                correctCount += 1
            elif abs(inputIndex - scriptureIndex) <= 1:
                print("The word was within one space difference of its suppose to be space. giving half a point")
                correctCount += 0.5
        else: #if the word is not found, see if we can find a similar word - maybe they mispelled the word but it's still in correct spot
            #do loop for each word
            
            percentage = 0.00
            inputIndex = None
            scriptureIndex = None
            for scriptureWord in scriptureStringList:
                letterCorrect = 0
                print(f"word in this context is {word}")
                print(f"scripture word in this context is {scriptureWord}")
                for i in range(len(scriptureWord)):
                    #if word is bigger than scriptureWord, we need to doc off points per extra letter
                    try:
                        if word[i] == scriptureWord[i]:
                            print("MATCH")
                            letterCorrect += 1
                    except:
                        pass

                #find bigger word because we need to know if we are missing a letter in percentage calculation
                biggerWord = ""
                if len(word) >= len(scriptureWord):
                    biggerWord = word
                else:
                    biggerWord = scriptureWord


                tempPercentage = letterCorrect / len(biggerWord) #length of the bigger word
                print(f"tempPercentage: {tempPercentage}")
                #if this percentage is higher than what we already have, grab the index of each word in their list
                if tempPercentage > percentage:
                    percentage = tempPercentage
                    inputIndex = inputStringList.index(word)
                    scriptureIndex = scriptureStringList.index(scriptureWord)
                    print(f"Percentage has been changed to {tempPercentage}")
                    #if they are at the same index, that is better than if they are not
                    
            #after finding the highest percetnage, see what their index is like
            if(inputIndex == scriptureIndex):
                correctCount += (percentage) #percent is always 1.0 or lower, so use this as how right we got the word in the correct place
            elif abs(inputIndex - scriptureIndex) <= 1:
                #if we are within one distance of where the word is suppose to be, give them half a point on top of how well they spelt the word
                correctCount += 0.5 * percentage
    
    #now calculate overall percentage
    percentage = correctCount / len(scriptureStringList)
    print(f"percentage in decimal form: {percentage}\n correctCount: {correctCount}")
    return percentage


def FormatFloatToPercentage(floatPercentage: float) -> str:
    """Formats a float into a percentage

    Args:
        floatPercentage (float): float version of percentage

    Returns:
        str: the float but as a percentage string representation of the float we input
    """
    return f"{floatPercentage:.2%}"



#I want to quiz myself by being given the reference and I have to type out the verse. However, i want to account for slight errors
#I want to have a percentage accuracy of how close i was to the original scripture

def main():
    """Main function that is to be run as the program. Should be clean.
    """
    while(True):
        answer = input("What would you like to do? ")
        answer = answer.lower().strip()

        match answer:
            case 'done':
                break
            case 'add':
                AddLoop()
            case 'delete':
                DeleteLoop()
            case 'quiz':
                StringPercentageMatch("Hello There  Stinky World!", "Hello World!") #83.3%
            case 'list':
                ListScripture()
            case _:
                print("not real answer")

if __name__ == "__main__":
    main()




