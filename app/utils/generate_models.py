from sqlalchemy import MetaData, inspect, Integer, Date
from sqlalchemy import create_engine
import os
from pathlib import Path
import inflect
from ..database import SQLALCHEMY_DATABASE_URL

p = inflect.engine()

def camel_case(snake_str):
    """將 snake_case 轉換為 CamelCase"""
    components = snake_str.split('_')
    return ''.join(x.title() for x in components)

def generate_model_file(table_name, table, inspector, output_dir):
    """為單個表生成模型文件"""
    class_name = camel_case(p.singular_noun(table_name) or table_name)
    
    # 生成導入語句
    imports = [
        "from sqlalchemy import Column, Integer, String, Float, Date, ForeignKey, DateTime",
        "from sqlalchemy.orm import relationship",
        "from .base import Base, TimeStampMixin",
        "\n"
    ]
    
    # 生成類定義
    class_def = [
        f"class {class_name}(Base, TimeStampMixin):",
        f"    __tablename__ = '{table_name}'",
        ""
    ]
    
    # 生成列定義
    columns = []
    for column in table.columns:
        col_type = str(column.type)
        # 簡化類型表示
        if 'INTEGER' in col_type:
            col_type = 'Integer'
        elif 'VARCHAR' in col_type:
            col_type = 'String'
        elif 'TIMESTAMP' in col_type:
            col_type = 'DateTime'
        elif 'DOUBLE PRECISION' in col_type or 'DOUBLE_PRECISION' in col_type:
            col_type = 'Float'
        elif 'DATE' in col_type:
            col_type = 'Date'
            
        # 構建列定義
        col_parts = []
        col_parts.append(col_type)
        
        if column.primary_key:
            col_parts.append('primary_key=True')
        if not column.nullable:
            col_parts.append('nullable=False')
            
        # 處理外鍵
        if column.foreign_keys:
            fk = next(iter(column.foreign_keys))
            col_parts.append(f"ForeignKey('{fk.target_fullname}')")
            
        col_def = f"    {column.name} = Column({', '.join(col_parts)})"
        columns.append(col_def)
    
    # 生成關係定義
    relationships = []
    fks = inspector.get_foreign_keys(table_name)
    
    # 處理外鍵關係
    for fk in fks:
        referred_table = fk['referred_table']
        referred_class = camel_case(p.singular_noun(referred_table) or referred_table)
        local_col = fk['constrained_columns'][0]
        rel_name = local_col.replace('_id', '')
        rel_def = f'    {rel_name} = relationship("{referred_class}", back_populates="{table_name}")'
        relationships.append(rel_def)
    
    # 處理多對多關係
    for other_table in inspector.get_table_names():
        if other_table.startswith('book_'):
            related_entity = other_table.replace('book_', '')
            if related_entity == table_name:
                continue
                
            related_class = camel_case(p.singular_noun(related_entity) or related_entity)
            rel_name = p.plural(related_entity)
            rel_def = f'    {rel_name} = relationship("{related_class}", secondary="{other_table}", back_populates="books")'
            relationships.append(rel_def)
    
    # 組合所有代碼
    code = imports + class_def + columns + ["\n"] + relationships + ["\n"]
    
    # 創建文件
    file_path = os.path.join(output_dir, f"{table_name}.py")
    with open(file_path, "w") as f:
        f.write("\n".join(code))
    
    return class_name

def generate_association_models(metadata, inspector, output_dir):
    """生成關聯表模型"""
    code = [
        "from sqlalchemy import Column, Integer, String, Float, Date, ForeignKey, DateTime, Table",
        "from .base import Base",
        "\n"
    ]
    
    for table_name in metadata.tables:
        if table_name.startswith('book_'):
            table = metadata.tables[table_name]
            table_def = [
                f"{table_name} = Table(",
                f"    '{table_name}',",
                "    Base.metadata,"
            ]
            
            for column in table.columns:
                col_type = str(column.type)
                # 簡化類型表示
                if 'INTEGER' in col_type:
                    col_type = 'Integer'
                elif 'VARCHAR' in col_type:
                    col_type = 'String'
                elif 'TIMESTAMP' in col_type:
                    col_type = 'DateTime'
                elif 'DOUBLE PRECISION' in col_type or 'DOUBLE_PRECISION' in col_type:
                    col_type = 'Float'
                elif 'DATE' in col_type:
                    col_type = 'Date'
                    
                if column.foreign_keys:
                    fk = next(iter(column.foreign_keys))
                    col_def = f"    Column('{column.name}', {col_type}, ForeignKey('{fk.target_fullname}'), primary_key=True),"
                else:
                    col_def = f"    Column('{column.name}', {col_type}, primary_key=True),"
                table_def.append(col_def)
            
            table_def.append(")")
            table_def.append("\n")
            code.extend(table_def)
    
    if len(code) > 3:  # 如果有關聯表定義
        with open(os.path.join(output_dir, "associations.py"), "w") as f:
            f.write("\n".join(code))

def generate_base_model(output_dir):
    """生成 base.py 文件"""
    code = [
        "from sqlalchemy.ext.declarative import declarative_base",
        "from sqlalchemy import Column, DateTime, func",
        "\n",
        "# 建立基礎的 declarative Base 類別",
        "Base = declarative_base()",
        "\n",
        "class TimeStampMixin:",
        '    """',
        '    時間戳混入類別，提供 created_at 和 updated_at 欄位',
        '    - created_at: 記錄資料建立時間，預設為當前資料庫時間',
        '    - updated_at: 記錄資料最後更新時間，當更新時自動更新為當前資料庫時間',
        '    """',
        "    created_at = Column(DateTime, nullable=False, default=func.now())",
        "    updated_at = Column(DateTime, nullable=False, default=func.now(), onupdate=func.now())",
        "\n"
    ]
    
    file_path = os.path.join(output_dir, "base.py")
    with open(file_path, "w") as f:
        f.write("\n".join(code))

def generate_models():
    """生成所有模型文件"""
    engine = create_engine(SQLALCHEMY_DATABASE_URL)
    inspector = inspect(engine)
    metadata = MetaData()
    metadata.reflect(bind=engine)
    
    # 獲取模型目錄路徑
    current_dir = Path(__file__).parent.parent
    models_dir = current_dir / "models"
    
    # 確保目錄存在
    models_dir.mkdir(exist_ok=True)
    
    # 首先生成 base.py
    generate_base_model(str(models_dir))
    
    # 生成 __init__.py
    init_content = ["from .base import Base, TimeStampMixin"]
    
    # 生成各個模型文件
    for table_name in metadata.tables:
        if not table_name.startswith('book_'):  # 跳過關聯表
            table = metadata.tables[table_name]
            class_name = generate_model_file(table_name, table, inspector, str(models_dir))
            if class_name:
                init_content.append(f"from .{table_name} import {class_name}")
    
    # 生成關聯表模型
    generate_association_models(metadata, inspector, str(models_dir))
    init_content.append("from .associations import *")
    
    # 更新 __init__.py
    with open(models_dir / "__init__.py", "w") as f:
        f.write("\n".join(init_content))
        f.write("\n\n__all__ = [")
        for line in init_content[1:]:
            if "from ." in line:
                module = line.split("import ")[1]
                f.write(f"\n    '{module}',")
        f.write("\n]\n")

if __name__ == "__main__":
    generate_models() 