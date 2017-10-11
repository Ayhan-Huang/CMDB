import xlrd

# 打开excel文件
workbook = xlrd.open_workbook('test.xlsx')

# 获取工作表
sheets = workbook.sheets()  # 获取工作表list。
sheet1 = sheets[0]  # 通过索引顺序获取。
sheet2 = workbook.sheet_by_index(1)  # 通过索引顺序获取。
sheet3 = workbook.sheet_by_name('sheet2')  # 通过名称获取。

# 获取行数和列数
rows = sheet1.nrows
cols = sheet1.ncols

# 获取一行和一列：
# row_values(i), i是行数，从0开始计数，返回list对象。
# col_values(i), i是列数，从0开始计数，返回list对象。
oneRow = sheet1.row_values(0)
oneCol = sheet1.col_values(0)
print('row',oneRow)  # [0.0, 1.0, 2.0, 3.0]
print('col',oneCol)  # [0.0, 1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0, 10.0]

# 获取单元格数据
myCell = sheet1.cell(0,0)
print('A1是',myCell)  # number:0.0
myCellValue = myCell.value
print('A1的值是',myCellValue)  # 0.0
myCellValue = sheet1.cell_value(0, 0)  # 直接获取单元格数据，i是行数，j是列数，行数和列数都是从0开始计数。

