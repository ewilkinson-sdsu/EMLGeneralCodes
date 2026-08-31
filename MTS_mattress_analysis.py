import pandas as pd
import glob, os, shutil

pd.set_option('display.width',300)
pd.set_option('display.max_columns',100)
pd.set_option('display.min_rows',200)
pd.set_option('display.max_rows',400)


os.chdir('C:/Users/Eric/Desktop/Mattress Project/data/Second Project/New Zero Order Retake/Raw Data')   #/New Zero Order Retake/Raw Data
all_csvs = glob.glob('*.csv')

samples = set()
for file in all_csvs:
    samples.add(file.split('_')[0])

platen_offset = 75.019
platen_play = 1.008

for sample in samples:
    down1 = pd.read_csv(f'{sample}_initcomp_down-1.csv', encoding='utf-8')
    up1 = pd.read_csv(f'{sample}_initcomp_up-1.csv', encoding='utf-8')
    down2 = pd.read_csv(f'{sample}_initcomp_down-2.csv', encoding='utf-8')
    up2 = pd.read_csv(f'{sample}_initcomp_up-2.csv', encoding='utf-8')
    initial_compression_1 = pd.concat([down1, up1])
    initial_compression_2 = pd.concat([down2, up2])
    initial_compressions = pd.concat([down1, up1, down2, up2])
    initial_compression_1['Height (mm)'] = initial_compression_1['Axial Displacement (mm)'] + platen_offset
    initial_compression_2['Height (mm)'] = initial_compression_2['Axial Displacement (mm)'] + platen_offset
    initial_compressions['Height (mm)'] = initial_compressions['Axial Displacement (mm)'] + platen_offset
    # print(initial_compressions)
    initial_compression_1.to_csv(f'../Individual Movements/{sample}_Intial_Compression_1.csv', index=False, encoding='utf-8')
    initial_compression_2.to_csv(f'../Individual Movements/{sample}_Intial_Compression_2.csv', index=False, encoding='utf-8')
    initial_compressions.to_csv(f'../{sample}_Intial_Compressions.csv', index=False, encoding='utf-8')

    full1 = pd.read_csv(f'{sample}_25percent_loading-1.csv', encoding='utf-8')
    full2 = pd.read_csv(f'{sample}_25percent_loading-2.csv', encoding='utf-8')
    full3 = pd.read_csv(f'{sample}_65percent_loading.csv', encoding='utf-8')
    full4 = pd.read_csv(f'{sample}_unloading.csv', encoding='utf-8')

    full1['Height (mm)'] = full1['Axial Displacement (mm)'] + platen_offset
    full2['Height (mm)'] = full2['Axial Displacement (mm)'] + platen_offset
    full3['Height (mm)'] = full3['Axial Displacement (mm)'] + platen_offset
    full4['Height (mm)'] = full4['Axial Displacement (mm)'] + platen_offset

    full1['Compressive Force (N)'] = -full1['Axial Force (N)']
    full2['Compressive Force (N)'] = -full2['Axial Force (N)']
    full3['Compressive Force (N)'] = -full3['Axial Force (N)']
    full4['Compressive Force (N)'] = -full4['Axial Force (N)']

    initial_thickness = full1.loc[len(full1) - 1,'Height (mm)'] - 1.008

    full1['Compressive Strain (%)'] = -100 * (full1['Height (mm)'] / initial_thickness - 1)
    full2['Compressive Strain (%)'] = -100 * (full2['Height (mm)'] / initial_thickness - 1)
    full3['Compressive Strain (%)'] = -100 * (full3['Height (mm)'] / initial_thickness - 1)
    full4['Compressive Strain (%)'] = -100 * (full4['Height (mm)'] / initial_thickness - 1)

    full1.to_csv(f'../Individual Movements/{sample}_Measurement_Compression.csv', index=False, encoding='utf-8')
    full2.to_csv(f'../Individual Movements/{sample}_25perc_Compression.csv', index=False, encoding='utf-8')
    full3.to_csv(f'../Individual Movements/{sample}_65perc_Compression.csv', index=False, encoding='utf-8')
    full4.to_csv(f'../Individual Movements/{sample}_Unloading.csv', index=False, encoding='utf-8')

    full1['Adjusted Height (mm)'] = full1['Height (mm)'] - platen_play
    try:
        adjustment_index = full2[(full2['Compressive Force (N)'] > 61.07)].index[0]
        full2['Adjusted Height (mm)'] = full2['Height (mm)']
        full2.loc[0:adjustment_index, 'Adjusted Height (mm)'] = full2.loc[0:adjustment_index, 'Height (mm)'] - platen_play
        full3['Adjusted Height (mm)'] = full3['Height (mm)']
        full4['Adjusted Height (mm)'] = full4['Height (mm)']
    except:
        full2['Adjusted Height (mm)'] = full2['Height (mm)'] - platen_play
        adjustment_index = full3[(full3['Compressive Force (N)'] > 61.07)].index[0]
        full3['Adjusted Height (mm)'] = full3['Height (mm)']
        full3.loc[0:adjustment_index, 'Adjusted Height (mm)'] = full3.loc[0:adjustment_index, 'Height (mm)'] - platen_play
        full4['Adjusted Height (mm)'] = full4['Height (mm)']
    # print(adjustment_index)

    IFD_25 = full3.loc[0:20,'Compressive Force (N)'].mean()
    IFD_65 = full4.loc[0:20,'Compressive Force (N)'].mean()
    support_factor = IFD_65 / IFD_25

    full_test = pd.concat([full1, full2, full3, full4])
    full_test.to_csv(f'../{sample}_Full_Test.csv', index=False, encoding='utf-8')
    # print(full_test)

    print(f'{sample}\t  {initial_thickness:0.3f} mm\tIFD25: {IFD_25:0.2f}\tIFD65: {IFD_65:0.2f}\tSF: {support_factor:0.3f}')