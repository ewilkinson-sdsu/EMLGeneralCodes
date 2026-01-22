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

def multiPeakFinder():
    peaks = [602, 903, 1031, 1217, 1364, 1735]
    spans = [7, 15, 8, 14, 10, 40]
    # peaks = [1735]
    # spans = [40]
    columns = ['Unsmoked (%)', 'Smoked (%)', 'Leached Unsmoked (%)', 'Leached Smoked (%)', 'CAP (%)']
    all_peaks = pd.DataFrame(columns=columns, dtype=float)
    for peak, span in zip(peaks, spans):
        sample_peaks = FTIR_Peaks(peak_loc = peak, point_span=span)
        temp_df = pd.DataFrame([sample_peaks],columns=columns)
        all_peaks = pd.concat([all_peaks, temp_df], ignore_index=True)
    print(all_peaks)
    # all_peaks.to_csv('FITR_peaks.csv')

def FTIR_Peaks(file_name = './CombinedSpectra.csv', peak_loc = 601.75, check_span = 5, point_span = 5):
    FTIR_data = pd.read_csv(file_name)
    column_names = FTIR_data.columns
    column_names = column_names[1:]
    # print(column_names[0:])

    peak_index_low = (FTIR_data['Wavenumber (1/cm)'] - peak_loc + check_span).abs().argsort()[:1][0]
    peak_index_high = (FTIR_data['Wavenumber (1/cm)'] - peak_loc - check_span).abs().argsort()[:1][0]

    interpolated_peaks = []
    peak_heights = []
    for name in column_names:
        est_transmittance = FTIR_data[name][peak_index_low:peak_index_high].min()
        peak_index = (FTIR_data[name] - est_transmittance).abs().argsort()[:1][0]
        est_peak = FTIR_data['Wavenumber (1/cm)'][peak_index]
        temp_wavenum = np.array(FTIR_data['Wavenumber (1/cm)'].loc[peak_index-point_span:peak_index+point_span])
        temp_trans = np.array(FTIR_data[name].loc[peak_index-point_span:peak_index+point_span])
        x, y = scipy.optimize.curve_fit(func, temp_wavenum, temp_trans, p0=[est_peak,.1,.1,est_transmittance])
        interpolated_peaks.append(x[0])
        peak_heights.append(x[3])

        wavenum_span = np.linspace(FTIR_data['Wavenumber (1/cm)'].loc[peak_index-point_span],FTIR_data['Wavenumber (1/cm)'].loc[peak_index+point_span],100)
        plt.figure(figsize=(4.5, 3), dpi=300)
        plt.plot(temp_wavenum, temp_trans,'b.')
        plt.plot(wavenum_span, func(wavenum_span, *x), 'k--')
        plt.plot(x[0],x[3],'x')
        plt.show(block=False)
        # print(y)
    #
    # # fig = plt.figure(sample_name + ' - ' + pos_name + '(' + pos_name2 + ') - ' + str(heating_rate),figsize=(4.5,3),dpi=300)
    # # plt.plot(FTIR_data['Temperature (°C)'], FTIR_data['Deriv. Weight (%/°C)'])
    # for peak, height in zip(interpolated_peaks,peak_heights):
    #     plt.plot(interpolated_peaks, peak_heights, 'x')
    #     # plt.plot(pf_c, pf_h, 'x', color='red')
    #     # plt.plot(dc_c, dc_h, 'x', color='blue')
    # plt.show()
    #
    int_peaks = []
    for each in interpolated_peaks:
        int_peaks.append(float(each))
    return int_peaks

def func(x,a,b,c,d):
    y_vals = []
    for x_val in x:
        if x_val >= a:
            y_vals.append(b * (x_val - a) ** 2 + d)
        else:
            y_vals.append(c * (x_val - a) ** 2 + d)
    return np.array(y_vals)

if __name__ == "__main__":
    multiPeakFinder()
