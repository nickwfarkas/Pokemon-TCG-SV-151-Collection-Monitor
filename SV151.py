from CardCollection import *
import tkinter
from tkinter import filedialog

api_key = ''

def list_commands():
    print("""
          ls: list commands
          n: Owned/Oustanding counts
          mp: Market Price of collection and outstanding cards
          own: price breakdown of owned cards
          out: price breakdown of outstanding cards
          exp: export raw 151 data
          expout: export oustanding price breakdown
          expown: export own price breakdown\n\n""")

def command_router(cc: CardCollection, command: str):
    command = command.lower().strip()
    if(command == "ls"):
        list_commands()
        return 1
    if(command == "q"):
        return 1
    if(command == "n"):
        print(cc.get_n())
        return 1
    if(command == "mp"):
        print(cc.get_MP())
        return 1
    if(command == "own"):
        print(cc.get_owned_price_breakdown_df().to_string())
        return 1
    if(command == "out"):
        print(cc.get_outstanding_price_breakdown_df().to_string())
        return 1
    if(command == "exp"):
        print(cc.raw_to_csv())
        return 1
    if(command == "expout"):
        print(cc.outstanding_breakdown_to_csv())
        return 1
    if(command == "expown"):
        print(cc.owned_breakdown_to_csv())
        return 1

if(__name__ == "__main__"):

    tkinter.Tk().withdraw()
    print("Choose Collection File Location...")
    path_to_collection = filedialog.askopenfilename()
    print(f"{path_to_collection} chosen!")

    if(path_to_collection == ""):
        cc = CardCollection(api_key)
    else:
        cc = CardCollection(api_key,path_to_collection=path_to_collection)
    
    command = ''
    
    while(command != 'q'):
        command = input("\nInput Pokemon Collection Command\nls: list commands\nq: exit\n")
        command_router(cc,command)
