import os


def get_inp_file():
    # 1. 讓使用者輸入 .inp 檔案完整路徑
    file_path = input("請輸入要讀取的 .inp 檔案完整路徑: ").strip()
    if not os.path.exists(file_path):
        print("檔案不存在，請確認路徑是否正確。")
        exit()

    ask_file_name = input('請告訴我檔案名稱(無須副檔名)：')
    file_name = ask_file_name + '.inp'
    directory = os.path.dirname(file_path)  # 取得原始檔案所在的資料夾
    output_path = os.path.join(directory, file_name)  # 儲存新的 inp 檔案

    # 讀取檔案內容
    with open(file_path, 'r') as file:
        lines = file.readlines()

    return file_path, output_path, lines


def extract_node_data(lines):
    is_in_node_section = False
    coord_inf = []

    for line in lines:
        line = line.strip()

        if line.startswith("*Part, name=out"):
            is_in_node_section = True
            continue
        elif line.startswith("*Element, type=C3D8R"):
            is_in_node_section = False
            break

        if is_in_node_section:
            elements = line.split(',')
            if len(elements) == 4:
                node_id = elements[0].strip()
                x_coord = float(elements[1].strip())
                y_coord = float(elements[2].strip())
                z_coord = float(elements[3].strip())
                coord_inf.append([node_id, x_coord, y_coord, z_coord])

    return coord_inf


def extract_elements(lines, start_keyword, end_keyword):
    elements = []
    is_in_section = False
    for line in lines:
        if start_keyword in line:
            is_in_section = True
            continue
        if is_in_section and end_keyword in line:
            break
        if is_in_section:
            elements.extend(line.strip().split(','))
    elements = [elem.strip() for elem in elements if elem.strip()]
    return elements


def match_set_with_coords(node_set, coord_inf):
    node_ids = [row[0] for row in coord_inf]
    x_coords = [row[1] for row in coord_inf]
    y_coords = [row[2] for row in coord_inf]
    z_coords = [row[3] for row in coord_inf]

    matched_rows = []
    for node in node_set:
        if node in node_ids:
            index = node_ids.index(node)
            matched_rows.append([node, x_coords[index], y_coords[index], z_coords[index]])
    return matched_rows

def replace_section(lines, start_keyword, end_keyword, new_data):
    is_in_section = False
    new_lines = []
    for line in lines:
        if start_keyword in line:
            is_in_section = True
            new_lines.append(line)  # 保留關鍵字行
            continue
        if is_in_section and end_keyword in line:
            is_in_section = False
            # 插入新數據，每行 16 個數字
            for i in range(0, len(new_data), 16):
                new_lines.append(",  ".join(new_data[i:i + 16]) + "\n")
        if not is_in_section:
            new_lines.append(line)
    return new_lines

def build_PBC_word(lines, base_array, rearrange_array):
    equations = []
    is_enrichment_section = False
    new_lines = []

    for line in lines:
        if "*Enrichment," in line:
            is_enrichment_section = True
        if is_enrichment_section and "*End Assembly" in line:
            for back_row, front_node in zip(base_array, rearrange_array):
                for i in range(1, 4):
                    equations.append(f"*Equation\n2\nout-1.{front_node}, {i}, 1.,out-1.{back_row[0]}, {i}, -1.\n")
            is_enrichment_section = False
        new_lines.append(line)

    return new_lines[:new_lines.index("*End Assembly\n")] + equations + new_lines[new_lines.index("*End Assembly\n"):]


def main():
    file_path, output_path, lines = get_inp_file()
    coord_inf = extract_node_data(lines)

    back_set = extract_elements(lines, '*Nset, nset=back', '*Elset, elset=back')
    front_set = extract_elements(lines, '*Nset, nset=front', '*Elset, elset=front')
    in_b_set = extract_elements(lines, '*Nset, nset=in-b,', '*Elset, elset=in-b,')
    in_f_set = extract_elements(lines, '*Nset, nset=in-f,', '*Elset, elset=in-f,')

    back_set_rows = match_set_with_coords(back_set, coord_inf)
    front_set_rows = match_set_with_coords(front_set, coord_inf)
    in_b_set_rows = match_set_with_coords(in_b_set, coord_inf)
    in_f_set_rows = match_set_with_coords(in_f_set, coord_inf)

    model_size = float(input("請告訴我模型的Z方向長度(深度): "))
    m_size = model_size + 10 ** -6

    new_front_set_arrangement = []
    for back_row in back_set_rows:
        for front_row in front_set_rows:
            if back_row[1] == front_row[1] and back_row[2] == front_row[2] and abs(
                    front_row[3] - back_row[3]) <= m_size:
                new_front_set_arrangement.append(front_row[0])

    new_in_f_set_arrangement = []
    for in_b_row in in_b_set_rows:
        for in_f_row in in_f_set_rows:
            if in_b_row[1] == in_f_row[1] and in_b_row[2] == in_f_row[2] and abs(in_b_row[3] - in_f_row[3]) <= m_size:
                new_in_f_set_arrangement.append(in_f_row[0])

    modified_lines = replace_section(lines, '*Nset, nset=front', '*Elset, elset=front', new_front_set_arrangement)
    modified_lines = replace_section(modified_lines, '*Nset, nset=in-f,', '*Elset, elset=in-f,',
                                     new_in_f_set_arrangement)
    modified_lines = build_PBC_word(modified_lines, back_set_rows, new_front_set_arrangement)
    modified_lines = build_PBC_word(modified_lines, in_b_set_rows, new_in_f_set_arrangement)

    with open(output_path, 'w') as file:
        file.writelines(modified_lines)

    print(f"已儲存修改後的 inp 檔案: {output_path}")


if __name__ == "__main__":
    main()
