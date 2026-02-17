import requests
from pprint import pprint
from LLMRequests import headers, globalUrl

def getModelsList() -> None:
    urlModels = globalUrl + "/models"
    response = requests.get(urlModels, headers)
    data = response.json()
    pprint(data)

    for d in (data["data"]):
        name = d['id']
        print(name)


if __name__ == "__main__":
    getModelsList()