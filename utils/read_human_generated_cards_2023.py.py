from typing import List, Tuple
import os
import re
from pypdf import PdfReader
import pandas as pd

# Define the folder containing the PDF files
folder_path = 'data/clean_data'  # Change this to your folder path

def read_human_generated_cards_2023(dirname: str) -> List[Tuple[str]]:
    
    data = []
    for filename in os.listdir(dirname):
        if filename.endswith('.pdf'):
            print("--------------------")
            print(filename)
            file_path = os.path.join(dirname, filename)
            reader = PdfReader(file_path)
            for i,page in enumerate(reader.pages):
                text = page.extract_text(extraction_mode="layout",layout_mode_space_vertically=False)
                # print(repr(text))
                if text:
                    lines = text.splitlines()
                    name = re.sub(r'\s+',' ',lines[0])
                    age = re.sub(r'\s+',' ',lines[1])
                    # doesn't extract space after age (number)
                    age = re.sub(r"(\d+)([А-Я]+)",r"\1 \2", age)
                    birth_info = re.sub(r'\s+',' ',lines[2])
                    occupation = re.sub(r'\s+',' ',lines[3])
                    if len(lines) > 6: # need to stitch
                        occupation += ' ' + re.sub(r'\s+',' ',lines[4])
                    death_info = re.sub(r'\s+',' ',lines[-2])
                    # doesn't extract space after number
                    death_info = re.sub(r"(\d+)([А-Я]+)",r"\1 \2", death_info)
                    # print(repr(death_info))
                    id = lines[-1].strip()
                    if id.isnumeric(): # only get the cards with id
                        data.append((filename,i,id,name,age,birth_info,occupation,death_info,text))
    return data

def output_human_generated_cards_as_csv(dirname: str='data/human_generated_cards', output_filename: str='data/human_generated_cards_2023.csv') -> None:
    
    data = read_human_generated_cards_2023(dirname)
    df = pd.DataFrame(data)
    df.columns = ['filename', 'page_num', 'id', 'name', 'age', 'birth_info', 'occupation', 'death_info','card']
    df.to_csv(output_filename, index=False)

output_human_generated_cards_as_csv()