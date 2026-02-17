import pandas as pd
from typing import Dict, Any

def userPrompt(profile: Dict[str, Any], sample_rows: pd.DataFrame) -> str:
    
    
    prompt = f"""

    Ниже описание датасета:

    Общая информация:
    - Количество строк: {profile["n_rows"]}
    - Количество колонок: {profile["n_columns"]}

    Колонки:
    """

    for col in profile["columns"]:
        prompt += f"""
            - {col["name"]}
            тип: {col["type"]}
            пропуски: {col["missing_values"]}
            уникальных значений: {col["unique_values"]}
        """

        if "stats" in col:
            stats = col["stats"]
            prompt += f"""  статистика:
                - min: {stats["min"]}
                - max: {stats["max"]}
                - mean: {stats["mean"]}
                - std: {stats["std"]}
            """

    prompt += f"""

    Пример первых строк данных:
    {sample_rows.to_markdown(index=False)}

    """
    return prompt


def systemPrompt() -> str:
    prompt = """Ты — эксперт по аналитике данных и визуализации. Тебе поступает описание датасета.
                    Задача:
                    1. Проанализируй структуру данных
                    2. Предложи 5 наиболее подходящих типов визуализации
                    3. Используй универсальные названия визуализации:
                    - line_chart
                    - bar_chart
                    - stacked_bar_chart
                    - pie_chart
                    - histogram
                    - boxplot
                    - scatter_plot
                    - heatmap
                    - area_chart
                    - bubble_chart

                    Верни строго JSON в формате:
                    List[
                    {{
                        "type": "Универсальное название визуализации, например line_chart",
                        "why": "почему подходит",
                        "columns_used": ["col1", "col2"]
                    }}
                    ]

                    НЕ МЕНЯЙ ФОРМАТ JSON,
                    Никакого текста вне JSON.
                """
    return prompt