from TGAPeakFinder import TGAFindPeaks
import os, glob
import csv

dir_name = 'C:/Users/ewilkinson1605/Desktop/File Organization/Combined EML Data/TGA/Cigarette Filters/Smoked Activation Energy'
file_dir = os.chdir(dir_name)
tga_csvs = glob.glob('*cig*.csv')

file_outputs = []
for each in tga_csvs:
    print(each)
    file_outputs.append(TGAFindPeaks(file_name=each, prom_setting = .0005))
print(file_outputs)
fields = ['Sample','Position','Heating Rate (C/min)','Weight at Test Start (mg)','Weight at Ramp Start (mg)','Residue (%)','Peaks (C)']
with open('TGA Analysis Outputs - Smoked Activation Energy.csv','w', newline='') as myfile:
    writer = csv.writer(myfile)
    writer.writerow(fields)     # Write header
    writer.writerows(file_outputs)