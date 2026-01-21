import pandas as pd
pd.set_option('display.width',400)
pd.set_option('display.max_columns',50)
pd.set_option('display.min_rows',100)
pd.set_option('display.max_rows',200)

def correctAndCombine(file_name = './unsmokedfilter_cig145_creepandrecovery_0p5mpa_2hours_30c.csv'):
    initial_length = 0.0
    initial_width = 0.0
    initial_thickness = 0.0
    with open(file_name) as fileObject:
        row_list = []
        for row in fileObject:
            row_list.append(row)
        length_str = row_list[25]
        length_str = length_str.split(",", 1)[1]
        length_str = length_str.split(" mm", 1)[0]
        initial_length = float(length_str)*1000
        width_str = row_list[26]
        width_str = width_str.split(",", 1)[1]
        width_str = width_str.split(" mm", 1)[0]
        initial_width = float(width_str)/1000
        thickness_str = row_list[27]
        thickness_str = thickness_str.split(",", 1)[1]
        thickness_str = thickness_str.split(" mm", 1)[0]
        initial_thickness = float(thickness_str)/1000
        header_row = row_list.index('[step]\n') + 2
    crosssectional_area = initial_width * initial_thickness

    creep_data = pd.read_csv(file_name[0:-4] + '-2.csv',header=header_row,skiprows=[header_row+1])
    creep_data = creep_data[['Time','Step time','Temperature','Force','Length']]
    creep_data['Strain'] = (creep_data['Length'] - initial_length) / initial_length
    creep_data['Adjusted Cross-section (m^2)'] = crosssectional_area / (creep_data['Strain'] + 1)
    creep_data['Stress (Pa)'] = creep_data['Force'] / creep_data['Adjusted Cross-section (m^2)']
    creep_data['Compliance (1/MPa)'] = 1000000 * creep_data['Strain'] / creep_data['Stress (Pa)']
    # print(creep_data)

    avg_measured_stress = creep_data['Stress (Pa)'].mean()
    max_strain = creep_data['Strain'].max()

    recovery_data = pd.read_csv(file_name,header=header_row,skiprows=[header_row+1])
    recovery_data = recovery_data[['Time','Step time','Temperature','Force','Length']]
    recovery_data['Strain'] = (recovery_data['Length'] - initial_length) / initial_length
    recovery_data['Adjusted Cross-section (m^2)'] = crosssectional_area / (recovery_data['Strain'] + 1)
    recovery_data['Stress (Pa)'] = recovery_data['Force'] / recovery_data['Adjusted Cross-section (m^2)']
    recovery_data['Recoverable Strain'] = max_strain - recovery_data['Strain']
    recovery_data['Recoverable Compliance (1/MPa)'] = 1000000 * recovery_data['Recoverable Strain'] / avg_measured_stress
    recovery_data['Recovered Strain'] = 1 - recovery_data['Strain'] / max_strain
    # print(recovery_data)

    all_data = pd.concat([creep_data,recovery_data],ignore_index=True)
    all_data.sort_values(by=['Time'],inplace=True,ignore_index=True)
    all_data.rename(columns={"Force": "Force (N)", "Step time": "Step time (s)", "Time": "Time (s)", "Temperature": "Temperature (C)", "Stress": "Stress (Pa)", "Length": "Length (um)"},inplace=True)
    all_data.drop(['Adjusted Cross-section (m^2)'],axis=1,inplace=True)
    # print(all_data)

    all_data.to_csv(file_name[0:-4] + '_corrected.csv',na_rep='',index=False)

if __name__ == "__main__":
    correctAndCombine()