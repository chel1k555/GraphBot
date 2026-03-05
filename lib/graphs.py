import pandas as pd
import matplotlib.pyplot as plt
from openpyxl import Workbook
from openpyxl.chart import BarChart, LineChart, Reference, AreaChart, PieChart
from openpyxl.drawing.image import Image as ExcelImage
from openpyxl.utils.dataframe import dataframe_to_rows
from openpyxl.utils import get_column_letter
import io
import os
import json



def generate_chart(file_path: str, chart_config: list):
    df = pd.read_excel(file_path)

    chart_type = chart_config["type"]
    columns = chart_config["columns_used"]

    # Создание Workbook и листа
    wb = Workbook()
    ws = wb.active
    ws.title = "Chart"
    
    # Добавление данных в лист
    for r in dataframe_to_rows(df, index=False, header=True):
        ws.append(r)

    row_count = len(df)
    
    # Создание графика openpyxl
    chart = None
    if chart_type == "bar_chart":
        chart = BarChart()
        chart.title = "Bar Chart"
    elif chart_type == "line_chart":
        chart = LineChart()
        chart.title = "Line Chart"
    elif chart_type == "pie_chart":
        chart = PieChart()
        chart.title = "Pie Chart"
    elif chart_type == "histogram":
        chart = BarChart()
        chart.type = "col"
        chart.title = "Histogram"
    elif chart_type == "area_chart":
        chart = AreaChart()
        chart.title = "Area Chart"
    elif chart_type == "scatter_plot":
        chart = LineChart()
        chart.style = 13
        chart.title = "Scatter Plot"
    
    # Добавление данных в график
    if chart:
        data = Reference(ws, min_col=2, min_row=1, max_col=len(df.columns), max_row=row_count+1)
        cats = Reference(ws, min_col=1, min_row=2, max_row=row_count+1)
        chart.add_data(data, titles_from_data=True)
        chart.set_categories(cats)
        ws.add_chart(chart, "D2")
    
    # Создание PNG для вывода
    plt.figure()
    if chart_type == "bar_chart":
        df[columns].plot(kind="bar")
    elif chart_type == "line_chart":
        df[columns].plot(kind="line")
    elif chart_type == "pie_chart":
        df[columns[0]].value_counts().plot(kind="pie")
    elif chart_type == "histogram":
        df[columns[0]].plot(kind="hist")
    elif chart_type == "scatter_plot":
        plt.scatter(df[columns[0]], df[columns[1]])
    elif chart_type == "area_chart":
        df[columns].plot(kind="area")

    plt.title(chart_type)

    os.makedirs("static", exist_ok=True)
    output_path = "static/chart.png"
    plt.savefig(output_path)
    plt.close()

    # Сохранение Excel файла с графиком
    excel_path = "static/chart.xlsx"
    wb.save(excel_path)

    return output_path


