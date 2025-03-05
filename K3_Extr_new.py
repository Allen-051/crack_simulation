##### 此版本「使用者可自行輸入K3」或「選擇case對應的代碼」，另需輸入取樣元素號碼、圖表標題
##### 可計算「contour平均值」和「與解析解之相對誤差」
##### 若使用者尚未取得解析解之K3，依然可以提取dat檔中的資料並且繪製成圖

import numpy as np
import os
import matplotlib.pyplot as plt

def extract_K3():
    while True:
        choice = input("使用者，你好，如果你*沒有解析解*請按1，有解析解請按2: ").strip()
        if choice == '1':
            return False
        elif choice == '2':
            return True
        else:
            print("輸入錯誤，請輸入1或2")

def get_k3_value():
    user_choice = input("請問你想自己輸入K3解析解嗎？\n"
                        "是，請輸入：YES\n"
                        "否，請輸入：NO\n"
                        "您的回覆：").strip().upper()
    if user_choice == 'YES':
        while True:
            try:
                K3_value = int(input("請輸入K3的大小: "))
                print(f"使用者定義的K3為 {K3_value}")
                return K3_value
            except ValueError:
                print("這個數目無效，請輸入一整數.")
    elif user_choice == 'NO':
        while True:
            try:
                K3_value = int(input('For E2=10.4 GPa, a=2.4. 輸入:1\n'
                                    'For E2=10.4 GPa, a=4.0. 輸入:2\n'
                                    'For E2=10.4 GPa, a=5.6. 輸入:3\n'
                                    'For E2=39 GPa, a=1.6. 輸入:4\n'
                                    'For E2=39 GPa, a=2.0. 輸入:5\n'
                                    'For E2=39 GPa, a=2.4. 輸入:6\n'
                                    'For E2=52 GPa, a=1.6. 輸入:7\n'
                                    'For E2=52 GPa, a=2.0. 輸入:8\n'
                                    'For E2=52 GPa, a=2.4. 輸入:9\n'
                                    'For E2=104 GPa, a=1.6. 輸入:10\n'
                                    'For E2=104 GPa, a=2.0. 輸入:11\n'
                                    'For E2=104 GPa, a=2.4. 輸入:12\n'
                                    '請按下對應的選擇值: '))
                if 1 <= K3_value <= 12:
                    print(f"\n你輸入了 {K3_value}.\n")
                    return K3_value
                else:
                    print("數值不在這範圍，請再次輸入。")
            except ValueError:
                print("請輸入一個整數")
    else:
        print("請您輸入'YES'或'NO'。")
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
    plt.ylim(30 * 10** 7, 60* 10 ** 7)
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
    ask_path = input('請告訴我檔案位置(絕對位置)如 D:\pbc\job-1.dat'
                     '\n輸入檔案路徑：　').strip()
    if not os.path.exists(ask_path):
        print("檔案不存在，請確認路徑是否正確。")
        exit()

    process_K3 = extract_K3()
    lines = read_file(ask_path)
    ask_name = input('請告訴我這個檔案的名稱(無須附檔名)： ')
    ### 輸入檔案儲存路徑 ###
    save_path = input("請告訴我，你想要儲存這個檔案的路徑位置(絕對位置): ").strip()

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
        print(f"txt檔案近乎完成！請確認陣列輸出的尺寸(元素數目,共7筆資料): {array_shape}")
        up_bond = float(input('請告訴我計算「K3平均值」的第一個元素數目: '))
        low_bond = float(input('請告訴我計算「K3平均值」的最後一個個元素數目: '))
        filtered_k3_array = k3_array[(k3_array[:, 0] >= up_bond) & (k3_array[:, 0] <= low_bond)]
        average_values = np.round(np.mean(filtered_k3_array[:, 1:6], axis=0), 0)
        rel_e = calculate_relative_error(average_values, K3)
        save_results(k3_array, average_values, rel_e, up_bond, low_bond, output_txt)


    else:
        k3_array = process_K3_values(lines, 0)
        s = np.array(k3_array)
        array_shape = s.shape
        print(f"txt檔案近乎完成！請確認陣列輸出的尺寸(元素數目,共7筆資料): {array_shape}")
        up_bond = float(input('請告訴我計算「K3平均值」的第一個元素數目: '))
        low_bond = float(input('請告訴我計算「K3平均值」的最後一個個元素數目: '))
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
