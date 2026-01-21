from DMACorrectionCalculator import correctAndCombine
import os, glob

file_dir = os.chdir('D:/Current EML Data/DMA/Creep Unsmoked Filters')   #D:/Current EML Data/DMA/Creep Unsmoked Filters
all_csvs = glob.glob('*cig*.csv')
second_csvs = glob.glob('*cig*-*.csv')
corrected_csvs = glob.glob('*cig*_corrected.csv')

files_list = all_csvs
files_to_correct = []
for each in second_csvs:
    files_list.remove(each)
for each in corrected_csvs:
    files_list.remove(each)
for each in files_list:
    corrected_name = each[0:-4] + '_corrected.csv'
    if corrected_name not in corrected_csvs:
        files_to_correct.append(each)

for each in files_to_correct:
    print(each)
    correctAndCombine(file_name=each)