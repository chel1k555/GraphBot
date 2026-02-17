import pandas as pd
import matplotlib.pyplot as plt
from openpyxl import Workbook
from openpyxl.chart import BarChart, LineChart, Reference, AreaChart
from openpyxl.drawing.image import Image as ExcelImage
from openpyxl.utils.dataframe import dataframe_to_rows
import io
import os
import json


    #возврат типа диаграммы в виде строки
def take_commands_and_return_type(json_input):
    list_commands = []
    for i in range(5):
        jsonchek = json_input[i]
        type_c = jsonchek.get("type", "")
        if type_c in ["line_chart", "bar_chart", "stacked_bar_chart", "pie_chart", "histogram", "boxplot", "scatter_plot", "heatmap", "area_chart", "bubble_chart"]:
            list_commands.append(type_c)
        else:
            list_commands.append("line_chart") # базовый если нету нужного
    return list_commands

def generate_report(input_file, sheets_to_process, user_commands):
    """
    input_file: путь к исходному Excel
    sheets_to_process: список названий листов
    user_commands: список команд (например, ['bar', 'line'])
    """
    output_file = "Result.xlsx"
    wb_new = Workbook()
    # Удаляем стандартный лист
    std_sheet = wb_new.active
    wb_new.remove(std_sheet)

    for sheet_name in sheets_to_process:
        # Чтение данных
        try:
            df = pd.read_excel(input_file, sheet_name=sheet_name)
        except Exception as e:
            print(f"Ошибка при чтении листа {sheet_name}: {e}")
            continue

        if df.empty:
            continue

        ws = wb_new.create_sheet(title=sheet_name)
        
        for r in dataframe_to_rows(df, index=False, header=True):
            ws.append(r)

        row_count = len(df)
        chart_col_letter = chr(65 + len(df.columns) + 2)
        current_row = 2

        for cmd in user_commands:
            chart = None
            if cmd == 'bar_chart':
                chart = BarChart()
                chart.title = f"Bar Chart ({sheet_name})"
            elif cmd == 'line_chart':
                chart = LineChart()
                chart.title = f"Line Chart ({sheet_name})"
            elif cmd == 'stacked_bar_chart':
                chart = BarChart()
                chart.type = "col"
                chart.grouping = "stacked"
                chart.title = f"Stacked Bar Chart ({sheet_name})"
            elif cmd == 'pie_chart':
                chart = BarChart()
                chart.type = "pie"
                chart.title = f"Pie Chart ({sheet_name})"
            elif cmd == 'hsitogram':
                chart = BarChart()
                chart.type = "col"
                chart.title = f"Histogram ({sheet_name})"
            elif cmd == 'boxplot':
                chart = BarChart()
                chart.type = "box"
                chart.title = f"Boxplot ({sheet_name})"
            elif cmd == 'scatter_plot':
                chart = LineChart()
                chart.style = 13
                chart.title = f"Scatter Plot ({sheet_name})"
            elif cmd == 'heatmap':
                chart = AreaChart()
                chart.title = f"Heatmap ({sheet_name})"
            elif cmd == 'area_chart':
                chart = AreaChart()
                chart.title = f"Area Chart ({sheet_name})"

            
            if chart:
                data = Reference(ws, min_col=2, min_row=1, max_col=len(df.columns), max_row=row_count+1)
                cats = Reference(ws, min_col=1, min_row=2, max_row=row_count+1)
                chart.add_data(data, titles_from_data=True)
                chart.set_categories(cats)
                ws.add_chart(chart, f"{chart_col_letter}{current_row}")

            # создаем png для диаграмм
            img_path = f"temp_{sheet_name}_{cmd}.png"
            df.plot(x=df.columns[0], kind='line' if cmd=='line' else 'bar')
            plt.title(f"{cmd.upper()} View")
            plt.savefig(img_path)
            plt.close()

            img = ExcelImage(img_path)
            ws.add_image(img, f"{chr(ord(chart_col_letter)+10)}{current_row}")
            
            current_row += 20

        auto_chart = None
        cond_label = ""
        
        if row_count <= 20:
            auto_chart = BarChart()
            cond_label = "Small Data (Bar)"
        elif 20 < row_count <= 50:
            auto_chart = LineChart()
            cond_label = "Medium Data (Line)"
        elif 50 < row_count <= 100:
            auto_chart = AreaChart()
            cond_label = "Large Data (Area)"
        else:
            auto_chart = LineChart()
            cond_label = "Huge Data (Line)"

        if auto_chart:
            auto_chart.title = f"Auto Logic: {cond_label}"
            data_ref = Reference(ws, min_col=2, min_row=1, max_col=len(df.columns), max_row=row_count+1)
            auto_chart.add_data(data_ref, titles_from_data=True)
            ws.add_chart(auto_chart, f"{chart_col_letter}{current_row}")

            # PNG для автоматической диаграммы
            img_path_auto = f"temp_{sheet_name}_auto.png"
            kind_map = {BarChart: 'bar', LineChart: 'line', AreaChart: 'area'}
            df.plot(x=df.columns[0], kind='line' if row_count > 20 else 'bar')
            plt.title(cond_label)
            plt.savefig(img_path_auto)
            plt.close()

            img_auto = ExcelImage(img_path_auto)
            ws.add_image(img_auto, f"{chr(ord(chart_col_letter)+10)}{current_row}")

    #чистка временных и сохран итога
    wb_new.save(output_file)
    for file in os.listdir():
        if file.startswith("temp_") and file.endswith(".png"):
            os.remove(file)
            
    print(f"Файл {output_file} успешно создан.")

'''
def create_test_excel():
    with pd.ExcelWriter("test_data.xlsx") as writer:
        df1 = pd.DataFrame({'Category': ['A', 'B', 'C'], 'Val': [10, 20, 15]})
        df1.to_excel(writer, sheet_name='SmallSheet', index=False)
        
        df2 = pd.DataFrame({'Month': range(60), 'Users': [x**2 for x in range(60)]})
        df2.to_excel(writer, sheet_name='BigSheet', index=False)
'''

if __name__ == "__main__":

    #create_test_excel()
    
    # Параметры: файл, листы, команды
    target_sheets = ['SmallSheet', 'BigSheet']
    list_of_jsons = ['{type:}', '{type:}', '{type:}', '{type:}', '{type:}']
    commands = take_commands_and_return_type(list_of_jsons)
    
    generate_report("test_data.xlsx", target_sheets, commands)