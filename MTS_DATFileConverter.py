import os, glob, re, io
import pandas as pd

file_dir = os.chdir('C:/Users/Eric/Desktop/Mattress Project/data/First Project')   #D:/Current EML Data/DMA/Creep Unsmoked Filters
all_dats = glob.glob('*.dat')

for file in all_dats:
    with open(file, encoding='utf8') as f:
        data = f.read()
        # data = re.sub('Data Acquisition: Timed\nStation Name: EML858.cfg\nTest File Name:.*\nTime      Axial Force Axial Displacement\ns         N         mm\n0',
        #              '\nTime,Axial Force,Axial Displacement\ns,N,mm\n0', data)
        # data = re.sub('\n\n\nData Header:.*\nData Acquisition: Timed\nStation Name: EML858.cfg\nTest File Name:.*\nTime      Axial Force Axial Displacement\ns         N         mm',
        #              '', data)
        data = re.sub('MTS793\\|BTW\\|ENU\\|1\\|0\\|.\\|/\\|:\\|1\\|0\\|0\\|A\n\nData Header:.*Time:.*\nData Acquisition: Timed\nStation Name: EML858.cfg\nTest File Name:.*\nTime      Axial Force Axial Displacement\ns         N         mm\n0',
                     'Time (s),Axial Force (N),Axial Displacement (mm)\n0', data)
        data = re.sub('\n\n\nData Header:.*\nData Acquisition: Timed\nStation Name: EML858.cfg\nTest File Name:.*\nTime      Axial Force Axial Displacement\ns         N         mm',
                     '', data)
        # print(data)

        data = re.sub(' ', ',', data)
        # data = re.sub(',Time:,', ' Time: ', data)
        # data = re.sub('/2025,', '/2025 ', data)
        # data = re.sub(',AM', ' AM', data)
        # data = re.sub(',PM', ' PM', data)
        data = re.sub('Time,', 'Time ', data)
        data = re.sub('Force,', 'Force ', data)
        data = re.sub('Displacement,', 'Displacement ', data)
        data = re.sub('Axial,', 'Axial ', data)
        for i in range(50):
            data = re.sub(',,', ',', data)
        # print(data)

        data_df = pd.read_csv(io.StringIO(data))
        # print(data_df)

        runs = 1
        cut_index = []
        for index in range(1,len(data_df)):
            if data_df.loc[index,'Time (s)'] < data_df.loc[index - 1,'Time (s)']:
                cut_index.append(index)
                runs += 1
        # print(runs)

        if runs >= 2:
            start_index_list = [0] + cut_index
            end_index_list_plus1 = cut_index + [len(data_df)]
            for test in range(len(start_index_list)):
                data_df_slice = data_df[start_index_list[test]:end_index_list_plus1[test] - 1]
                data_df_slice.to_csv(file[:-4] + f'-{test+1}.csv', index=False, encoding='utf-8')
        else:
            data_df.to_csv(file[:-4] + '.csv', index=False, encoding='utf-8')
