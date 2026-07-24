import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
pd.set_option('display.width',300)
pd.set_option('display.max_columns',100)
pd.set_option('display.min_rows',800)
pd.set_option('display.max_rows',800)

dic_base_file_default = 'C:/Users/ewilkinson/Documents/EML Files - Combined Data/DIC/Mattress Project/Quasi-static Test 5'
dma_file_default = 'C:/Users/ewilkinson/Documents/EML Files - Combined Data/DMA/PVDF Films/pvdf standard - dic test 5.csv'

def calculate_poisson(dic_base_file = None, dma_file = None, eval_index = 0, eval_span = 20, uncertainty_cutoff = 5, plot_data = False):
    vert_file = dic_base_file + ' - vertical.xlsx'
    horiz_file = dic_base_file + ' - horizontal.xlsx'

    dma_data = pd.read_csv(dma_file, encoding='utf-8')

    vert_data = pd.read_excel(vert_file, skiprows=3, header=None, names=['Step','Vertical mStrain (mm/m)','Vertical mStrain Uncertainty (mm/m)'])
    horiz_data = pd.read_excel(horiz_file, skiprows=3, header=None, names=['Step','Horizontal mStrain (mm/m)','Horizontal mStrain Uncertainty (mm/m)'])
    combined_dic_data = pd.merge(vert_data, horiz_data, how='outer', on=['Step'])
    combined_dic_data['Poisson Ratio'] = -combined_dic_data['Horizontal mStrain (mm/m)'] / combined_dic_data['Vertical mStrain (mm/m)']
    combined_dic_data['Poisson Ratio Uncertainty'] = np.sqrt((combined_dic_data['Horizontal mStrain Uncertainty (mm/m)'] / combined_dic_data['Vertical mStrain (mm/m)']) ** 2 + (combined_dic_data['Horizontal mStrain (mm/m)'] * combined_dic_data['Vertical mStrain Uncertainty (mm/m)'] / (combined_dic_data['Vertical mStrain (mm/m)']) ** 2) ** 2)
    combined_dic_data = combined_dic_data.reindex(sorted(combined_dic_data.columns), axis=1)

    shifted_poisson = []
    length_adjust = len(dma_data) - len(combined_dic_data)
    for i in range(len(dma_data)):
        if i < length_adjust:
            shifted_poisson.append([np.nan, np.nan])
        else:
            shifted_poisson.append([combined_dic_data.loc[i - length_adjust,'Poisson Ratio'].item(), combined_dic_data.loc[i - length_adjust,'Poisson Ratio Uncertainty'].item()])
    dma_data[['Poisson Ratio','Poisson Ratio Uncertainty']] = shifted_poisson

    tan_mod = []
    for i, row in dma_data.iterrows():
        # print(dma_data.loc[i,'Stress - Calculated (MPa)'])
        if i == 0:
            tan_mod.append(np.nan)
        else:
            tan_mod.append((dma_data.loc[i, 'Stress - Calculated (MPa)'] - dma_data.loc[i - 1, 'Stress - Calculated (MPa)']) / (
                        (dma_data.loc[i, 'Strain - Calculated (%)'] - dma_data.loc[i - 1, 'Strain - Calculated (%)']) / 100))

    dma_data['tan(Modulus) (MPa)'] = tan_mod

    if plot_data:
        fig, ax = plt.subplots()
        ax.plot(dma_data['Strain - Calculated (%)'], dma_data['Poisson Ratio'],'k')
        ax.set(xlabel='Strain (%)', ylabel="Poisson's")
        ax.set_xlim(0, 5)
        ax.set_ylim(0, 0.3)
        ax2 = ax.twinx()
        ax2.plot(dma_data['Strain - Calculated (%)'], dma_data['tan(Modulus) (MPa)'],'r')
        ax2.set(ylabel="tan(mod) (MPa)")
        ax2.set_ylim(0, 6000)
        plt.show()

    if eval_index < eval_span: eval_index = eval_span

    poisson_running_avg = []
    for i in range(len(dma_data)):
        if i < eval_index:
            poisson_running_avg.append([np.nan, np.nan])
        else:
            temp_slice = dma_data.loc[i - eval_span:i + eval_span, ['Poisson Ratio', 'Poisson Ratio Uncertainty']]
            temp_len = len(temp_slice)
            uncertainty_terms = []
            for i, row in temp_slice.iterrows():
                # print(row['Poisson Ratio'])
                uncertainty_terms.append((row['Poisson Ratio Uncertainty'] / temp_len) ** 2)
            poisson_running_avg.append([temp_slice['Poisson Ratio'].mean(), np.sqrt(sum(uncertainty_terms)).item()])

    dma_data[['Poisson Ratio Running Avg', 'Poisson Ratio Running Avg Uncertainty']] = poisson_running_avg
    dma_data['Poisson Ratio Running Avg Unvertainty (%)'] = abs(dma_data['Poisson Ratio Running Avg Uncertainty'] / dma_data['Poisson Ratio Running Avg']) * 100

    temp_index = dma_data.loc[dma_data['Poisson Ratio Running Avg Unvertainty (%)'] < uncertainty_cutoff].index[0]

    return dma_data.loc[temp_index, ['Strain - Calculated (%)', 'Poisson Ratio Running Avg']].to_list()

if __name__ == "__main__":
    print(calculate_poisson(dic_base_file=dic_base_file_default, dma_file=dma_file_default))
