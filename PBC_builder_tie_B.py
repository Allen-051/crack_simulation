file_path = 'Job-7.inp' #請使用者自行更改為合適的.inp檔案路徑

# 分開存儲 inclusion 與 out 的節點資訊
incl_coord_inf = []  # *Part, name=inclusion 內的節點數據
matx_coord_inf = []  # *Part, name=out 內的節點數據

with open(file_path, 'r') as file:
    lines = file.readlines()

# 讀取並記錄節點座標數據
is_in_node_section = False
part_count = 0  # 計數，確認處理第幾個Part區段
current_storage = None  # 指向目前要存放資料的變數

for line in lines:
    line = line.strip()

    if line.startswith("*Part, name=inclusion"):
        is_in_node_section = True
        part_count += 1
        current_storage = incl_coord_inf  # 存入 incl_coord_inf
        continue
    elif line.startswith("*Part, name=out"):
        is_in_node_section = True
        part_count += 1
        current_storage = matx_coord_inf  # 存入 matx_coord_inf
        continue
    elif line.startswith("*Element, type=C3D8R"):
        if part_count == 1:  # 遇到第一個 *Element, type=C3D8R
            is_in_node_section = False
        elif part_count == 2:  # 遇到第二個 *Element, type=C3D8R
            is_in_node_section = False
        continue

    if is_in_node_section and current_storage is not None:
        elements = line.split(',')
        if len(elements) == 4:
            node_id = elements[0].strip()
            x_coord = float(elements[1].strip())
            y_coord = float(elements[2].strip())
            z_coord = float(elements[3].strip())
            current_storage.append([node_id, x_coord, y_coord, z_coord])

# **座標對應陣列**
incl_x_coord = [row[1] for row in incl_coord_inf]
incl_y_coord = [row[2] for row in incl_coord_inf]
incl_z_coord = [row[3] for row in incl_coord_inf]

matx_x_coord = [row[1] for row in matx_coord_inf]
matx_y_coord = [row[2] for row in matx_coord_inf]
matx_z_coord = [row[3] for row in matx_coord_inf]

# **輸出陣列大小**
print(f"Total number of nodes in incl_coord_inf: {len(incl_coord_inf)}")
print(f"Total number of nodes in matx_coord_inf: {len(matx_coord_inf)}")


# **讀取 Back & Front Set**
def extract_elements(file_path, start_keyword, end_keyword):
    elements = []
    is_in_section = False
    with open(file_path, 'r') as file:
        for line in file:
            if start_keyword in line:
                is_in_section = True
                continue
            if is_in_section and end_keyword in line:
                break
            if is_in_section:
                elements.extend(line.strip().split(','))

    elements = [elem.strip() for elem in elements if elem.strip()]
    return elements


# 提取 Back & Front Set
back_set = extract_elements(file_path, '*Nset, nset=back', '*Elset, elset=back')
front_set = extract_elements(file_path, '*Nset, nset=front', '*Elset, elset=front')

# 提取 Inclusion Set
in_b_set = extract_elements(file_path, '*Nset, nset=in-b,', '*Elset, elset=in-b,')
in_f_set = extract_elements(file_path, '*Nset, nset=in-f,', '*Elset, elset=in-f,')


# **配對座標**
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


# **Back & Front 使用 matx_coord_inf**
back_set_rows = match_set_with_coords(back_set, matx_coord_inf)
front_set_rows = match_set_with_coords(front_set, matx_coord_inf)

# **Inclusion Sets 使用 incl_coord_inf**
in_b_set_rows = match_set_with_coords(in_b_set, incl_coord_inf)
in_f_set_rows = match_set_with_coords(in_f_set, incl_coord_inf)

# **設定模型大小**
model_size = float(input("Please enter the model size: "))
m_size = model_size + 10 ** -5

# **配對 Back & Front**
new_front_set_arrangement = []
for back_row in back_set_rows:
    for front_row in front_set_rows:
        if back_row[1] == front_row[1] and back_row[2] == front_row[2] and abs(front_row[3] - back_row[3]) <= m_size:
            new_front_set_arrangement.append(front_row[0])

# **配對 Inclusion Sets**
new_in_f_set_arrangement = []
for in_b_row in in_b_set_rows:
    for in_f_row in in_f_set_rows:
        if in_b_row[1] == in_f_row[1] and in_b_row[2] == in_f_row[2] and abs(in_b_row[3] - in_f_row[3]) <= m_size:
            new_in_f_set_arrangement.append(in_f_row[0])

# **輸出最終結果**
print(f"New front set has {len(new_front_set_arrangement)} nodes.")
print(f"New front inclusion set has {len(new_in_f_set_arrangement)} nodes.")

# **寫入 PBC 方程**
equations_matrix = []
for back_row, front_node in zip(back_set_rows, new_front_set_arrangement):
    for i in range(1, 4):
        equations_matrix.append(f"*Equation\n2\nout-1.{front_node}, {i}, 1.,out-1.{back_row[0]}, {i}, -1.")

equations_inclusion = []
for in_b, in_f in zip(in_b_set_rows, new_in_f_set_arrangement):
    for j in range(1, 4):
        equations_inclusion.append(f"*Equation\n2\ninclusion-1.{in_f}, {j}, 1.,inclusion-1.{in_b[0]}, {j}, -1.")

# **輸出到文件**
output_path = r'D:\ABAQUS\infinite crack\hard_tie\a=2.0\caseB\COPY_8.txt'
with open(output_path, 'w') as f:
    f.write(f"New front set has {len(new_front_set_arrangement)} nodes.\n")
    f.write(f"New front inclusion set has {len(new_in_f_set_arrangement)} nodes.\n")
    ### 文件內輸出新的front set ###
    f.write("#This is the new front set arrangement:\n")
    if new_front_set_arrangement:
        for i in range(0, len(new_front_set_arrangement), 16):
            f.write(", ".join(new_front_set_arrangement[i:i + 16]) + "\n")
    ### 文件內輸出新的front inclusion set ###
    f.write("##This is the new front inclusion set arrangement:\n")
    if new_in_f_set_arrangement:
        for i in range(0, len(new_in_f_set_arrangement), 16):
            f.write(", ".join(new_in_f_set_arrangement[i:i + 16]) + "\n")
    ### 文件內列出所有匹配點的PBC關鍵字 ###
    f.write("###Key words to build PBC equations:\n")
    for word in equations_matrix:
        f.write(word + "\n")
    for word in equations_inclusion:
        f.write(word + "\n")

print(f"Data has been written to {output_path}.")
