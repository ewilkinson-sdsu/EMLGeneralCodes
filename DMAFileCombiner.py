from operator import index

import pandas as pd
import os, glob
pd.set_option('display.width',400)
pd.set_option('display.max_columns',50)
pd.set_option('display.min_rows',100)
pd.set_option('display.max_rows',200)

def fileCombine(folder = 'D:/Current EML Data/DMA/Creep Unsmoked Filters', parameter = 'Recovered Strain', comb_range = 'recovery', output_file = 'AllUnsmokedFilters_Recovery.csv'):
    os.chdir(folder)
    all_tests = glob.glob('*_corrected.csv')

    if comb_range == 'creep':
        time_max = 7200
        index_min = 0
        index_max = 7200
    elif comb_range == 'recovery':
        time_max = 7200
        index_min = 7200
        index_max = 14400
    elif comb_range == 'both':
        time_max = 14400
        index_min = 0
        index_max = 14400

    all_test_data = pd.DataFrame()
    all_test_data['Time'] = range(0,time_max)
    all_test_data['Time'] = all_test_data['Time'] + 0.5
    for each in all_tests:
        print(each)
        indiv_file_data = pd.read_csv(each)
        filename_split = each.split("_", 10)
        cig_id = filename_split[1]
        stress_id = filename_split[3]
        temp_id = filename_split[5]
        id = stress_id+" "+temp_id+" - "+cig_id
        all_test_data[id] = indiv_file_data[parameter][index_min:index_max].to_numpy()
    # print(all_test_data)

    # print(sorted(all_test_data.columns))
    all_test_data = all_test_data[sorted(all_test_data.columns)]
    all_test_data = all_test_data[ ['Time'] + [ col for col in all_test_data.columns if col != 'Time' ] ]
    all_test_data.to_csv(output_file,na_rep='',index=False)

if __name__ == "__main__":
    fileCombine()