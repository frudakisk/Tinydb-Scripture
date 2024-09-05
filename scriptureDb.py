from tinydb import TinyDB, Query
import requests
import re

#add scripture into database
#make sure scripture does not already exist in the database before adding it
#give a flow of creating scripture untill user is done
#instead of mapping, try to use a class (DONE)

#I think I should be using a bible api so that the user does not have to write out the entire verse each time

#API needs translation, bookId, chapter number, and verse number
#I should allow people to input multiple verses such as John 3:16-18

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

s = Scripture("John 3:16", "John", 3, 16, "For God so loved the world, that he gave his only begotten Son, that whosoever believeth in him should not perish, but have everlasting life", "NIV")

#Insert scripture into the database
#make sure it is not already there
def InsertScripture(s: Scripture) -> bool:
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
    #expecting something like 'John 3:16'
    items = reference.split(' ')
    temp = items[1].split(":")
    items = [items[0], temp[0], temp[1]]
    return items

#Replaces <br> tags with newlines, and all other html tags with ''
def RemoveHtmlTags(text:str) -> str:
    clean = re.sub(r'<br.*?>', '\n', text)
    clean = re.sub(r'<.*?>', '', clean)
    return clean


isOn = True
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

    #Find books involved in users input translation - Request JSON from API
    translationsBook = "https://bolls.life/static/bolls/app/views/translations_books.json"
    response = requests.get(translationsBook)
    data = response.json()

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
    except:
        print("Translation does not exist")
        continue

    

    #2. insert into url
    url = f"https://bolls.life/get-verse/{translation}/{bookId}/{scriptureItems[1]}/{scriptureItems[2]}/"
    response = requests.get(url)
    apiData = response.json()
    print("data incoming!!!")
    print(apiData)

    #3. Grab the text from the url and clean it of html poison
    verse = RemoveHtmlTags(apiData['text'])
    print(verse)

    #4. Create Scripture object and try to insert to JSON file
    newScripture = Scripture(reference, scriptureItems[0], scriptureItems[1], scriptureItems[2], verse, translation)
    myBool = InsertScripture(newScripture)
