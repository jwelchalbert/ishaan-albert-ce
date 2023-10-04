# Albert Invent - Data Engineering Take Home 

Welcome to the albert invent data engineering take home project. This project is designed to demonstrate your development skills in a task that is typical in an Albert data pipeline/workflow. The project should take no longer than 4 hours to complete and your submission needs to be pushed to the git repository on a new branch with your name by the end of the four hour period.

As a first step please clone this repository and read through this README for a description of the project task -- if you have any questions, please reach out to jonathan@albertinvent.com as soon as possible with your question.

## Description of the Project
We often deal with formulation data and will need to pull data from different data APIs and aggregated together into a composite description of the formula. For example often a formula is specified in the form of a set of [CAS#](https://en.wikipedia.org/wiki/CAS_Registry_Number) and a concentration values (each representing a different chemical component of the formula). Sometimes the concentrations are given in a 'by parts' form which has ratios which are correct, but it is not normalized (we will need to fix this as part of the data pipeline (see below for more details)). In addition, the CAS# itself contains no chemical information (CAS#'s are like social security numbers for chemicals, they are given out in sequential order on a first come first serve basis -- nothing about the CAS# tells us what the chemistry or physical properties of the compound are). For modeling purposes we would therefore like to convert the formula information into things that are more useful for modeling.

NOTE: The example dataset `formulas.json` is representative of real world data -- and all that entails. Scientists are not perfect when it comes to entering data, but the result of your application needs to deal with potential scientist errors.

You can make the following assumptions 
- All CAS numbers are correct as they are pulled from a database of known raw materials -- if when looking up data about a cas number you come up short, this is not an error in the CAS it is simply an indication that the pubchem service (see below) does not have data on it.
- All `conc` are intended to be real valued floating point numbers -- if it is impossible to determine the intent then you may assume the concentration is zero and eliminate it from the formula - but this should be a last resort -- make sure you keep track of when this happens.

Your task is to build a small API service which accepts JSON payloads of raw formulas which will have a structure like the following:

```json
[
    {
        "cas": "20963-87-5",
        "conc": 57.71
    },
    {
        "cas": "1303-11-3",
        "conc": 36.88
    },
    {
        "cas": "15283-45-1",
        "conc": 34.56
    },
    {
        "cas": "13768-60-0",
        "conc": 23.8
    },
    {
        "cas": "37382-15-3",
        "conc": 9.55
    },
    {
        "cas": "12408-33-2",
        "conc": 35.42
    },
]
```

and it will return payloads which have been augmented with chemical data which you will retrieve from pubchem (a publicly available chemical database) and the formula concentrations (the `conc` field) will be normalized such that when you add up all the formula values they add up to 100. 

For each component in the formula you will attempt to find the following information about it:
- `SMILES` String - this is a chemical formula string that may look like `"C(C(C(=O)[O-])O)(C(=O)[O-])O.[Ag+].[Ag+]"` -- Some compounds may have multiple SMILES strings, the order of importance should be 'Canonical' then 'Isometric' then whatever else if those two are not available. Only include a single SMILES string per CAS
- `Polar Surface Area` - This is a numerical value that describes the surface area of a molecule which is polar
- `Molecular Weight` - This is a measure of the total molecular weight of theh compound
- `Log P` - the partition coeffcient of the compound between n-octanol and water -- it is a measure of the molecule's lipophilicity
- `Hydrogen Bond Acceptor` - the number of hydrogen bond acceptor sites 
- `Compound Complexity` - A numerical representation of the structural complexity of the molecule

If in the event that one of these properties is not available for a particular compound (or if the compound itself is not available on pubchem) then you should log these instances in a file somewhere that is easy to parse later.

Your application should accept as a POST operation, a JSON payload like above and return a JSON payload which has the augmented data on it, e.g. (here is an example for caffeine in a formula where its concentration after normalizing the formula is 24.12) 

```json
    {
        "cas": "58-08-2",
        "conc": 24.12,
        "smiles": "CN1C=NC2=C1C(=O)N(C(=O)N2C)C",
        "polarSurfaceArea": 58.4,
        "molecularWeight": 194.19,
        "logP": -0.1,
        "hydrogenBondAcceptor": 3,
        "compoundComplexity": 293
    },
```

# Submitting your work 
Once you have completed your development - you will push the code to a branch other than `main` -- read that twice -- do not push to main -- instead push to a branch with your name as the branch name -- after you have pushed your final commit open a pull request into main for a code review. 

# Development Notes
Below are some general development notes - please read through everything carefully before you begin. 

## Expected Coding standards
- If you use python you **MUST** use type hints wherever possible. This means when declaring member variables of a class, defining function argument lists, and including function return types. If you use an SDK which makes it impossible to determine a concrete type for something you are using then make a note in a comment near the definition of the variable or the function to indicate that the library you are using is written poorly and hence you are forced to use the 'Any' type in place of a concrete type :). 
- If you use python edit the `pyproject.toml` file to add any additional requirements that are needed to run your application. Do not just include a dangling `requirements.txt` file, take the time to build a proper python package around your application.
- Regardless of the language you use, make sure to comment your code when appropriate -- document your functions with proper doc strings
- Do not leave unused imports in your code 

