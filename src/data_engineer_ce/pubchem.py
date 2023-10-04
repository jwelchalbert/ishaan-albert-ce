from typing import Any, Dict
import aiohttp


class ChemicalDataFetcher:
    """
    A class used to fetch chemical data from the PubChem database.

    ...

    Attributes
    ----------
    BASE_URL : str
        a string representing the base URL of the PubChem database

    Methods
    -------
    fetch_data(cas_numbers: list[str]) -> list[Dict[str, Any]] | None:
        Fetches the chemical data for the given CAS numbers.
    cas_to_cid(session: aiohttp.ClientSession, cas: str) -> str | None:
        Converts a CAS number to a CID number.
    """

    BASE_URL: str = "https://pubchem.ncbi.nlm.nih.gov/rest/pug"

    def __init__(self) -> None:
        pass

    async def fetch_data(self, cas_numbers: list[str]) -> list[Dict[str, Any]] | None:
        """
        Fetches the chemical data for the given CAS numbers.

        Parameters
        ----------
        cas_numbers : list[str]
            A list of CAS numbers for which to fetch the chemical data.

        Returns
        -------
        list[Dict[str, Any]] | None
            A list of dictionaries containing the fetched chemical data, or None if no data could be fetched.
        """
        all_data = []
        async with aiohttp.ClientSession() as session:
            for cas in cas_numbers:
                cid = await self.cas_to_cid(session, cas)
                if cid:
                    data = await self.get_compound_data(session, cid)
                    if data is not None:
                        all_data.append(data)
                    else:
                        # TODO: Log this problem
                        pass
        return all_data

    async def cas_to_cid(self, session: aiohttp.ClientSession, cas: str) -> str | None:
        """
        Converts a CAS number to a CID number.

        Parameters
        ----------
        session : aiohttp.ClientSession
            The current aiohttp client session.
        cas : str
            The CAS number to convert.

        Returns
        -------
        str | None
            The corresponding CID number, or None if the conversion could not be performed.
        """
        url = f"{self.BASE_URL}/compound/name/{cas}/cids/JSON"
        async with session.get(url) as response:
            if response.status == 200:
                json_response = await response.json()
                cids = json_response.get("IdentifierList", {}).get("CID", [])
                return cids[0] if cids else None
            else:
                # TODO: Convert the following print statement into a proper Logging call
                # print(f"Error {response.status}: Unable to fetch CID for CAS {cas}")
                return None

    async def get_compound_data(
        self, session: aiohttp.ClientSession, cid: str
    ) -> Dict[str, Any] | None:
        """
        Gets the pubchem data associated with a given compound

        Parameters
        ----------
        session : aiohttp.ClientSession
            The current aiohttp client session.
        cid : str
            The CID number for the compound.

        Returns
        -------
        TODO: fill this out
        """
        # The API endpoint you should use is
        # TODO: You need to implement the async GET request for this
        # function.
        pass
