from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, DateTime, func


# 建立基礎的 declarative Base 類別
Base = declarative_base()


class TimeStampMixin:
    """
    時間戳混入類別，提供 created_at 和 updated_at 欄位
    - created_at: 記錄資料建立時間，預設為當前資料庫時間
    - updated_at: 記錄資料最後更新時間，當更新時自動更新為當前資料庫時間
    """
    created_at = Column(DateTime, nullable=False, default=func.now())
    updated_at = Column(DateTime, nullable=False, default=func.now(), onupdate=func.now())

