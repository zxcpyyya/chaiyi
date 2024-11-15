<<<<<<< HEAD
import os
from datetime import timedelta


class Config:
    # Flask配置
    SESSION_COOKIE_SECURE = True
    PERMANENT_SESSION_LIFETIME = timedelta(minutes=30)

    # 数据库配置
    MYSQL_HOST = os.getenv("MYSQL_HOST", "localhost")
    MYSQL_USER = os.getenv("MYSQL_USER", "root")
    MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD", "ldf052821")
    MYSQL_DB = os.getenv("MYSQL_DB", "xiaodachuang")

    # 邮件服务器配置
    SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.qq.com")
    SMTP_USER = os.getenv("SMTP_USER", "206284929@qq.com")
    SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "ztznowgbfxxnbiei")

    # Redis配置
    REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
=======
from datetime import timedelta
import os


class Config:
      SESSION_COOKIE_SECURE = True
      PERMANENT_SESSION_LIFETIME = timedelta(minutes=30)

      # 数据库配置
      MYSQL_HOST = os.getenv("MYSQL_HOST", "localhost")
      MYSQL_USER = os.getenv("MYSQL_USER", "root")
      MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD", "ldf052821")
      MYSQL_DB = os.getenv("MYSQL_DB", "xiaodachuang")

      # 邮件服务器配置
      SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.qq.com")
      SMTP_USER = os.getenv("SMTP_USER", "206284929@qq.com")
      SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "ztznowgbfxxnbiei")

      # Redis配置
      REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
>>>>>>> origin/main
