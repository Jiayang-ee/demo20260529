"""基金白名单配置"""
from datetime import date

FUND_WHITELIST: list[dict] = [
    {"code": "000001", "name": "华夏成长混合", "type": "混合型"},
    {"code": "000021", "name": "华夏优势增长混合", "type": "混合型"},
    {"code": "000083", "name": "汇添富消费行业混合", "type": "混合型"},
    {"code": "000263", "name": "工银信息产业混合A", "type": "混合型"},
    {"code": "000336", "name": "农银研究精选混合", "type": "混合型"},
    {"code": "000478", "name": "建信中证500指数增强A", "type": "指数型"},
    {"code": "000596", "name": "前海开源中证军工指数A", "type": "指数型"},
    {"code": "001054", "name": "工银新金融股票A", "type": "股票型"},
    {"code": "001410", "name": "信澳新能源产业股票", "type": "股票型"},
    {"code": "110011", "name": "易方达中小盘混合", "type": "混合型"},
    {"code": "012922", "name": "易方达全球成长精选混合(QDII)C", "type": "QDII"},
]

DATA_DIR = "data/funds"