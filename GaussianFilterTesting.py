from logging import Filter

import pandas as pd
import numpy as np
from scipy.optimize import curve_fit
from scipy.signal import find_peaks
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

    peaks = find_peaks(tga_data['Deriv. Weight (%/°C)'], width=[75/heating_rate,2500/heating_rate], rel_height=.1, height = .05, prominence=prom_setting, wlen = 4500/heating_rate)
    print(peaks)
    peak_sort = pd.DataFrame({'peaks':peaks[0],'prominences':peaks[1]['prominences'],'heights':peaks[1]['peak_heights'],'widths':peaks[1]['widths']})
    peak_sort.sort_values(by='prominences',axis=0,ascending=False,ignore_index=True,inplace=True)
    # print(peak_sort)
    deconv_initial_guess = []
    upper_bound = []
    lower_bound = []
    for peak in peak_sort.iterrows():
        deconv_initial_guess.append(float(peak[1]['heights']))
        deconv_initial_guess.append(float(tga_data['Temperature (°C)'].loc[peak[1]['peaks']]))
        deconv_initial_guess.append(float(peak[1]['widths']/20))
        deconv_initial_guess.append(0.5)
        upper_bound.append(float(peak[1]['heights'])+2)
        upper_bound.append(float(tga_data['Temperature (°C)'].loc[peak[1]['peaks']])+20)
        upper_bound.append(float(peak[1]['widths']/20)+50)
        upper_bound.append(2)
        lower_bound.append(float(peak[1]['heights'])-2)
        lower_bound.append(float(tga_data['Temperature (°C)'].loc[peak[1]['peaks']])-20)
        lower_bound.append(float(peak[1]['widths']/20)-50)
        lower_bound.append(-1)
    print(deconv_initial_guess)

    x, y = curve_fit(t_gaussian, tga_data['Temperature (°C)'], tga_data['Deriv. Weight (%/°C)'], p0 = deconv_initial_guess, bounds = [lower_bound, upper_bound])
    # print(x)
    # print(y)

    fig = plt.figure(sample_name + ' - ' + pos_name + '(' + pos_name2 + ') - ' + str(heating_rate),figsize=(4.5,3),dpi=300)
    plt.plot(tga_data['Temperature (°C)'], tga_data['Deriv. Weight (%/°C)'], label='deriv')
    y_fit_all = t_gaussian(tga_data['Temperature (°C)'], *x)
    plt.plot(tga_data['Temperature (°C)'],y_fit_all, linewidth=1, label='all')
    for i in range(len(peak_sort)):
        y_fit = gaussian(tga_data['Temperature (°C)'], *x[0+4*i:4+4*i])
        plt.plot(tga_data['Temperature (°C)'], y_fit, linewidth=1, label=i)
    plt.legend()
    plt.show()

    outputs = [sample_name, pos_name2, heating_rate, test_start_weight, float(ramp_start_weight), residue]
    for i in range(len(peak_sort)):
        outputs.append(float(x[1+4*i]))
    print(outputs)

    c_peaks = []
    c_heights =[]
    for i in range(len(peak_sort)):
        c_peaks.append(float(x[1+4*i]))
        c_heights.append(float(x[0+4*i]))
    print(c_peaks)
    print(c_heights)
    return outputs

def gaussian(x, amp, mu, sig, c):
    fun_val = c + amp * np.exp( -np.power(x- mu, 2) / (2 * np.power(sig, 2)))
    return fun_val

def t_gaussian(x, amp1, mu1, sig1, c1, amp2, mu2, sig2, c2, amp3, mu3, sig3, c3):
    fun_val1 = gaussian(x, amp1, mu1, sig1, c1)
    fun_val2 = gaussian(x, amp2, mu2, sig2, c2)
    fun_val3 = gaussian(x, amp3, mu3, sig3, c3)
    return fun_val1 + fun_val2 + fun_val3

if __name__ == "__main__":
    TGAFindPeaks()
