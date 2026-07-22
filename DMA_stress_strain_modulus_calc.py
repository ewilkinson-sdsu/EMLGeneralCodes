import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
pd.set_option('display.width',300)
pd.set_option('display.max_columns',100)
pd.set_option('display.min_rows',200)
pd.set_option('display.max_rows',400)

def calculate_modulus(dma_data = None, file_name = None, regression_span = 20):
    if dma_data is None:
        if file_name is not None:
            dma_data = pd.read_csv(file_name, encoding='utf-8')
        else:
            print('Error: No input data or file_name')
            return

    tan_mod = []
    for i, row in dma_data.iterrows():
        # print(dma_data.loc[i,'Stress - Calculated (MPa)'])
        if i == 0:
            tan_mod.append(np.nan)
        else:
            tan_mod.append((dma_data.loc[i, 'Stress - Calculated (MPa)'] - dma_data.loc[i - 1, 'Stress - Calculated (MPa)']) / ((dma_data.loc[i, 'Strain - Calculated (%)'] - dma_data.loc[i - 1, 'Strain - Calculated (%)']) / 100))

    dma_data['tan(Modulus) (MPa)'] = tan_mod

    peak_mod_loc = dma_data['tan(Modulus) (MPa)'].idxmax()
    if peak_mod_loc < 20: peak_mod_loc = 20

    strain_fit_vals = np.reshape(np.array(dma_data.loc[peak_mod_loc - regression_span:peak_mod_loc + regression_span, 'Strain - Calculated (%)'] / 100), (-1, 1))
    stress_fit_vals = np.array(dma_data.loc[peak_mod_loc - regression_span:peak_mod_loc + regression_span, 'Stress - Calculated (MPa)'])
    reg = LinearRegression().fit(strain_fit_vals, stress_fit_vals)
    modulus = reg.coef_[0]
    r2 = reg.score(strain_fit_vals, stress_fit_vals)

    return [modulus.item(), r2]

if __name__ == "__main__":
    print(calculate_modulus(file_name='C:/Users/ewilkinson/Documents/EML Files - Combined Data/DMA/PVDF Films/pvdf standard - dic test 4.csv'))
