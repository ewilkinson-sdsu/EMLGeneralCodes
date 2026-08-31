from TRIOS_json_converter import convert_json
from DMA_stress_strain_modulus_calc import calculate_modulus
from DIC_poisson_calc import calculate_poisson
import os, glob
import pandas as pd

TRIOS_directory = 'C:/Users/Eric/Desktop/pvdf film project/PVDF Films/'
DIC_directory = 'C:/Users/Eric/Desktop/pvdf film project/dic files/'
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
    dic_base_file = DIC_directory + json[0:-5]
    final_strain, poisson_ratio = calculate_poisson(dic_base_file=dic_base_file, dma_data=dma_data, eval_span = 20)
    print(f'{json[0:-5]} with {modulus:0.1f} MPa and {poisson_ratio:0.4f} poisson ratio')


# for each in files_to_correct:
#     print(each)
#     correctAndCombine(file_name=each)