## Logging in your application
Logs are extremely important in any data engineering application -- when building your application please make sure to log any important steps, that includes successes, failures, or anything else that you think would be important to debugging a process like this.

## Pubchem
Pubchem does not take in CAS#'s directly, it uses an internal CID system which you must use -- so you will need to convert a CAS# to a pubchem CID before running a query on the compound. 

The pubchem API is a REST API the details of which you can find at [this link](https://pubchem.ncbi.nlm.nih.gov/docs/pug-rest). 

The API can be accessed through the following base URL `https://pubchem.ncbi.nlm.nih.gov/rest/pug`

The two endpoints that you will need to use for this project are 

`/compound/name/{cas}/cids/JSON`
which will help you convert CAS#'s into CIDS
and 
`/compound/cid/{cid}/JSON`
which will return to you any data that is available for that CID

### Caffeine Example
An example Pubchem result can be found for the Caffeine molecule here 
https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/cid/2519/JSON 
Note that the payload structure is largely consistent across all compounds.

## Async API Operation
Your API should be fully asynchronous -- that is to say, you need to use `async`/`await` style keywords in your code (if your language of choice supports it) or `go` routines if you are using golang, etc... -- if your language does not support async calls then choose another language for this exercise. 

For example, if your language is python then a function which implements an asynchronous GET call to convert a CAS# into a pubchem CID might look like the following (we are using `aiohttp` here but you can use whatever library you want so long as it supports async operation):

```python
import aiohttp
import asyncio

class ChemicalDataFetcher:
    BASE_URL = "https://pubchem.ncbi.nlm.nih.gov/rest/pug"

    async def cas_to_cid(self, cas: str):
        url = f"{self.BASE_URL}/compound/name/{cas}/cids/JSON"

        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status == 200:
                    json_response = await response.json()
                    cids = json_response.get('IdentifierList', {}).get('CID', [])
                    return cids[0] if cids else None
                else:
                    # TODO: Log that something went wrong here...
                    return None

```


## Caching Results
When building out your application try to reduce the number of API calls that you need to make to increase the throughput of your application. Several formulas in the example dataset may contain the same CAS compounds used in different concentrations. You should implement some kind of caching mechanism in your application to avoid making repeat calls to pubchem where possible.

# Testing your application 
You can use `curl`, a script, postman, etc... to test your application and demonstrate that it is working as that is the goal of the exercise -- ideally though you would load in the `formulas.json` file that is in this repo (your data source) in a seperate script/application and have that application send multiple requests in parallel to your application to see how it handles multiple requests coming in at the same time. 

## Bonus Points
- Benchmark your application - determine the processing rate measured in formulas/sec
- As part of your caching mechanism, keep track of how many times each compound is used and implement a `/stats` endpoint which will return high level stats about each compound that the service has seen
- Add in additional properties for each compound using something like `rdkit` to compute one or two extra molecular descriptors

## Skeleton Code 
Included in this repo is some skeleton code that you are welcome to use if you are using python as your language. It includes a basic wrapper around the pubchem API, but it is not complete it only implements the above cas to cid function. If you use it you should extend this class to do whatever it needs to do to get the data you are after. 



