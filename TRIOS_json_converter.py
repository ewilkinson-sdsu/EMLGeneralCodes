import json
import pandas as pd
pd.set_option('display.width',300)
pd.set_option('display.max_columns',100)
pd.set_option('display.min_rows',200)
pd.set_option('display.max_rows',400)

def convert_json(file_name = 'C:/Users/ewilkinson/Documents/EML Files - Combined Data/DMA/PVDF Films/pvdf standard - dic test 5.json', strain_adjustment = True):
    with open(file_name, 'r', encoding='utf8') as file:
        json_data = json.load(file)

    sample_name = json_data['Sample']['Name']
    initial_length = json_data['Procedure']['Configuration']['InstrumentConfigurations'][0]['Geometry']['Length']['Value']
    initial_width = json_data['Procedure']['Configuration']['InstrumentConfigurations'][0]['Geometry']['Width']['Value']
    initial_thickness = json_data['Procedure']['Configuration']['InstrumentConfigurations'][0]['Geometry']['Thickness']['Value']
    initial_cross_sectional_area = initial_width * initial_thickness

    column_names = []
    column_parameters = []
    column_units = []
    for column in json_data['Results']['Processed']['ColumnHeaders']:
        column_names.append(column)
        column_parameters.append(json_data['Results']['Processed']['ColumnHeaders'][column]['DisplayName'])
        if json_data['Results']['Processed']['ColumnHeaders'][column]['ValueType'] == 'Number':
            column_units.append(json_data['Results']['Processed']['ColumnHeaders'][column]['Unit']['Name'])
        else:
            column_units.append('')

    experiment_data = []
    for row in json_data['Results']['Processed']['Rows']:
        temp_row = []
        for column_name in column_names:
            temp_row.append(row[column_name])
        experiment_data.append(temp_row)

    column_parameters_units_combined = []
    for param, unit in zip(column_parameters, column_units):
        if unit != '':
            column_parameters_units_combined.append(f'{param} ({unit})')
        else:
            column_parameters_units_combined.append(f'{param} (N/A)')

    converted_data = pd.DataFrame(experiment_data, columns=column_parameters_units_combined)

    if strain_adjustment:
        converted_data['Strain - Calculated (%)'] = 100 * (converted_data['Length (mm)'] - initial_length) / initial_length
        converted_data['Adjusted Cross-sectional Area (mm^2)'] = initial_cross_sectional_area / (converted_data['Strain - Calculated (%)'] / 100 + 1)
        converted_data['Stress - Calculated (MPa)'] = converted_data['Force (N)'] / converted_data['Adjusted Cross-sectional Area (mm^2)']

    if strain_adjustment:
        output_filename = file_name[0:-5] + '-adjusted.csv'
        print(f'"{sample_name}" analyzed, adjusted for initial size of {initial_length} x {initial_thickness} x {initial_width}')
    else:
        output_filename = file_name[0:-5] + '.csv'
        print(f'"{sample_name}" analyzed')

    converted_data = converted_data.reindex(sorted(converted_data.columns), axis=1)
    converted_data.to_csv(output_filename, na_rep='', index=False, encoding='utf-8')

    return sample_name, initial_length, initial_thickness, initial_width, converted_data

if __name__ == "__main__":
    convert_json()