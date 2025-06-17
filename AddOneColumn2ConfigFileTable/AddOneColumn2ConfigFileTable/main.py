import sqlite3
def column_exists(cursor, table, column):
    cursor.execute(f'PRAGMA table_info({table})')
    return any(col[1] == column for col in cursor.fetchall())

def is_numeric(text):
    try:
        float(text)
        return True
    except (ValueError, TypeError):
        return False

def get_column_values_with_rowid(cursor, table, column):
    """
    获取指定表中某列的所有 rowid 和该列的值
    返回列表形式：[ (rowid, value), ... ]
    """
    cursor.execute(f'SELECT rowid, "{column}" FROM {table}')
    return cursor.fetchall()

def print_all_rows(coption: str, cursor, table):
    """
    打印表中所有数据，包括列名。
    """
    cursor.execute(f'SELECT * FROM {table}')
    rows = cursor.fetchall()

    # 获取列名
    column_names = [description[0] for description in cursor.description]
    print(f"{coption}： 表结构:", column_names)

    print("数据内容:")
    for row in rows:
        print(row)

def fix_column_to_numeric_text(db_path, table, column, default='3.5'):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    print_all_rows("修改前查看数据库", cursor, table)

    # 1. 如果列不存在，则添加
    if not column_exists(cursor, table, column):
        print(f'添加列 "{column}"...')
        cursor.execute(f'ALTER TABLE {table} ADD COLUMN "{column}" TEXT')
        conn.commit()
    else:
        print(f'列 "{column}" 已存在。')

    # 2. 读取该列的所有值
    rows = get_column_values_with_rowid(cursor, table, column)

    # 3. 筛选出非数字项，准备更新
    to_update = [(default, rowid) for rowid, value in rows if not is_numeric(value)]

    print(f'需更新 {len(to_update)} 条不能转为数字的记录')

    if to_update:
        cursor.executemany(
            f'UPDATE {table} SET "{column}" = ? WHERE rowid = ?',
            to_update
        )
        conn.commit()

    print_all_rows("修改后查看数据库", cursor, table)

    cursor.close()
    conn.close()

# 按装订区域中的绿色按钮以运行脚本。
if __name__ == '__main__':
    # 用法示例
    fix_column_to_numeric_text('./IVSDatabase.db', 'configFile', 'NavImgZoomInScale', '3.5')
    input("按 Enter 键继续...")

# 访问 https://www.jetbrains.com/help/pycharm/ 获取 PyCharm 帮助
