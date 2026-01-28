from PeakFinder_Interp import FindPeaks
import pandas as pd
import numpy as np
import os
pd.set_option('display.width',400)
pd.set_option('display.max_columns',50)
pd.set_option('display.min_rows',100)
pd.set_option('display.max_rows',800)
np.set_printoptions(threshold=np.inf)

def TGAFindPeaks(prom_setting = 0.01, folder_name = 'C:/Users/ewilkinson1605/Desktop/File Organization/Combined EML Data/TGA/Cigarette Filters/Leached Unsmoked/Leak', file_name = './Leached_Unsmoked_CigLU2_750C_10Cmin.csv'):
    os.chdir(folder_name)
    with open(file_name, encoding='utf-16-le') as fileObject:
        row_list = []
        for row in fileObject:
            row_list.append(row)
        weight_str = row_list[13]
        weight_str = weight_str.split("\t", 1)[1]
        weight_str = weight_str.split("\t", 1)[0]
        test_start_weight = float(weight_str)
        header_row = row_list.index('StartOfData\n') + 1
        rate_row = [i for i, elem in enumerate(row_list) if '°C/min' in elem]
        heating_rate = row_list[rate_row[0]].split(" °C/min", 1)[0]
        heating_rate = float(heating_rate.split("Ramp ", 1)[1])
        nsig_row = [i for i, elem in enumerate(row_list) if 'Nsig' in elem]
        nsig = int(row_list[nsig_row[0]].split("\t", 1)[1])
        column_names = []
        for i in range(nsig):
            signal_name = 'Sig' + str(i+1)
            signalname_row = [i for i, elem in enumerate(row_list) if signal_name in elem]
            signal_name_full = row_list[signalname_row[0]].split("\t", 1)[1]
            column_names.append(signal_name_full.split("\n", 1)[0])

    if 'Cigarette' in file_name:
        sample_name = file_name.split('Cigarette')[1]
        sample_name = sample_name.split('_')[0]
    elif 'Filter' in file_name:
        try:
            sample_name = file_name.split('Filter')[2]
            sample_name = sample_name.split('_')[0]
        except:
            sample_name = file_name.split('Filter')[1]
            sample_name = sample_name.split('_')[0]
    elif 'Cig' in file_name:
        sample_name = file_name.split('Cig')[1]
        sample_name = sample_name.split('_')[0]
    else:
        sample_name = file_name
    if sample_name == '':
        sample_name = file_name

    if 'Position' in file_name:
        pos_name = file_name.split('Position')[1]
        pos_name = pos_name.split('_')[0]
    elif 'Pos' in file_name:
        pos_name = file_name.split('Pos')[1]
        pos_name = pos_name.split('_')[0]
    else:
        pos_name = '-'
    if pos_name == '4':
        pos_name2 = 'Mouth'
    elif pos_name == '3':
        pos_name2 = 'Middle'
    elif pos_name == '1':
        pos_name2 = 'Tobacco'
    elif pos_name == '2':
        pos_name2 = 'Tobacco - 1 Slice Back'
    else:
        pos_name2 = pos_name

    tga_data = pd.read_csv(file_name, names = column_names, skiprows=header_row, encoding='utf-16-le', delimiter = '\t')
    tga_data = tga_data[tga_data['Time (min)'] > 1.995]
    tga_data.reset_index(drop = True, inplace = True)
    ramp_start_weight = tga_data['Weight (mg)'][0]
    tga_data['Weight (%)'] = 100 * tga_data['Weight (mg)'] / ramp_start_weight
    residue = min(tga_data['Weight (%)'])

    interpolated_peaks = FindPeaks(x_data=tga_data['Temperature (°C)'], y_data=tga_data['Deriv. Weight (%/°C)'], width=[75/heating_rate,2500/heating_rate], rel_height=.1, height = .05, prom_setting=prom_setting, wlen = 4500/heating_rate)
    print(interpolated_peaks)

    outputs = [sample_name, pos_name2, heating_rate, test_start_weight, float(ramp_start_weight), residue]
    for each in interpolated_peaks:
        outputs.append(float(each[1]))
    print(outputs)
    return outputs

def func(x,a,b,c,d):
    y_vals = []
    for x_val in x:
        if x_val >= a:
            y_vals.append(b * (x_val - a) ** 2 + d)
        else:
            y_vals.append(c * (x_val - a) ** 2 + d)
    return np.array(y_vals)

if __name__ == "__main__":
    TGAFindPeaks()