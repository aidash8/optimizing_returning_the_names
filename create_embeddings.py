# This program creates embeddings for data in csv file
# The code mostly is taken from OpenAi Cookbook: https://platform.openai.com/docs/guides/embeddings/what-are-embeddings
from typing import List
import argparse
import re
import pandas as pd
import asyncio
from openai import AsyncOpenAI

async def get_embedding(client: AsyncOpenAI, text: str, model: str="text-embedding-3-small") -> List[int]:
    try:
        emb = await client.embeddings.create(input = [text], model=model)
        return emb.data[0].embedding
    except Exception as e:
        print(f"Error: {type(e).__name__, e} for {text}")
        return []
    
async def get_embeddings_dataframe(
        client: AsyncOpenAI, 
        col_to_embed: str, 
        df: pd.DataFrame,
        model: str="text-embedding-3-small"
        ) -> pd.DataFrame:
    
    embeddings = await asyncio.gather(*[get_embedding(client, x[col_to_embed], model=model) for x in df.to_dict(orient='records')])

    return embeddings

async def create_embeddings_from_csv(
        client: AsyncOpenAI,
        filepath: str="data/ru_abbr_dictionary.csv", 
        col_to_embed: str="abbr",
        output_filepath: str="data/ru_abbr_dictionary_embedding.csv",
        ) -> None:

    # read data from csv
    df = pd.read_csv(filepath)
    df.drop(columns=['Unnamed: 0'], inplace=True)
    # filter out empty col_to_embed
    df = df.loc[df[col_to_embed].notnull()]
    df['embedding'] = await get_embeddings_dataframe(client, col_to_embed, df)
    df.to_csv(output_filepath)

def main(args) -> None:

    filepath = args.filepath
    if not re.search(r'\.csv$',filepath):
        filepath += '.csv'
    output_filepath = args.output_filepath
    if not re.search(r'\.csv$', output_filepath):
        output_filepath += '.csv'
    col_to_embed = args.col_to_embed 

    with open("secret.txt", "r") as file:
        OPENAI_KEY = re.sub(r'\s+','',file.read())

    # use these parameters to avoid rate limit errors    
    client = AsyncOpenAI(api_key=OPENAI_KEY, timeout=60, max_retries=3)
    asyncio.run(create_embeddings_from_csv(client, filepath, col_to_embed, output_filepath))

if __name__ == "__main__":
    parser = argparse.ArgumentParser(prog='Create embeddings to data stored in a csv file')
    parser.add_argument('filepath', help='The filename and path of the csv file with data')
    parser.add_argument('output_filepath', help='The filename and path of the output csv with embeddings')
    parser.add_argument('col_to_embed', help='The column name of data for embedding')
    args = parser.parse_args()
    main(args)