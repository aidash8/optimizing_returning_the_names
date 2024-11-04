# Prepare reference dictionariet
from typing import List, Tuple
import argparse
import re
from pypdf import PdfReader
import pandas as pd

def manual_cleaning_abbr(page_idx: int, page_text: str) -> str:

    if page_idx == 0:
        page_text = re.sub(r'Автономная Советская Оо\n\s+циалистическая Республика', 'Автономная Советская Социалистическая Республика', page_text)  
    elif page_idx == 3:
        page_text = page_text.replace(';\nа. д. ', ';\nа. д. --')
        page_text = page_text.replace('авиационная  зажигательная  бомба;\n', 'авиационная  зажигательная  бомба,') 
    elif page_idx == 5:
        page_text = page_text.replace('и т. д.\nал ','и т. д.;\nал ')
    elif page_idx == 7:
        page_text = page_text.replace('ев:\nАРС —','ев;\nАРС —') 
    return page_text

# Some abbreviations were read without separation between abbr and its meaning
def add_long_dash_after_abbr(page_text: str) -> str:
    # fix it at the beginning of the page
    matches = re.findall(r'^\s*([\w\.]+(\s\(?\w+\)?)?\s{8,})-?\s*-?\s*[\w■\"\']+', page_text)
    for m in matches:
        page_text = page_text.replace(m[0], m[0] + '--') 
    # fix it at the rest of the page
    matches = re.findall(r';\n+\s*([\w\.]+(\s\(?\w+\)?)?\s{8,})-?\s*-?\s*[\w■\"\']+', page_text)
    for m in matches:
        page_text = page_text.replace(m[0], m[0] + '--')
    return page_text

# Cleans majority, but needs more cleaning (pg 209)
def read_abbr(filename: str) -> List[Tuple[str]]:
   
    reader = PdfReader(filename)
    
    start_abbr_pg, end_abbr_pg = 9, 299
    abbreviations_li = []
    for i,page in enumerate(reader.pages[start_abbr_pg:end_abbr_pg]): # abbreviations are from page 9 till 299
        page_text = page.extract_text(extraction_mode='layout').strip()
        # manual cleaning
        page_text = manual_cleaning_abbr(i, page_text)
        # rule-base cleaning
        page_text_clean = re.sub(r'\n+\s*\-*»*\d+\.?\,?\s*\**\s*\d*\n*$', '\n', page_text) # replaces the page number at the end of the page with new line
        page_text_clean = re.sub(r'^\n*\s*\w\s*\n+', '', page_text_clean) # removes the letter at the begining of the page
        page_text_clean = re.sub(r'—([\(\)\.\,\s\w]+):?\n([\(\)\s\w]+)—', r'— \1;\n\2 —',page_text_clean) # separates 2 abbreviations into 2 lines
        page_text_clean = add_long_dash_after_abbr(page_text_clean) # adds long dash after abbreviations as they are missing
        page_text_clean = re.sub(r"\n{2,}", "\n",page_text_clean) # removes double new line
        page_text_clean = re.sub(r"\xad\n*\s*", "",page_text_clean) # stiches meaning of abbreviation to one line
        page_text_clean = re.sub(r"\,\n\s*", ", ",page_text_clean) # stiches meaning of abbreviations to one line
        page_text_clean = re.sub(r"\-\n\s*", "",page_text_clean) # stiches meaning of abbreviations to one line
        page_text_clean = re.sub('—+', '::', page_text_clean) # long dash (one or more) is abbr separation with its meaning
        page_text_clean = re.sub('-{2,}', '::', page_text_clean) # short two or more dashes is abbr separation with its meaning
        page_text_clean = re.sub(r"[^\w\-\n\.\(\)\,:;]", " ",page_text_clean) # leaves only needed characters
        page_text_clean = re.sub(r' +', ' ',page_text_clean) # removes extra spaces
        page_text_clean = re.sub(r'^[ \s]+', '',page_text_clean) # removes space at the beg of line
    
        for line in page_text_clean.split(';\n'):
            if line.strip():
                line = line.strip()
                abbr, sep, meaning = line.partition('::')
                meaning = re.sub(r'\n\s+', ' ',meaning.strip()) # removes extra spaces
                abbreviations_li.append((abbr.strip(), meaning))
  
    return abbreviations_li 

def read_abbr_as_dataframe(filename: str) -> pd.DataFrame:  
    abbr_li = read_abbr(filename)
  
    return pd.DataFrame(abbr_li, columns=['abbr', 'meaning'])

def create_abbr_dictionary_csv(input_pdf_name: str, output_csv_name: str) -> None:
    abbreviations_df = read_abbr_as_dataframe(input_pdf_name)
    abbreviations_df.to_csv(output_csv_name)

def main(args) -> None:
    input_pdf_name = args.input_pdf_name
    if not re.search(r'\.pdf$',input_pdf_name):
        input_pdf_name += '.pdf'
    output_csv_name = args.output_csv_name
    if not re.search(r'\.csv$', output_csv_name):
        output_csv_name += '.csv'
    create_abbr_dictionary_csv(input_pdf_name, output_csv_name)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(prog='Create Russian abbreviation dictionary of 1953 year as csv file')
    parser.add_argument('input_pdf_name', help='The location and name of the abbreviation dictionary pdf')
    parser.add_argument('output_csv_name', help='The location and name of the output csv')
    args = parser.parse_args()
    main(args)