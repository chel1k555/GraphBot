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

    if response.status_code == 401 or (isinstance(data, dict) and data.get("detail") == "Invalid API Key"):
        raise RuntimeError(
            "Invalid LLM API key. Update lib/GptApiKey.txt with a valid key "
            "from https://intelligence.io.solutions and restart the server."
        )

    if not response.ok or "choices" not in data:
        detail = data.get("detail") if isinstance(data, dict) else None
        raise ValueError(f"LLM response format invalid (status={response.status_code}, detail={detail})")

    text = data['choices'][0]['message']['content']
    
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


ALLOWED_TYPES = {
    "line_chart", "bar_chart", "pie_chart",
    "histogram", "scatter_plot", "area_chart",
}


def validate_visualizations(data) -> list:
    """
    Приводит ответ LLM к формату:
    List[{
        "type": str,
        "why": str,
        "columns_used": list[str],
        "columns_used_with_text": list[str]
    }]
    """

    if data is None:
        raise ValueError("Empty LLM response")

    if isinstance(data, list):
        visualizations = data
    elif isinstance(data, dict):
        if "visualizations" in data:
            visualizations = data["visualizations"]
        elif "analysis" in data and isinstance(data["analysis"], dict) \
                and "visualizations" in data["analysis"]:
            visualizations = data["analysis"]["visualizations"]
        else:
            raise ValueError("Cannot find visualizations list in response")
    else:
        raise ValueError("Unexpected JSON structure")

    if not isinstance(visualizations, list):
        raise ValueError("Visualizations must be a list")

    required_keys = {"type", "why", "columns_used"}
    cleaned = []

    for i, item in enumerate(visualizations):

        if not isinstance(item, dict):
            raise ValueError(f"Visualization {i} is not an object")

        if not required_keys.issubset(item.keys()):
            raise ValueError(f"Visualization {i} missing required keys")

        if not isinstance(item["columns_used"], list):
            raise ValueError(f"Visualization {i} columns_used must be list")

        # совместимость со старой опечаткой "colums_used_with_text"
        text_cols = item.get("columns_used_with_text",
                             item.get("colums_used_with_text", []))
        if not isinstance(text_cols, list):
            text_cols = []

        if item["type"] not in ALLOWED_TYPES:
            # пропускаем заведомо некорректные типы вместо падения
            continue

        cleaned.append({
            "type": item["type"],
            "why": str(item["why"]).strip(),
            "columns_used": item["columns_used"],
            "columns_used_with_text": text_cols,
        })

    if not cleaned:
        raise ValueError("No valid visualizations in LLM response")

    return cleaned
