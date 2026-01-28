import os
import pandas as pd

samples = ['1a','1b','2a','2b','3a','3b','4a','4b']
thicknesses = [105.347,103.591,113.063,115.604,135.526,136.539,120.133,122.352]
offsets = [-65.615,-65.615,-65.615,-65.615,-88.134,-88.134,-79.283,-79.283]
os.chdir('C:/Users/ewilkinson1605/Desktop/File Organization/Other EML Files/Mattress Project Report/CSV Extracted Data')

results = []
for i in range(len(samples)):
    data_25p = pd.read_csv(f'sample-{samples[i]}_25percent_loading.csv', encoding='utf8', header=1, skiprows=[2])
    data_65p = pd.read_csv(f'sample-{samples[i]}_65percent_loading.csv', encoding='utf8', header=1, skiprows=[2])
    data_unl = pd.read_csv(f'sample-{samples[i]}_unloading.csv', encoding='utf8', header=1, skiprows=[2])

    IDF_25 = data_65p.loc[0:10,'Axial Force'].mean()
    IDF_65 = data_unl.loc[0:10,'Axial Force'].mean()

    results.append([samples[i], IDF_25, IDF_65, IDF_65/IDF_25])

    data_25p['Strain'] = 1 - (data_25p['Axial Displacement'] - offsets[i]) / thicknesses[i]
    data_65p['Strain'] = 1 - (data_25p['Axial Displacement'] - offsets[i]) / thicknesses[i]
    data_25p['Strain'] = 1 - (data_25p['Axial Displacement'] - offsets[i]) / thicknesses[i]

    combined_curve = []
    for i, line in data_25p.iterrows():
        combined_curve.append([line['']])

output_df = pd.DataFrame(results,columns=['Sample','IDF 25%','IDF 65%','Support Factor'])
print(output_df)
