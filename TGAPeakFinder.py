from logging import Filter

import pandas as pd
import numpy as np
import scipy
import matplotlib.pyplot as plt
import statsmodels.api as sm
pd.set_option('display.width',400)
pd.set_option('display.max_columns',50)
pd.set_option('display.min_rows',100)
pd.set_option('display.max_rows',800)
np.set_printoptions(threshold=np.inf)

def TGAFindPeaks(file_name = './Leached_Unsmoked_CigLU2_750C_10Cmin.csv', prom_setting = .01):
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

    peaks = scipy.signal.find_peaks(tga_data['Deriv. Weight (%/°C)'], width=[75/heating_rate,2500/heating_rate], rel_height=.1, height = .05, prominence=prom_setting, wlen = 4500/heating_rate)
    # print(peaks)
    peak_sort = pd.DataFrame({'peaks':peaks[0],'prominences':peaks[1]['prominences']})
    peak_sort.sort_values(by='prominences',axis=0,ascending=False,ignore_index=True,inplace=True)
    # print(peak_sort)

    span = int(500/heating_rate)
    interpolated_peaks = []
    peak_heights = []
    for peak in peak_sort.iterrows():
        temp_temps = np.array(tga_data['Temperature (°C)'].loc[peak[1]['peaks']-span:peak[1]['peaks']+span])
        temp_derivs = np.array(tga_data['Deriv. Weight (%/°C)'].loc[peak[1]['peaks']-span:peak[1]['peaks']+span])
        x, y = scipy.optimize.curve_fit(func, temp_temps, temp_derivs, p0=[tga_data['Temperature (°C)'].loc[peak[1]['peaks']],-.001,-.001,tga_data['Deriv. Weight (%/°C)'].loc[peak[1]['peaks']]])
        interpolated_peaks.append(x[0])
        peak_heights.append(x[3])

        plt.figure(figsize=(4.5, 3), dpi=300)
        plt.plot(temp_temps, temp_derivs)
        plt.plot(temp_temps, func(temp_temps, *x), 'g--')
        plt.plot(x[0],x[3],'x')
        plt.show(block=True)
        # print(y)

    dc_c = [359.49582105285504, 130.49828874698957, 180.44422354427132]
    dc_h = [1.9602503035000647, 0.08614022732249757, 0.08250885695486251]

    pf_c = [np.float64(361.2381299332903), np.float64(129.343357775068), np.float64(175.07555286190598)]
    pf_h = [np.float64(2.036192448749077), np.float64(0.11439523335376074), np.float64(0.10914504932714185)]


    fig = plt.figure(sample_name + ' - ' + pos_name + '(' + pos_name2 + ') - ' + str(heating_rate),figsize=(4.5,3),dpi=300)
    plt.plot(tga_data['Temperature (°C)'], tga_data['Deriv. Weight (%/°C)'])
    for peak, height in zip(interpolated_peaks,peak_heights):
        plt.plot(interpolated_peaks, peak_heights, 'x')
        # plt.plot(pf_c, pf_h, 'x', color='red')
        # plt.plot(dc_c, dc_h, 'x', color='blue')
    plt.show()

    outputs = [sample_name, pos_name2, heating_rate, test_start_weight, float(ramp_start_weight), residue]
    for each in interpolated_peaks:
        outputs.append(float(each))
    print(outputs)
    print(interpolated_peaks)
    print(peak_heights)
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