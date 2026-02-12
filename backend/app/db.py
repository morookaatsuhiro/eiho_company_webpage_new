"""
数据库配置和连接管理
"""
import os
from sqlalchemy import create_engine, inspect
from sqlalchemy.orm import sessionmaker, declarative_base

# 支持环境变量配置数据库 URL（生产环境可用 PostgreSQL）
# Vercel 的只读文件系统会导致本地 sqlite 写入失败，默认改用 /tmp。
def _default_database_url() -> str:
    if os.getenv("VERCEL") == "1" or os.getenv("VERCEL_ENV"):
        return "sqlite:////tmp/eiho.db"
    return "sqlite:///./eiho.db"


DATABASE_URL = os.getenv("DATABASE_URL", _default_database_url())

# SQLite 需要 check_same_thread=False，PostgreSQL/MySQL 不需要
connect_args = {}
if DATABASE_URL.startswith("sqlite"):
    connect_args = {"check_same_thread": False}

engine = create_engine(
    DATABASE_URL,
    connect_args=connect_args,
    # 生产环境建议开启连接池
    pool_pre_ping=True,  # 连接前检查连接是否有效
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def ensure_homepage_nav_columns() -> None:
    """为已有数据库补齐导航栏新增字段。"""
    inspector = inspect(engine)
    table_names = set(inspector.get_table_names())
    if "homepage" not in table_names:
        return

    columns = {col["name"] for col in inspector.get_columns("homepage")}
    need_concept = "nav_concept_text" not in columns
    need_news = "nav_news_text" not in columns
    if not (need_concept or need_news):
        return

    is_sqlite = DATABASE_URL.startswith("sqlite")
    is_postgres = DATABASE_URL.startswith("postgresql")

    with engine.begin() as conn:
        if is_postgres:
            # PostgreSQL: 使用 IF NOT EXISTS，避免并发冷启动时重复添加失败
            conn.exec_driver_sql(
                "ALTER TABLE homepage ADD COLUMN IF NOT EXISTS nav_concept_text VARCHAR(100) DEFAULT 'メッセージ'"
            )
            conn.exec_driver_sql(
                "ALTER TABLE homepage ADD COLUMN IF NOT EXISTS nav_news_text VARCHAR(100) DEFAULT 'ニュース'"
            )
            return

        if is_sqlite:
            # SQLite: 不支持 IF NOT EXISTS，先检查后执行
            if need_concept:
                conn.exec_driver_sql(
                    "ALTER TABLE homepage ADD COLUMN nav_concept_text VARCHAR(100) DEFAULT 'メッセージ'"
                )
            if need_news:
                conn.exec_driver_sql(
                    "ALTER TABLE homepage ADD COLUMN nav_news_text VARCHAR(100) DEFAULT 'ニュース'"
                )
            return

        # 其他数据库尽量兼容：先检查后添加
        if need_concept:
            conn.exec_driver_sql(
                "ALTER TABLE homepage ADD COLUMN nav_concept_text VARCHAR(100) DEFAULT 'メッセージ'"
            )
        if need_news:
            conn.exec_driver_sql(
                "ALTER TABLE homepage ADD COLUMN nav_news_text VARCHAR(100) DEFAULT 'ニュース'"
            )


def get_db():
    """数据库会话依赖注入"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
