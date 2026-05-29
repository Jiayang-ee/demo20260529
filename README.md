# Fund Backtest API

基金定投回测工具后端服务。

## 快速开始

```bash
pip install -r requirements.txt
uvicorn app.main:app --reload
```

## API 端点

- `GET /api/funds` - 基金列表
- `POST /api/funds/sync` - 同步净值
- `POST /api/backtest` - 回测

## 测试

```bash
pytest tests/ -v
```