from fastapi import FastAPI, HTTPException
import httpx
import logging
from typing import Any, Dict, List, Union
from pydantic import BaseModel

# Logging Configuration
logging.basicConfig(filename="api.log", level=logging.INFO)

# FastAPI App initialization
app = FastAPI()

# Define the PubChem API base URL
PUBCHEM_BASE_URL = "https://pubchem.ncbi.nlm.nih.gov/rest/pug"

# Pydantic Model for Compound
class Compound(BaseModel):
    cas: str
    conc: float

# Utility Functions
async def fetch_data(url: str) -> Union[Dict[str, Any], List[Any]]:
    """
    Asynchronously fetch data from a given URL and return it as JSON.

    Args:
    url (str): The URL to fetch data from.

    Returns:
    Union[Dict[str, Any], List[Any]]: The fetched data as JSON.
    """
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
        response.raise_for_status()
        return response.json()

async def get_chemical_data(cid: int) -> Dict[str, Any]:
    """
    Get various chemical properties for a given PubChem CID.

    Args:
    cid (int): The CID to fetch data for.

    Returns:
    Dict[str, Any]: The fetched chemical data as JSON, or an error message.
    """
    url = f"{PUBCHEM_BASE_URL}/compound/cid/{cid}/property/CanonicalSMILES,IsomericSMILES,TPSA,MolecularWeight,XLogP,HBondAcceptorCount,Complexity/JSON"
    try:
        data = await fetch_data(url)
        logging.info(f"Chemical data fetched for CID {cid}: {data}")  
        return data
    except httpx.HTTPStatusError as e:
        logging.error(f"Failed to fetch chemical data for CID {cid}: {str(e)}")
        return {"error": f"Failed to fetch chemical data for CID {cid}"}

@app.get("/get_cid/{cas}")
async def get_cid(cas: str) -> Dict[str, Any]:
    """
    Get the PubChem CID using a CAS#.

    Args:
    cas (str): The CAS# to convert to a CID.

    Returns:
    Dict[str, Any]: The fetched data as JSON, or an error message.
    """
    url = f"{PUBCHEM_BASE_URL}/compound/name/{cas}/cids/JSON"
    try:
        data = await fetch_data(url)
        logging.info(f"CID fetched for CAS {cas}: {data}")  
        return data
    except httpx.HTTPStatusError as e:
        logging.error(f"Failed to fetch CID for CAS {cas}: {str(e)}")
        return {"error": f"Failed to fetch CID for CAS {cas}"}

@app.get("/get_compound/{cid}")
async def get_compound(cid: int) -> Dict[str, Any]:
    """
    Get compound data using a PubChem CID.

    Args:
    cid (int): The CID to fetch data for.

    Returns:
    Dict[str, Any]: The fetched data as JSON, or an error message.
    """
    url = f"{PUBCHEM_BASE_URL}/compound/cid/{cid}/JSON"
    try:
        data = await fetch_data(url)
        logging.info(f"Data fetched for CID {cid}: {data}")  
        return data
    except httpx.HTTPStatusError as e:
        logging.error(f"Failed to fetch data from PubChem for CID {cid}: {str(e)}")
        return {"error": f"Failed to fetch data from PubChem for CID {cid}"}

@app.get("/payload_summary/")
async def get_json_data_summary(git_link: str = "https://raw.githubusercontent.com/jwelchalbert/ishaan-albert-ce/main/formulas.json") -> Dict[str, Union[Dict[str, int], List[Any]]]:
    """
    Get a summary and preview of the JSON data from a given Git link.

    Args:
    git_link (str): The Git link to fetch data from.

    Returns:
    Dict[str, Union[Dict[str, int], List[Any]]]: A summary and preview of the fetched data.
    """
    try:
        json_data = await fetch_data(git_link)
        logging.info("JSON data processed")
        
        summary = {"total_items": len(json_data)}
        preview_items = json_data[:5]  # Adjust as needed
        
        return {"summary": summary, "preview": preview_items}
    except Exception as e:
        logging.error(f"Error: {str(e)}")
        raise HTTPException(status_code=404, detail=f"Error : {str(e)}")
    
@app.post("/augment_payload/")
async def augment_payload(compounds: List[Compound]) -> List[Dict[str, Any]]:
    """
    Augment the payload with chemical data from PubChem and normalize concentrations. Provide a compound with their CAS number and concentration. 
    The API will return a list of compounds with the following additional information for each: SMILES string, Polar Surface Area, Molecular Weight, Log P, Hydrogen Bond Acceptor, 
    and Compound Complexity. You can provide a single compound to get its relevant information
    
    Example input: 
    
    [
    {
        "cas": "20963-87-5",
        "conc": 57.71
    }
]

    Args:
    compounds (List[Compound]): List of compounds to be augmented.

    Returns:
    List[Dict[str, Any]]: Augmented data.
    """
    try:  
        # Normalize concentrations
        total_conc = sum(compound.conc for compound in compounds)
        for compound in compounds:
            compound.conc = (compound.conc / total_conc) * 100
        
        augmented_data = []
        
        for compound in compounds:
            # Convert CAS to CID
            try:
                cid_data = await fetch_data(f"{PUBCHEM_BASE_URL}/compound/name/{compound.cas}/cids/JSON")
                cid = cid_data.get('IdentifierList', {}).get('CID', [None])[0]
            except httpx.HTTPStatusError as e:
                logging.warning(f"No CID found for CAS {compound.cas}. Error: {str(e)}")
                continue  # Skip to the next compound if this one fails
            
            # Fetch chemical data
            chemical_data = await get_chemical_data(cid)
            properties = chemical_data.get('PropertyTable', {}).get('Properties', [{}])[0]
            
            # Augment payload
            augmented_data.append({
                "cas": compound.cas,
                "conc": compound.conc,
                "smiles": properties.get('CanonicalSMILES') or properties.get('IsomericSMILES'),
                "polarSurfaceArea": properties.get('TPSA'),
                "molecularWeight": properties.get('MolecularWeight'),
                "logP": properties.get('XLogP'),
                "hydrogenBondAcceptor": properties.get('HBondAcceptorCount'),
                "compoundComplexity": properties.get('Complexity')
            })
            
            # Log if any property is missing
            for prop, value in augmented_data[-1].items():
                if value is None:
                    logging.warning(f"Missing {prop} for CAS {compound.cas}")
        
        return augmented_data
    
    except Exception as e:
        logging.error(f"An error occurred: {str(e)}", exc_info=True)  
        raise HTTPException(status_code=500, detail="Internal Server Error")  
