from fastapi import FastAPI, HTTPException, status, Depends, Response
import logging
from pydantic import BaseModel
from typing import Optional, List
import base64
import requests
from src.data_engineer_ce.pubchem import ChemicalDataFetcher
from cachetools import LRUCache

app = FastAPI()

logging.basicConfig(filename="api.log", level=logging.INFO)
cache = LRUCache(maxsize=1000)

@app.get("/payload/", response_model=dict)
async def get_json_data(git_link: str="https://raw.githubusercontent.com/jwelchalbert/ishaan-albert-ce/main/formulas.json"):
    try:
        cached_data  = cache.get(git_link)
        if cached_data:
            logging.info("JSON data from cache")
            return {cached_data}
        response = requests.get(git_link)
        response.raise_for_status()
        json_data = response.json()
        cache[git_link] = json_data
        logging.info("JSON data processed")
        return{json_data}
    except Exception as e:
        logging.error(f"Error: {str(e)}")
        raise HTTPException(status_code=404, detail=f"Error")
    
# Define the PubChem API base URL
pubchem_base_url = "https://pubchem.ncbi.nlm.nih.gov/rest/pug"

@app.get("/get_compound")
# Function to fetch compound information by name
def get_compound(cid:int=2244):
    # Construct the API URL for name-based search
    url = f"{pubchem_base_url}/compound/cid/{cid}/JSON"

    # Make the API request
    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()
        return data
    else:
        return {"error": "Failed to fetch data from GitHub"}