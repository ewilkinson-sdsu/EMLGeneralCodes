import pandas as pd
import numpy as np
import scipy
import matplotlib.pyplot as plt
pd.set_option('display.width',400)
pd.set_option('display.max_columns',50)
pd.set_option('display.min_rows',100)
pd.set_option('display.max_rows',800)
# np.set_printoptions(threshold=np.inf)

# file_name = 'C:/Users/ewilkinson1605/Desktop/File Organization/Combined EML Data/DMA/Sean Foam Compression/DMA Foam Avgs.csv'
# dma_data = pd.read_csv(file_name)
# dma_data['Loss Modulus (MPa)'] = dma_data['Loss Modulus (MPa)'] / 1000000
# dma_data['Storage Modulus (MPa)'] = dma_data['Storage Modulus (MPa)'] / 1000000
# # print(dma_data)

def FindPeaks(x_data, y_data, prom_setting=0.01, span=6, plot_peaks=True, plot_signal=True, width=None, rel_height=0.5, height=None, wlen=None):

    peaks = scipy.signal.find_peaks(y_data, prominence=(prom_setting*y_data.max()), width=width, rel_height=rel_height, height=height, wlen=wlen)
    # print(peaks)
    peak_sort = pd.DataFrame({'peaks':peaks[0],'prominences':peaks[1]['prominences']})
    peak_sort.sort_values(by='prominences',axis=0,ascending=False,ignore_index=True,inplace=True)
    # print(peak_sort)

    interpolated_peaks = []
    peak_heights = []
    peak_indexes = []
    for peak in peak_sort.iterrows():
        temp_temps = np.array(x_data.loc[peak[1]['peaks']-span:peak[1]['peaks']+span])
        temp_derivs = np.array(y_data.loc[peak[1]['peaks']-span:peak[1]['peaks']+span])
        x, y = scipy.optimize.curve_fit(func, temp_temps, temp_derivs, p0=[x_data.loc[peak[1]['peaks']],-1,-1,y_data.loc[peak[1]['peaks']]])
        interpolated_peaks.append(x[0])
        peak_heights.append(x[3])
        peak_indexes.append(peak[1]['peaks'])

        if plot_peaks:
            plt.figure(figsize=(4.5, 3), dpi=300)
            plt.plot(temp_temps, temp_derivs)
            plt.plot(temp_temps, func(temp_temps, *x), 'g--')
            plt.plot(x[0],x[3],'x')
            plt.show(block=True)
        # print(y)

    if plot_signal:
        fig = plt.figure(figsize=(4.5,3),dpi=300)
        plt.plot(x_data, y_data)
        for peak, height in zip(interpolated_peaks,peak_heights):
            plt.plot(interpolated_peaks, peak_heights, 'x')
        plt.show()

    peak_outputs = []
    for ind, x_loc, height in zip(peak_indexes, interpolated_peaks, peak_heights):
        peak_outputs.append([ind.item(), x_loc.item(), height.item()])
    # print(peak_outputs)
    return peak_outputs

def func(x,a,b,c,d):
    y_vals = []
    for x_val in x:
        if x_val >= a:
            y_vals.append(b * (x_val - a) ** 2 + d)
        else:
            y_vals.append(c * (x_val - a) ** 2 + d)
    return np.array(y_vals)

# if __name__ == "__main__":
#     FindPeaks(dma_data['Temperature (C)'], dma_data['Loss Modulus (MPa)'])