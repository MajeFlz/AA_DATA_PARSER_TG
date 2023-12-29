import re
import os
from dateutil import parser
import pandas as pd

async def analyse_interests(file_path, keywords):


    Trymessages = []
    print(keywords)   
    with open(file_path, "r", encoding="utf-8") as file:
        messages = file.read().split("---MESSAGE_SEPARATOR---")
    
        for msg in messages:
            # Search for keywords in the message
            if any(key in msg for key in keywords):
                Trymessages.append(msg)


        return Trymessages 

