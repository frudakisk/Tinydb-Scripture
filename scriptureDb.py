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
Check if the book is real
Check if the chapter number is real
Check if the verse number is real
Check if the translation is real
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
        db.insert(s.__dict__)
        return True
    else:
        print("this scripture already exist in our database")
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
    items = [items[0], temp[0], temp[1]]
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
    #check if the book name is even a real one within the translation
    bookName = scriptureItems[0]

    for item in data[translation]: #we should be checking if this translation is even real FIRST
        if bookName == item['name']:
            return True
        
    return False


def IsChapterReal(data: dict, scriptureItems: list, translation: str) -> bool:
    """Checks if the chapter number of the scripture reference is a real chapter

    Args:
        data (dict): a JSON format dictonary that contains bible translations and books in that translation
        scriptureItems (list): A scripture reference split up by book name, chapter number, and verse number
        translation (str): translation user wants verse in

    Returns:
        bool: returns True if chapter is real, false otherwise
    """
    bookName = scriptureItems[0]
    chapterNumber = int(scriptureItems[1])

    for item in data[translation]:
        if bookName == item['name']:
            maxChapters = item['chapters']
            if chapterNumber <= maxChapters:
                return True
    
    return False


def IsVerseReal(scriptureItems: list, translation: str) -> bool:
    url = f"https://bolls.life/get-text/{translation}/{bookId}/{scriptureItems[1]}/"




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
    reference = reference.capitalize().strip()
    #parse input to grab book name, chapter num and verse num
    scriptureItems = SpliceScripture(reference)
    #format translation
    translation = translation.upper().strip()

    print("Checking Chapter\n")
    print(IsChapterReal(data, scriptureItems, translation))

        #check if reference is even real by book, chapter, verse in that order
    if IsBookReal(scriptureItems, translation) and IsChapterReal(bookName) and IsVerseReal():
        pass

    booksInTranslation = None
    bookId = None
    #1. convert book name to bookid - Need translation first
    try:
        booksInTranslation = data[translation] #check if translation is a real one
        #find bookid in this translation
        for item in booksInTranslation:
            if(item['name'] == scriptureItems[0]):
                print(item)
                bookId = item['bookid']
                print(f"bookId is {bookId}")

        if bookId == None:
            raise Exception(f"Could not find book {scriptureItems[0]} in current {translation} translation")
    except Exception as ex:
        print(f"Translation does not exist: {ex}")
        continue

    

    #2. insert into url
    apiData = CreateAPIVerse(translation, bookId, scriptureItems)

    #3. Grab the text from the url and clean it of html poison
    verse = RemoveHtmlTags(apiData['text'])
    print(verse)

    #4. Create Scripture object and try to insert to JSON file
    newScripture = Scripture(reference, scriptureItems[0], scriptureItems[1], scriptureItems[2], verse, translation)
    myBool = InsertScripture(newScripture)


