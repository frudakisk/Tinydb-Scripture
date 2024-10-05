from scriptureDb import *

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
                grade = Quiz()
                print(f"Grade: {grade}")
            case 'list':
                ListScripture()
            case 'search':
                SearchLoop()
            case _:
                print("not real answer")

if __name__ == "__main__":
    main()
