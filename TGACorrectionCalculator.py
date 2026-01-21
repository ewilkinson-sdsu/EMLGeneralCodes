import pandas as pd
import numpy as np
from scipy.interpolate import make_splrep
from scipy.signal import butter, lfilter
import matplotlib.pyplot as plt
import statsmodels.api as sm
import math
pd.set_option('display.width',400)
pd.set_option('display.max_columns',50)
pd.set_option('display.min_rows',100)
pd.set_option('display.max_rows',800)
np.set_printoptions(threshold=np.inf)

def TGAFindPeaks(file_name = './Leached_Unsmoked_CigLU11_750C_05Cmin.csv'):
    start_weight = 0.0
    with open(file_name, encoding='utf-16-le') as fileObject:
        row_list = []
        for row in fileObject:
            row_list.append(row)
        weight_str = row_list[13]
        weight_str = weight_str.split("\t", 1)[1]
        weight_str = weight_str.split("\t", 1)[0]
        start_weight = float(weight_str)
        header_row = row_list.index('StartOfData\n') + 1
        nsig_row = [i for i, elem in enumerate(row_list) if 'Nsig' in elem]
        nsig = int(row_list[nsig_row[0]].split("\t", 1)[1])
        column_names = []
        for i in range(nsig):
            signal_name = 'Sig' + str(i+1)
            signalname_row = [i for i, elem in enumerate(row_list) if signal_name in elem]
            signal_name_full = row_list[signalname_row[0]].split("\t", 1)[1]
            column_names.append(signal_name_full.split("\n", 1)[0])

    tga_data = pd.read_csv(file_name, names = column_names, skiprows=header_row, encoding='utf-16-le', delimiter = '\t')
    tga_data = tga_data[tga_data['Time (min)'] > 1.995]
    tga_data.reset_index(drop = True, inplace = True)
    tga_data['Weight (%) - Header'] = 100 * tga_data['Weight (mg)'] / start_weight
    tga_data['Weight (%) - Initial'] = 100 * tga_data['Weight (mg)'] / tga_data['Weight (mg)'][0]
    tga_data['Deriv. Weight (%/°C) - Python'] = -tga_data['Weight (%) - Initial'].diff() / tga_data['Temperature (°C)'].diff()
    # tga_data['Smoothed Derivative'] = sm.nonparametric.lowess(tga_data['Deriv. Weight (%/°C) - Python'], tga_data['Temperature (°C)'], frac = 0.01, it = 3, return_sorted = False)
    print(tga_data)
    spline_subset = tga_data.dropna(axis=0,subset=['Deriv. Weight (%/°C) - Python'])
    spline_subset.sort_values(by='Temperature (°C)',inplace=True,ascending=True,ignore_index=True)

    reflect = 200
    # temp_temp_array = np.array(spline_subset['Temperature (°C)'])
    # temp_seriv_array = np.array(spline_subset['Deriv. Weight (%/°C) - Python'])
    # temp_temp_array = np.concatenate((np.flip(temp_temp_array[0:100]),temp_temp_array))
    # temp_seriv_array = np.concatenate((np.flip(temp_deriv_array[0:100]),temp_deriv_array))
    # print(temp_temp_array[0:200])
    # print(np.flip(temp_temp_array[0:100]))
    spline = make_splrep(spline_subset['Temperature (°C)'], spline_subset['Deriv. Weight (%/°C) - Python'])
    spline_temps = np.linspace(min(spline_subset['Temperature (°C)']),max(spline_subset['Temperature (°C)']),len(spline_subset)*100)
    print(len(spline_temps))
    spline_output = np.array(spline(spline_temps))
    plt.figure(figsize=(9,6),dpi=300)
    plt.xlim((50, 750))
    plt.ylim((-0.1, 1.3))
    plt.plot(spline_temps,spline_output,label='spline')
    plt.plot(tga_data['Temperature (°C)'], tga_data['Deriv. Weight (%/°C) - Python'],linewidth=.5, label='inst')
    plt.legend()
    plt.show()
    spline_output = np.concatenate((np.flip(spline_output[0:reflect]),spline_output))
    spline_freq = 1/(spline_temps[1]-spline_temps[0])
    filtered_signal = butter_lowpass_filter(spline_output, 1,spline_freq*2*math.pi, 3)


    # for i in range(7,14,1):
    #     for j in range(10):
    #         tga_data['Smoothed Derivative - ' + str(i/1000) + ' - ' + str(j)] = sm.nonparametric.lowess(tga_data['Deriv. Weight (%/°C) - Python'], tga_data['Temperature (°C)'],
    #                                                                 frac=i/1000, it=j, return_sorted=False)
    #
    # tga_data.to_csv('smoother_test3.csv',na_rep='',index=False)
    # print('figure start')
    plt.figure(figsize=(9,6),dpi=300)
    plt.xlim((50, 750))
    plt.ylim((-0.1, 1.3))
    plt.plot(tga_data['Temperature (°C)'], tga_data['Deriv. Weight (%/°C) - Python'],linewidth=.5, label='inst')
    plt.plot(tga_data['Temperature (°C)'], tga_data['Deriv. Weight (%/°C)'],linewidth=.5, label='ua')
    plt.plot(tga_data['Temperature (°C)'], tga_data['Smoothed - Matlab'],linewidth=.5, label='matlab')
    plt.plot(spline_temps, filtered_signal[reflect:],linewidth=.5, label='spline/lowpass')
    # print('fig calc start')
    # plt.plot(tga_data['Temperature (°C)'], tga_data['Smoothed Derivative'],linewidth=.3, label='Inline label')
    # plt.plot(tga_data['Temperature (°C)'], sm.nonparametric.lowess(tga_data['Deriv. Weight (%/°C) - Python'], tga_data['Temperature (°C)'], frac = 0.01, it = 0, return_sorted = False),linewidth=.1, label='0')
    # plt.plot(tga_data['Temperature (°C)'], sm.nonparametric.lowess(tga_data['Deriv. Weight (%/°C) - Python'], tga_data['Temperature (°C)'], frac = 0.01, it = 1, return_sorted = False),linewidth=.1, label='1')
    # plt.plot(tga_data['Temperature (°C)'], sm.nonparametric.lowess(tga_data['Deriv. Weight (%/°C) - Python'], tga_data['Temperature (°C)'], frac = 0.01, it = 2, return_sorted = False),linewidth=.1, label='2')
    # plt.plot(tga_data['Temperature (°C)'], sm.nonparametric.lowess(tga_data['Deriv. Weight (%/°C) - Python'], tga_data['Temperature (°C)'], frac = 0.01, it = 3, return_sorted = False),linewidth=.1, label='3')
    # plt.plot(tga_data['Temperature (°C)'], sm.nonparametric.lowess(tga_data['Deriv. Weight (%/°C) - Python'], tga_data['Temperature (°C)'], frac = 0.008, it = 3, return_sorted = False),linewidth=.15, label='.008 - 3')
    # print('1')
    # plt.plot(tga_data['Temperature (°C)'], sm.nonparametric.lowess(tga_data['Deriv. Weight (%/°C) - Python'], tga_data['Temperature (°C)'], frac = 0.01, it = 3, return_sorted = False),linewidth=.15, label='.01 - 3')
    # print('2')
    # plt.plot(tga_data['Temperature (°C)'], sm.nonparametric.lowess(tga_data['Deriv. Weight (%/°C) - Python'], tga_data['Temperature (°C)'], frac = 0.012, it = 3, return_sorted = False),linewidth=.15, label='.012 - 3')
    # print('3')
    # plt.plot(tga_data['Temperature (°C)'], sm.nonparametric.lowess(tga_data['Deriv. Weight (%/°C) - Python'], tga_data['Temperature (°C)'], frac = 0.008, it = 5, return_sorted = False),linewidth=.15, label='.008 - 5')
    # print('1')
    # plt.plot(tga_data['Temperature (°C)'], sm.nonparametric.lowess(tga_data['Deriv. Weight (%/°C) - Python'], tga_data['Temperature (°C)'], frac = 0.01, it = 5, return_sorted = False),linewidth=.15, label='.01 - 5')
    # print('2')
    # plt.plot(tga_data['Temperature (°C)'], sm.nonparametric.lowess(tga_data['Deriv. Weight (%/°C) - Python'], tga_data['Temperature (°C)'], frac = 0.012, it = 5, return_sorted = False),linewidth=.15, label='.012 - 5')
    # print('3')
    # plt.plot(tga_data['Temperature (°C)'], sm.nonparametric.lowess(tga_data['Deriv. Weight (%/°C) - Python'], tga_data['Temperature (°C)'], frac = 0.016, it = 6, return_sorted = False),linewidth=.15, label='.016')
    # print('4')
    # plt.plot(tga_data['Temperature (°C)'], sm.nonparametric.lowess(tga_data['Deriv. Weight (%/°C) - Python'], tga_data['Temperature (°C)'], frac = 0.01, it = 7, return_sorted = False),linewidth=.15, label='7')
    plt.legend()
    plt.show()

def butter_lowpass(cutoff, fs, order=5):
    return butter(order, cutoff, fs=fs, btype='low', analog=False)

def butter_lowpass_filter(data, cutoff, fs, order=5):
    b, a = butter_lowpass(cutoff, fs, order=order)
    y = lfilter(b, a, data)
    return y


if __name__ == "__main__":
    TGAFindPeaks()