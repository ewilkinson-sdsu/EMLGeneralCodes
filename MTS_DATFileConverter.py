import os, glob, re, io
import pandas as pd

file_dir = os.chdir('C:/Users/ewilkinson1605/Desktop/File Organization/Other EML Files/Mattress Project Report/CSV Extracted Data')   #D:/Current EML Data/DMA/Creep Unsmoked Filters
all_dats = glob.glob('*.dat')
all_csvs = glob.glob('*.csv')

# for file in all_dats:
#     with open(file, encoding='utf8') as f:
#         data = f.read()
#         data = re.sub('Data Acquisition: Timed\nStation Name: EML858.cfg\nTest File Name:.*\nTime      Axial Force Axial Displacement\ns         N         mm\n0',
#                      '\nTime,Axial Force,Axial Displacement\ns,N,mm\n0', data)
#         data = re.sub('\n\n\nData Header:.*\nData Acquisition: Timed\nStation Name: EML858.cfg\nTest File Name:.*\nTime      Axial Force Axial Displacement\ns         N         mm',
#                      '', data)
#         print(data)
#
#     with open(file[:-4] + '.csv', 'w', encoding='utf8') as f:
#         f.write(data)

for file in all_csvs:
    with open(file, encoding='utf8') as f:
        data = f.read()
        data = re.sub(' ', ',', data)
        data = re.sub(',Time:,', ' Time: ', data)
        data = re.sub('/2025,', '/2025 ', data)
        data = re.sub(',AM', ' AM', data)
        data = re.sub(',PM', ' PM', data)
        data = re.sub('Axial,', 'Axial ', data)
        for i in range(15):
            data = re.sub(',,', ',', data)
        print(data)

    with open(file, 'w', encoding='utf8') as f:
        f.write(data)
