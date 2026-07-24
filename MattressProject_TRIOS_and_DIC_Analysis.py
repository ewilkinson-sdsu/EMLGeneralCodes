from TRIOS_json_converter import convert_json
from DMA_stress_strain_modulus_calc import calculate_modulus
import os, glob
import pandas as pd

TRIOS_directory = 'C:/Users/ewilkinson/Documents/EML Files - Combined Data/DMA/PVDF Films'
DIC_directory = 'C:/Users/ewilkinson/Documents/EML Files - Combined Data/DIC/PVDF Films'
os.chdir(TRIOS_directory)   #D:/Current EML Data/DMA/Creep Unsmoked Filters
all_jsons = glob.glob('*.json')
# print(all_jsons)

for json in all_jsons:
    csv_name = json[0:-5] + '-adjusted.csv'
    if not os.path.isfile(csv_name):
        sample_name, initial_length, initial_thickness, initial_width, dma_data = convert_json(json, strain_adjustment=True)
    else:
        dma_data = pd.read_csv(csv_name)
    modulus, r2 = calculate_modulus(dma_data=dma_data, regression_span=20)


# for each in files_to_correct:
#     print(each)
#     correctAndCombine(file_name=each)