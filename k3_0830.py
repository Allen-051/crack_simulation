import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import os

def read_file(file_path):
    with open(file_path, 'r', encoding='big5', errors='ignore') as file:
        return file.readlines()

def extract_K3_blocks(lines):
    key = 'K   F A C T O R       E S T I M A T E S'
    indices = [i for i, line in enumerate(lines) if key in line]
    if len(indices) < 2:
        print("無法在檔案中找到兩次 'K FACTOR ESTIMATES' 出現。")
        return None, None
    return lines[indices[0]:indices[1]], lines[indices[1]:]

def process_K3_values(lines, K3=0):
    k3_values = []
    count = 1
    for line in lines:
        if 'K3:' in line:
            parts = line.split('K3:')[1].strip()
            values = [float(value) for value in parts.split()]
            k3_values.append([count] + values + [K3])
            count += 1
    return np.array(k3_values)

def get_k3_value():
    user_choice = input("請問你想自己輸入K3解析解嗎？\n是，請輸入：YES；否，請輸入：NO\n您的回覆：").strip().upper()
    if user_choice == 'YES':
        while True:
            try:
                return int(input("請輸入K3的大小: "))
            except ValueError:
                print("無效數字，請重新輸入整數。")
    elif user_choice == 'NO':
        menu = [520647600, 551583600, 579928500, 321290400, 337288600, 352497900,
                287735200, 305540600, 322343000, 224976700, 246332000, 266181000]
        while True:
            try:
                choice = int(input('請輸入對應選項(1~12): '))
                if 1 <= choice <= 12:
                    return menu[choice - 1]
                else:
                    print("請輸入 1~12 之間的數字。")
            except ValueError:
                print("請輸入整數。")
    else:
        print("請輸入 'YES' 或 'NO'")
        return get_k3_value()

def plot_k3(df, save_path, file_name, K3_exact=None):
    colors = ['maroon', 'deeppink', 'red', 'purple', 'orangered']
    plt.figure(figsize=(12, 6))
    x = df['Element']
    for i in range(5):
        plt.plot(x, df[f"K3-1-{i+1}"], label=f"K3-1-{i+1}", color=colors[i])
    plt.plot(x, df["K3-2-1"], label="K3-2-1", color='blue', linewidth=2)
    if K3_exact:
        plt.axhline(K3_exact, color='black', linestyle='--', label=f"解析解 K3 = {K3_exact:.0f}")
    plt.xlabel("Element")
    plt.ylabel("K3 Value")
    plt.title("K3 Comparison")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(os.path.join(save_path, f"{file_name}.jpg"))
    plt.show()

def prompt_for_bounds():
    while True:
        try:
            up = float(input("請輸入平均值起始元素編號（例如 10）: "))
            low = float(input("請輸入平均值結束元素編號（例如 20）: "))
            if up >= low:
                print("錯誤：起始編號必須小於結束編號。請重新輸入。")
            else:
                return up, low
        except ValueError:
            print("請輸入有效的數字。")

def save_to_csv(df, save_path, file_name, up_bond, low_bond, K3_exact=None):
    csv_path = os.path.join(save_path, f"{file_name}.csv")
    df = df.round({col: 0 for col in df.columns if 'K3' in col and 'Relative' not in col})
    df["Relative_Error"] = df["Relative_Error"].map(lambda x: f"{x:.3f}%")
    df.to_csv(csv_path, index=False, float_format='%.0f', sep=',  ')
    avg_row = df[(df["Element"] >= up_bond) & (df["Element"] <= low_bond)].mean(numeric_only=True).to_frame().T

    with open(csv_path, 'a', encoding='utf-8') as f:
        f.write('\n')
        f.write(f'Average from Element {int(up_bond)} to {int(low_bond)}\n')
        avg_row = avg_row.round({col: 0 for col in avg_row.columns if 'K3' in col and 'Relative' not in col})
        avg_row.to_csv(f, index=False, float_format='%.0f', sep=',  ')
        if K3_exact:
            avg_val = avg_row[[f"K3-1-{i+1}" for i in range(5)]].mean(axis=1).values[0]
            rel_err = round((avg_val - K3_exact) / K3_exact * 100, 3)
            f.write(f'Relative error compared to exact: {rel_err:.3f}')

def main():
    # 檔案路徑與儲存位置
    while True:
        dat_path = input("請輸入 dat 檔案絕對路徑：").strip()
        if os.path.exists(dat_path):
            break
        else:
            print("檔案不存在，請重新輸入。")

    while True:
        save_path = input("請輸入儲存資料夾路徑：").strip()
        try:
            os.makedirs(save_path, exist_ok=True)
            break
        except:
            print("無法建立資料夾，請重新輸入。")

    file_name = input("請輸入檔案名稱（無副檔名）：").strip()
    lines = read_file(dat_path)
    block1, block2 = extract_K3_blocks(lines)

    # 詢問是否有解析解
    while True:
        choice = input("請問是否有解析解？\n沒有請輸入 1，有請輸入 2：").strip()
        if choice == '1':
            K3_exact = None
            break
        elif choice == '2':
            K3_exact = get_k3_value()
            break
        else:
            print("請輸入有效選項（1 或 2）。")

    # 處理 K3
    k3_array_1 = process_K3_values(block1)
    k3_array_2 = process_K3_values(block2)

    df = pd.DataFrame(k3_array_1[:, :6], columns=["Element"] + [f"K3-1-{i+1}" for i in range(5)])
    df["K3-2-1"] = k3_array_2[:, 1] if k3_array_2.shape[1] > 1 else np.nan
    if K3_exact:
        df["K3_exact"] = K3_exact

    # 平均值處理
    up_bond, low_bond = prompt_for_bounds()
    avg_df = df[(df["Element"] >= up_bond) & (df["Element"] <= low_bond)]
    mean_vals = avg_df.mean(numeric_only=True)
    print("各圈 K3-1 平均值:")
    for i in range(5):
        print(f"K3-1-{i+1}: {int(round(mean_vals[f'K3-1-{i+1}'])).__str__()}" )
    avg_k3_2 = mean_vals["K3-2-1"]
    print(f"/nK3-2-1: {int(round(avg_k3_2))}")

    if K3_exact:
        avg_k3 = mean_vals[[f"K3-1-{i+1}" for i in range(5)]].mean()
        rel_err = round((avg_k3 - K3_exact) / K3_exact * 100, 3)
        print(f"與解析解相對誤差：{rel_err}%")

    # 存檔與繪圖
    save_to_csv(df, save_path, file_name, up_bond, low_bond, K3_exact)
    plot_k3(df, save_path, file_name, K3_exact)

if __name__ == "__main__":
    main()