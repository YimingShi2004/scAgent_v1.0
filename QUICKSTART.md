# scAgent 快速开始指南

## 1. 安装

```bash
# 克隆项目
cd scAgent

# 运行安装脚本
./install.sh

# 或手动安装
python3 -m venv .venv
source .venv/bin/activate
pip install -e .
```

## 2. 配置

scAgent 使用以下默认配置：

- **数据库**: `10.28.1.24:5432`
- **用户**: `yanglab`
- **密码**: `labyang`
- **模型API**: `http://10.28.1.21:30080/v1`
- **模型**: `Qwen3-235B-A22B`

如需修改配置，编辑 `scAgent/settings.yml` 文件。

## 3. 测试连接

```bash
# 激活虚拟环境
source .venv/bin/activate

# 运行测试脚本
python test_scagent.py

# 或使用CLI测试
scagent test-connection
```

## 4. 基本使用

### 分析数据库结构

```bash
# 分析表结构
scagent analyze-schema

# 分析特定表
scagent analyze-schema --tables geo_master

# 导出结构报告
scagent analyze-schema --output schema_report.txt
```

### 分析 GEO 数据

```bash
# 分析 geo_master 表
scagent analyze-geo --max-records 100

# 按物种过滤
scagent analyze-geo --organisms "Homo sapiens" "Mus musculus"

# 导出结果
scagent analyze-geo --output geo_analysis.csv
```

### 分析 SRA 数据

```bash
# 分析 sra_master 表
scagent analyze-sra --max-records 100

# 按平台过滤
scagent analyze-sra --platforms "Illumina HiSeq 2500"

# 导出结果
scagent analyze-sra --output sra_analysis.csv
```

### 寻找 sc-eQTL 适合的数据

```bash
# 寻找单细胞数据
scagent find-eqtl-data --max-datasets 50

# 按物种和组织过滤
scagent find-eqtl-data --organisms "Homo sapiens" --tissues "brain" "heart"

# 导出为不同格式
scagent find-eqtl-data --output eqtl_datasets.xlsx --format excel
```

### 数据清洗

```bash
# 清洗 geo_master 数据
scagent clean-data --table geo_master --output cleaned_geo.csv

# 清洗 sra_master 数据
scagent clean-data --table sra_master --output cleaned_sra.json --format json
```

## 5. 高级功能

### 使用 Python API

```python
from scAgent.db import get_table_info, query_geo_master
from scAgent.models import get_qwen_client

# 获取表信息
table_info = get_table_info(["geo_master", "sra_master"])

# 查询数据
results = query_geo_master(limit=10, conditions={"organism": "Homo sapiens"})

# 使用AI分析
client = get_qwen_client()
response = client.generate("分析这些数据的质量...")
```

### 自定义查询

```python
from scAgent.db.query import execute_query

# 执行自定义SQL查询
results = execute_query("""
    SELECT geo_accession, title, organism 
    FROM geo_master 
    WHERE title ILIKE '%single cell%' 
    LIMIT 10
""")
```

## 6. 输出格式

scAgent 支持多种输出格式：

- **CSV**: 默认格式，适合 Excel 打开
- **JSON**: 结构化数据，适合程序处理
- **Excel**: .xlsx 格式，适合复杂分析

## 7. 故障排除

### 数据库连接问题

```bash
# 检查网络连接
ping 10.28.1.24

# 检查端口
telnet 10.28.1.24 5432

# 测试连接
scagent test-connection --db-only
```

### 模型API连接问题

```bash
# 检查API端点
curl http://10.28.1.21:30080/v1/chat/completions

# 测试连接
scagent test-connection --model-only
```

### 常见错误

1. **导入错误**: 确保已激活虚拟环境
2. **权限错误**: 检查数据库用户权限
3. **网络超时**: 检查防火墙设置

## 8. 性能优化

- 使用 `--max-records` 限制查询数量
- 对大表使用条件过滤
- 批量处理大量数据时使用较小的 chunk_size

## 9. 获取帮助

```bash
# 查看所有命令
scagent --help

# 查看特定命令帮助
scagent find-eqtl-data --help
```

## 10. 示例工作流

```bash
# 1. 测试连接
scagent test-connection

# 2. 分析数据库结构
scagent analyze-schema --output schema_report.txt

# 3. 寻找人类脑组织的单细胞数据
scagent find-eqtl-data \
    --organisms "Homo sapiens" \
    --tissues "brain" \
    --max-datasets 20 \
    --output brain_datasets.csv

# 4. 分析找到的数据质量
scagent analyze-geo \
    --organisms "Homo sapiens" \
    --max-records 1000 \
    --output geo_analysis.csv

# 5. 清洗数据
scagent clean-data \
    --table geo_master \
    --max-records 1000 \
    --output cleaned_data.csv
```

这样就完成了一个完整的 sc-eQTL 数据筛选工作流！ 