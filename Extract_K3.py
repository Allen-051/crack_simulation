##### 此版本「使用者可自行輸入K3」或「選擇case對應的代碼」，另需輸入取樣元素號碼、圖表標題
##### 可計算「contour平均值」和「與解析解之相對誤差」
##### 若使用者尚未取得解析解之K3，依然可以提取dat檔中的資料並且繪製成圖

import numpy as np
import os
import matplotlib as plt

def extract_K3():
    while True:
        choice = input("Do you want to extract K3 values? Enter 1 to skip, 2 to process: ").strip()
        if choice == '1':
            return False
        elif choice == '2':
            return True
        else:
            print("Invalid input. Please enter 1 or 2.")

def get_k3_value():
    user_choice = input("Hello, user. Do you want to define K3 value by yourself？\n"
                        "If so, please enter 'YES'\n"
                        "If not, please enter 'NO'：").strip().upper()
    if user_choice == 'YES':
        while True:
            try:
                K3_value = int(input("Please enter the K3 value: "))
                print(f"User-defined K3 value is {K3_value}")
                return K3_value
            except ValueError:
                print("This is not a valid number. Please enter an integer.")
    elif user_choice == 'NO':
        while True:
            try:
                K3_value = int(input('For soft inclusion a=2.4. Enter:1\n'
                                    'For soft inclusion a=4.0. Enter:2\n'
                                    'For soft inclusion a=5.6. Enter:3\n'
                                    'For E2=39 GPa, a=1.6. Enter:4\n'
                                    'For E2=39 GPa, a=2.0. Enter:5\n'
                                    'For E2=39 GPa, a=2.4. Enter:6\n'
                                    'For E2=52 GPa, a=1.6. Enter:7\n'
                                    'For E2=52 GPa, a=2.0. Enter:8\n'
                                    'For E2=52 GPa, a=2.4. Enter:9\n'
                                    'For E2=104 GPa, a=1.6. Enter:10\n'
                                    'For E2=104 GPa, a=2.0. Enter:11\n'
                                    'For E2=104 GPa, a=2.4. Enter:12\n'
                                    'Please enter the case value: '))
                if 1 <= K3_value <= 12:
                    print(f"\nYou pressed {K3_value}.\n")
                    return K3_value
                else:
                    print("Invalid number. Please enter again.")
            except ValueError:
                print("This is not a valid number. Please enter an integer.")
    else:
        print("Invalid input. Please enter 'YES' or 'NO'.")
        return get_k3_value()

def read_file(file_path):
    with open(file_path, 'r') as file:
        return file.readlines()

def process_K3_values(lines, K3):
    k3_values = []
    count = 1
    for line in lines:
        if 'K3:' in line:
            parts = line.split('K3:')[1].strip()
            values = [float(value) for value in parts.split()]
            k3_values.append([count] + values + [K3])
            count += 1
    return np.array(k3_values)

def calculate_relative_error(average_values, K3):
    rel_e = [(round((avg - K3) / K3 * 100, 3)) for avg in average_values]
    return rel_e

def plot_graph(k3_array, file_name,save_path):
    plt.figure(figsize=(10, 6))
    x = k3_array[:, 0]
    for i in range(1, k3_array.shape[1] - 1):
        plt.plot(x, k3_array[:, i], label=f'c-{i}')
    plt.plot(x, k3_array[:, -1], label='Semi-Analytical K3')
    plt.xlabel('element number')
    plt.ylabel('K3 values')
    plt.ylim(0, 40 * 10 ** 7)
    plt.title(file_name)
    plt.legend()
    plt.grid(True)
    plt.savefig(save_path)
    plt.show()


def save_results(k3_array, average_values, rel_e, up_bond, low_bond, output_path):

    with open(output_path, 'w') as output_file:
        output_file.write("These are the K3 values:\n")
        for arr in k3_array:
            output_file.write(', '.join(map(str, arr)) + '\n')
        output_file.write('\n')
        output_file.write("AVERAGE K3: " + ', '.join(map(str, average_values)) + '\n')
        output_file.write(f'The average values are calculated from element number {up_bond} to {low_bond}.\n\n')
        for i, rel_error in enumerate(rel_e):
            output_file.write(f"Contour {i + 1} relative Error : {rel_error}%\n")


def main():
    file_path = 'e2=39_mstfce_iclu.dat' #請使用者自行替換成要處理的dat檔案位置
    
    process_K3 = extract_K3()
    lines = read_file(file_path)
    ask_name = input('Please name this file： ')
    ### 輸入檔案儲存路徑 ###
    save_path = input("Please enter the directory to save the data: ").strip()

    os.makedirs(save_path, exist_ok=True)
    output_txt = os.path.join(save_path, f"{ask_name}.txt")
    output_jpg = os.path.join(save_path, f"{ask_name}.jpg")

    if process_K3:
        K3_value = get_k3_value()
        K3 = [520647600,
              551583600,
              579928500,
              321290400,
              337288600,
              352497900,
              287735200,
              305540600,
              322343000,
              224976700,
              246332000,
              266181000][K3_value - 1] if 1 <= K3_value <= 12 else K3_value
        k3_array = process_K3_values(lines, K3)
        s = np.array(k3_array)
        array_shape = s.shape
        print(f"The shape of the new array is: {array_shape}")
        up_bond = float(input('Please enter the first element number to calculate average value of K3: '))
        low_bond = float(input('Please enter the last element number to calculate average value of K3: '))
        filtered_k3_array = k3_array[(k3_array[:, 0] >= up_bond) & (k3_array[:, 0] <= low_bond)]
        average_values = np.round(np.mean(filtered_k3_array[:, 1:6], axis=0), 0)
        rel_e = calculate_relative_error(average_values, K3)
        save_results(k3_array, average_values, rel_e, up_bond, low_bond, output_txt)


    else:
        k3_array = process_K3_values(lines, 0)
        s = np.array(k3_array)
        array_shape = s.shape
        print(f"The shape of the new array is: {array_shape}")
        up_bond = float(input('Please enter the first element number to calculate average value of K3: '))
        low_bond = float(input('Please enter the last element number to calculate average value of K3: '))
        filtered_k3 = k3_array[(k3_array[:, 0] >= up_bond) & (k3_array[:, 0] <= low_bond)]

        with open(output_txt, 'w') as output_file:
            output_file.write("These are the K3 values:\n")
            for arr in k3_array:
                output_file.write(', '.join(map(str, arr)) + '\n')
            output_file.write('\n')
            average_values = np.round(np.mean(filtered_k3[:, 1:6], axis=0), 0)
            output_file.write("AVERAGE K3: " + ', '.join(map(str, average_values)) + '\n')
        os.makedirs(save_path, exist_ok=True)

    plot_graph(k3_array, ask_name,output_jpg)


if __name__ == "__main__":
    main()
