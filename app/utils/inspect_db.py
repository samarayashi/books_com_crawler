from sqlalchemy import inspect
from sqlalchemy import create_engine
from ..database import SQLALCHEMY_DATABASE_URL

def inspect_database():
    """檢查數據庫結構並以易讀格式輸出"""
    try:
        engine = create_engine(SQLALCHEMY_DATABASE_URL)
        inspector = inspect(engine)
        
        # 添加調試信息
        tables = inspector.get_table_names()
        print(f"發現的表格: {tables}")
        
        if not tables:
            print("警告：數據庫中沒有找到任何表格！")
            return {}
            
        database_structure = {}
        
        for table_name in tables:
            database_structure[table_name] = {
                "columns": [],
                "primary_keys": [],
                "foreign_keys": [],
                "indexes": []
            }
            
            # 獲取列信息
            columns = inspector.get_columns(table_name)
            for column in columns:
                column_info = {
                    "name": column['name'],
                    "type": str(column['type']),
                    "nullable": column['nullable'],
                    "default": str(column.get('default', 'None'))
                }
                database_structure[table_name]["columns"].append(column_info)
                
            # 使用 get_pk_constraint 替代 get_primary_keys
            pk_constraint = inspector.get_pk_constraint(table_name)
            if pk_constraint:
                database_structure[table_name]["primary_keys"] = pk_constraint.get('constrained_columns', [])
            
            # 獲取外鍵
            foreign_keys = inspector.get_foreign_keys(table_name)
            for fk in foreign_keys:
                fk_info = {
                    "constrained_columns": fk['constrained_columns'],
                    "referred_table": fk['referred_table'],
                    "referred_columns": fk['referred_columns']
                }
                database_structure[table_name]["foreign_keys"].append(fk_info)
            
            # 獲取索引
            indexes = inspector.get_indexes(table_name)
            database_structure[table_name]["indexes"] = indexes

        return database_structure
        
    except Exception as e:
        print(f"檢查數據庫時發生錯誤: {str(e)}")
        return {}

def print_database_structure():
    """以易讀格式打印數據庫結構"""
    structure = inspect_database()
    
    for table_name, table_info in structure.items():
        print(f"\n表名: {table_name}")
        
        print("\n列:")
        for column in table_info["columns"]:
            print(f"  - {column['name']}: {column['type']}")
            print(f"    可空: {column['nullable']}, 默認值: {column['default']}")
        
        print(f"\n主鍵: {table_info['primary_keys']}")
        
        if table_info["foreign_keys"]:
            print("\n外鍵:")
            for fk in table_info["foreign_keys"]:
                print(f"  - {fk['constrained_columns']} -> {fk['referred_table']}.{fk['referred_columns']}")
        
        if table_info["indexes"]:
            print("\n索引:")
            for index in table_info["indexes"]:
                print(f"  - {index['name']}: {index['column_names']}")


def test_database_connection():
    """測試數據庫連接"""
    try:
        engine = create_engine(SQLALCHEMY_DATABASE_URL)
        with engine.connect() as connection:
            print("數據庫連接成功！")
            return True
    except Exception as e:
        print(f"數據庫連接失敗: {str(e)}")
        return False

if __name__ == "__main__":
    if test_database_connection():
        print_database_structure()