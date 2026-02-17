import requests
from pprint import pprint
import json
import re


globalUrl = "https://api.intelligence.io.solutions/api/v1"
url = globalUrl + "/chat/completions"
headers = {
    "accept": "application/json",
    "Authorization": f"Bearer {open("lib/GptApiKey.txt", "r").readline()}"
}
models = ["deepseek-ai/DeepSeek-V3.2", "deepseek-ai/DeepSeek-R1-0528"]


def GetLLMResponse(userPrompt: str, systemPrompt: str, debugMessages: bool = False) -> list:

    data = {
        "model": models[0],
        "messages": [
            {
                "role": "system", "content": systemPrompt
            },
            {
                "role": "user", "content": userPrompt
            },
        ],
        "response_format": {"type": "json_object"}
    }

    response = requests.post(url, headers=headers, json=data)
    data = response.json()

    if (debugMessages):
        print("==== Raw Data ====")
        pprint(data)
    
    try:
        text = data['choices'][0]['message']['content']
    except KeyError:
        raise ValueError("LLM response format invalid")
    
    if (debugMessages):
        print("==== Raw LLM Text ====")
        print(text)

    parsed_json = json.loads(text)

    if (debugMessages):
        print("==== Parsed JSON ====")
        pprint(parsed_json)

    validated = validate_visualizations(parsed_json)

    if (debugMessages):
        print("==== Validated Visualizations ====")
        pprint(validated)

    return validated


def validate_visualizations(data) -> list:
    """
    Приводит ответ LLM к формату:
    List[{
        "type": str,
        "why": str,
        "columns_used": list[str]
    }]
    """

    if data is None:
        raise ValueError("Empty LLM response")

    # Если уже список - ок
    if isinstance(data, list):
        visualizations = data

    # Если словарь, то ищем в нем нужный список
    elif isinstance(data, dict):

        # вариант: {"visualizations": [...]}
        if "visualizations" in data:
            visualizations = data["visualizations"]

        # вариант: {"analysis": {"visualizations": [...]}}
        elif "analysis" in data and isinstance(data["analysis"], dict):
            if "visualizations" in data["analysis"]:
                visualizations = data["analysis"]["visualizations"]
            else:
                raise ValueError("No 'visualizations' inside 'analysis'")

        else:
            raise ValueError("Cannot find visualizations list in response")

    else:
        raise ValueError("Unexpected JSON structure")

    # Проверка что это список
    if not isinstance(visualizations, list):
        raise ValueError("Visualizations must be a list")

    # Валидация структуры каждого элемента
    required_keys = {"type", "why", "columns_used"}

    for i, item in enumerate(visualizations):

        if not isinstance(item, dict):
            raise ValueError(f"Visualization {i} is not an object")

        if not required_keys.issubset(item.keys()):
            raise ValueError(f"Visualization {i} missing required keys")

        if not isinstance(item["columns_used"], list):
            raise ValueError(f"Visualization {i} columns_used must be list")

    return visualizations
