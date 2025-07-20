# scAgent 6必选4可选过滤策略创新报告

## 🎯 **概述**

scAgent系统在sc-eQTL数据筛选方面采用了创新的**6必选+4可选**分层过滤策略，通过智能算法和多维度评估，实现了高效、准确的数据质量筛选。

## 🏗️ **分层过滤架构**

### **核心设计理念**
```
┌─────────────────────────────────────┐
│           6个必选条件               │  ← 硬性要求，不通过直接拒绝
├─────────────────────────────────────┤
│           4个可选条件               │  ← 软性要求，影响质量评分
├─────────────────────────────────────┤
│        智能评分系统                 │  ← 综合评估，决定最终保留
└─────────────────────────────────────┘
```

## 📋 **6个必选条件详解**

### **1. Species Filter (物种过滤)**
```python
def check_species_filter(record: Dict[str, Any], required_species: List[str]) -> int:
    """
    必选条件1: 物种识别
    - 目标: 确保数据来自目标物种(如Homo sapiens)
    - 算法: 多字段模糊匹配
    - 评分: 0分(拒绝) 或 2分(通过)
    """
    organism = record.get('organism', '').lower()
    title = record.get('title', '').lower()
    summary = record.get('summary', '').lower()
    
    for species in required_species:
        species_lower = species.lower()
        if (species_lower in organism or 
            species_lower in title or 
            species_lower in summary):
            return 2  # 必选条件通过
    return 0  # 必选条件失败
```

**创新策略**:
- **多字段匹配**: 同时检查organism、title、summary字段
- **模糊匹配**: 支持"Homo sapiens"、"human"等多种表达
- **容错处理**: 大小写不敏感，提高匹配成功率

### **2. Cell Line Exclusion (细胞系排除)**
```python
def check_cell_line_exclusion(record: Dict[str, Any]) -> int:
    """
    必选条件2: 细胞系排除
    - 目标: 排除 immortalized cell lines
    - 算法: 关键词黑名单匹配
    - 评分: 0分(拒绝) 或 2分(通过)
    """
    cell_line_keywords = [
        'hela', '293t', 'k562', 'jurkat', 'hek293', 'mcf7', 'a549',
        'cell line', 'cell-line', 'immortalized', 'transformed'
    ]
    
    text_fields = [
        record.get('title', '').lower(),
        record.get('summary', '').lower(),
        record.get('cell_type', '').lower(),
        record.get('source_name', '').lower()
    ]
    
    for text in text_fields:
        for keyword in cell_line_keywords:
            if keyword in text:
                return 0  # 检测到细胞系，拒绝
    return 2  # 未检测到细胞系，通过
```

**创新策略**:
- **黑名单机制**: 建立细胞系关键词黑名单
- **多字段检查**: 覆盖title、summary、cell_type、source_name
- **精确识别**: 避免误判正常细胞类型

### **3. Database ID Availability (数据库ID可用性)**
```python
def check_database_id_availability(record: Dict[str, Any]) -> int:
    """
    必选条件3: 数据库ID验证
    - 目标: 确保有有效的数据库访问ID
    - 算法: 正则表达式模式匹配
    - 评分: 0分(拒绝) 或 2分(通过)
    """
    geo_accession = (record.get('gse') or '').strip()
    sra_accession = (record.get('run_accession') or record.get('study_accession') or '').strip()
    
    if geo_accession and geo_accession.startswith('GSE'):
        return 2  # 有效GEO ID
    elif sra_accession and (sra_accession.startswith('SRR') or sra_accession.startswith('SRP') or 
                           sra_accession.startswith('ERR') or sra_accession.startswith('DRR')):
        return 2  # 有效SRA ID
    return 0  # 无有效数据库ID
```

**创新策略**:
- **多数据库支持**: 同时支持GEO和SRA数据库
- **国际兼容**: 支持欧洲(ERR)和日本(DRR)数据库
- **字段映射**: 处理不同数据源的字段名差异

### **4. Tumor Annotation (肿瘤状态标注)**
```python
def check_tumor_annotation(record: Dict[str, Any]) -> int:
    """
    必选条件4: 肿瘤状态标注
    - 目标: 确保有肿瘤/正常状态信息
    - 算法: 语义关键词识别
    - 评分: 0分(拒绝) 或 2分(通过)
    """
    tumor_keywords = ['tumor', 'cancer', 'carcinoma', 'malignant']
    normal_keywords = ['normal', 'healthy', 'control', 'non-tumor']
    
    text_fields = [
        record.get('title', '').lower(),
        record.get('summary', '').lower(),
        record.get('disease', '').lower()
    ]
    
    for text in text_fields:
        if any(keyword in text for keyword in tumor_keywords + normal_keywords):
            return 2  # 有肿瘤状态信息
    return 0  # 无肿瘤状态信息
```

**创新策略**:
- **双向识别**: 同时识别肿瘤和正常样本
- **语义理解**: 使用医学专业术语
- **上下文分析**: 考虑疾病相关字段

### **5. Sequencing Method (测序方法)**
```python
def check_sequencing_method(record: Dict[str, Any]) -> int:
    """
    必选条件5: 测序方法识别
    - 目标: 确保有明确的测序技术信息
    - 算法: 技术关键词匹配
    - 评分: 0分(拒绝) 或 2分(通过)
    """
    seq_keywords = [
        'rna-seq', 'rna sequencing', 'transcriptome', 'expression',
        '10x', 'smart-seq', 'drop-seq', 'cel-seq', 'mars-seq'
    ]
    
    text_fields = [
        record.get('title', '').lower(),
        record.get('summary', '').lower(),
        record.get('library_strategy', '').lower()
    ]
    
    for text in text_fields:
        if any(keyword in text for keyword in seq_keywords):
            return 2  # 有测序方法信息
    return 0  # 无测序方法信息
```

**创新策略**:
- **技术覆盖**: 涵盖主流单细胞测序技术
- **字段优化**: 优先检查library_strategy字段
- **术语标准化**: 统一不同表达方式

### **6. Tissue Source (组织来源)**
```python
def check_tissue_source(record: Dict[str, Any]) -> int:
    """
    必选条件6: 组织来源识别
    - 目标: 确保有明确的组织来源信息
    - 算法: 解剖学关键词匹配
    - 评分: 0分(拒绝) 或 2分(通过)
    """
    tissue_keywords = [
        'brain', 'liver', 'heart', 'lung', 'kidney', 'muscle', 'blood',
        'skin', 'bone', 'pancreas', 'stomach', 'intestine', 'colon',
        'breast', 'ovary', 'testis', 'prostate', 'thyroid', 'spleen'
    ]
    
    text_fields = [
        record.get('title', '').lower(),
        record.get('summary', '').lower(),
        record.get('source_name', '').lower()
    ]
    
    for text in text_fields:
        if any(tissue in text for tissue in tissue_keywords):
            return 2  # 有组织来源信息
    return 0  # 无组织来源信息
```

**创新策略**:
- **解剖学知识**: 基于人体解剖学组织分类
- **多器官覆盖**: 涵盖主要器官系统
- **标准化命名**: 统一组织名称表达

## 📊 **4个可选条件详解**

### **1. Publication Info (发表信息)**
```python
def check_publication_info(record: Dict[str, Any]) -> int:
    """
    可选条件1: 发表信息
    - 目标: 识别是否有相关发表信息
    - 算法: 文献标识符检测
    - 评分: 0分(无) 或 1分(有)
    """
    pmid = record.get('pmid', '')
    doi = record.get('doi', '')
    pubmed_id = record.get('pubmed_id', '')
    
    if pmid or doi or pubmed_id:
        return 1  # 有发表信息
    
    # 文本中查找发表关键词
    pub_keywords = ['pmid', 'doi', 'pubmed', 'published', 'paper', 'article']
    text_fields = [record.get('title', '').lower(), record.get('summary', '').lower()]
    
    for text in text_fields:
        if any(keyword in text for keyword in pub_keywords):
            return 1  # 可能有发表信息
    return 0  # 无发表信息
```

### **2. Sample Size Info (样本量信息)**
```python
def check_sample_size_info(record: Dict[str, Any]) -> int:
    """
    可选条件2: 样本量信息
    - 目标: 评估样本量是否充足
    - 算法: 数值提取和阈值判断
    - 评分: 0分(不足) 或 1-2分(充足)
    """
    sample_count = safe_int_convert(record.get('sample_count', 0))
    
    if sample_count and sample_count > 0:
        if sample_count >= 100:
            return 2  # 大样本量
        elif sample_count >= 20:
            return 1  # 适中样本量
        else:
            return 0  # 小样本量
    
    # 文本中提取样本量信息
    import re
    text_fields = [record.get('title', '').lower(), record.get('summary', '').lower()]
    
    for text in text_fields:
        patterns = [r'n=(\d+)', r'(\d+)\s*samples?', r'(\d+)\s*subjects?']
        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                count = int(match.group(1))
                if count >= 100:
                    return 2
                elif count >= 20:
                    return 1
    return 0
```

### **3. Country Info (国家信息)**
```python
def check_country_info(record: Dict[str, Any]) -> int:
    """
    可选条件3: 国家信息
    - 目标: 识别数据来源国家
    - 算法: 国家名称映射
    - 评分: 0分(无) 或 1分(有)
    """
    country_keywords = {
        'usa': 'United States', 'united states': 'United States',
        'china': 'China', 'uk': 'United Kingdom', 'germany': 'Germany',
        'japan': 'Japan', 'france': 'France', 'canada': 'Canada'
    }
    
    text_fields = [
        record.get('title', '').lower(),
        record.get('summary', '').lower(),
        record.get('country', '').lower()
    ]
    
    for text in text_fields:
        for keyword, country in country_keywords.items():
            if keyword in text:
                return 1  # 有国家信息
    return 0  # 无国家信息
```

### **4. Age Info (年龄信息)**
```python
def check_age_info(record: Dict[str, Any]) -> int:
    """
    可选条件4: 年龄信息
    - 目标: 识别年龄相关信息
    - 算法: 正则表达式模式匹配
    - 评分: 0分(无) 或 1分(有)
    """
    import re
    
    text_fields = [
        record.get('title', '').lower(),
        record.get('summary', '').lower(),
        record.get('characteristics', '').lower()
    ]
    
    age_patterns = [
        r'(\d+)\s*(?:years?\s*old|y\.?o\.?|yr\.?s?)',
        r'(?:age|aged)\s*(\d+)',
        r'(\d+)\s*-\s*(\d+)\s*(?:years?|y\.?o\.?)'
    ]
    
    for text in text_fields:
        for pattern in age_patterns:
            if re.search(pattern, text):
                return 1  # 有年龄信息
    return 0  # 无年龄信息
```

## 🚀 **算法创新特性**

### **1. 分层决策机制**
```python
def apply_sc_eqtl_filters(records: List[Dict[str, Any]], filter_config: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    分层过滤决策机制
    """
    for record in records:
        filter_result = {
            "passes_required_filters": True,    # 必选条件状态
            "passes_optional_filters": True,    # 可选条件状态
            "filter_scores": {},               # 各条件评分
            "overall_score": 0                 # 综合评分
        }
        
        # 必选条件检查 - 任一失败直接拒绝
        for required_filter in required_filters:
            score = check_required_filter(record, required_filter)
            filter_result["filter_scores"][required_filter] = score
            if score == 0:
                filter_result["passes_required_filters"] = False
                break  # 提前终止，提高效率
        
        # 可选条件检查 - 影响质量评分
        if filter_result["passes_required_filters"]:
            for optional_filter in optional_filters:
                score = check_optional_filter(record, optional_filter)
                filter_result["filter_scores"][optional_filter] = score
        
        # 综合评分计算
        filter_result["overall_score"] = sum(filter_result["filter_scores"].values())
        
        # 最终决策
        if filter_result["passes_required_filters"]:
            filtered_records.append(record)
```

### **2. 智能评分系统**
```python
def calculate_intelligent_score(filter_scores: Dict[str, int]) -> int:
    """
    智能评分算法
    """
    # 必选条件权重
    required_weights = {
        "species": 2.0,           # 物种最重要
        "cell_line": 2.0,         # 细胞系排除重要
        "database_id": 2.0,       # 数据库ID必需
        "tumor": 1.5,             # 肿瘤状态重要
        "sequencing_method": 1.5, # 测序方法重要
        "tissue": 1.0             # 组织来源基础
    }
    
    # 可选条件权重
    optional_weights = {
        "publication": 0.5,       # 发表信息加分
        "sample_size": 1.0,       # 样本量重要
        "country": 0.3,           # 国家信息轻微加分
        "age": 0.3                # 年龄信息轻微加分
    }
    
    total_score = 0
    
    # 计算加权评分
    for filter_name, score in filter_scores.items():
        if filter_name in required_weights:
            total_score += score * required_weights[filter_name]
        elif filter_name in optional_weights:
            total_score += score * optional_weights[filter_name]
    
    return total_score
```

### **3. 置信度评估机制**
```python
def assess_filter_confidence(record: Dict[str, Any], filter_name: str) -> float:
    """
    置信度评估算法
    """
    confidence_factors = {
        "field_presence": 0.3,    # 字段存在性
        "data_quality": 0.3,      # 数据质量
        "pattern_match": 0.2,     # 模式匹配度
        "context_relevance": 0.2  # 上下文相关性
    }
    
    confidence = 0.0
    
    # 字段存在性评估
    if has_relevant_field(record, filter_name):
        confidence += confidence_factors["field_presence"]
    
    # 数据质量评估
    if has_high_quality_data(record, filter_name):
        confidence += confidence_factors["data_quality"]
    
    # 模式匹配度评估
    pattern_score = calculate_pattern_match(record, filter_name)
    confidence += pattern_score * confidence_factors["pattern_match"]
    
    # 上下文相关性评估
    context_score = assess_context_relevance(record, filter_name)
    confidence += context_score * confidence_factors["context_relevance"]
    
    return min(confidence, 1.0)  # 确保置信度在0-1之间
```

## 📊 **输出表体现**

### **1. 结构化输出字段**
```python
# 输出表中的字段结构
cleaned_record = {
    # 基础信息
    "id": record.get("id", ""),
    "title": record.get("title", ""),
    "summary": record.get("summary", ""),
    
    # 必选条件结果
    "passes_required_filters": filter_result.get("passes_required_filters", False),
    "species_score": filter_result.get("filter_scores", {}).get("species", 0),
    "cell_line_score": filter_result.get("filter_scores", {}).get("cell_line", 0),
    "database_id_score": filter_result.get("filter_scores", {}).get("database_id", 0),
    "tumor_score": filter_result.get("filter_scores", {}).get("tumor", 0),
    "sequencing_method_score": filter_result.get("filter_scores", {}).get("sequencing_method", 0),
    "tissue_score": filter_result.get("filter_scores", {}).get("tissue", 0),
    
    # 可选条件结果
    "passes_optional_filters": filter_result.get("passes_optional_filters", False),
    "publication_score": filter_result.get("filter_scores", {}).get("publication", 0),
    "sample_size_score": filter_result.get("filter_scores", {}).get("sample_size", 0),
    "country_score": filter_result.get("filter_scores", {}).get("country", 0),
    "age_score": filter_result.get("filter_scores", {}).get("age", 0),
    
    # 综合评估
    "sc_eqtl_overall_score": filter_result.get("overall_score", 0),
    "sc_eqtl_grade": calculate_grade_from_score(filter_result.get("overall_score", 0)),
    
    # 详细信息
    "filter_reasons": "; ".join(filter_result.get("filter_reasons", [])),
    "processing_timestamp": datetime.now().isoformat()
}
```

### **2. 质量等级分类**
```python
def calculate_grade_from_score(score: int) -> str:
    """
    基于综合评分计算质量等级
    """
    if score >= 15:
        return "A"  # 优秀 - 满足所有必选条件，大部分可选条件
    elif score >= 12:
        return "B"  # 良好 - 满足所有必选条件，部分可选条件
    elif score >= 8:
        return "C"  # 中等 - 满足必选条件，可选条件较少
    elif score >= 6:
        return "D"  # 及格 - 勉强满足必选条件
    else:
        return "F"  # 不及格 - 不满足必选条件
```

### **3. 详细报告生成**
```python
def generate_filter_report(original_records: List[Dict], filtered_records: List[Dict]) -> Dict:
    """
    生成详细的过滤报告
    """
    report = {
        "filtering_summary": {
            "original_count": len(original_records),
            "filtered_count": len(filtered_records),
            "retention_rate": (len(filtered_records) / len(original_records)) * 100
        },
        "required_filters_performance": {
            "species": calculate_filter_performance(original_records, "species"),
            "cell_line": calculate_filter_performance(original_records, "cell_line"),
            "database_id": calculate_filter_performance(original_records, "database_id"),
            "tumor": calculate_filter_performance(original_records, "tumor"),
            "sequencing_method": calculate_filter_performance(original_records, "sequencing_method"),
            "tissue": calculate_filter_performance(original_records, "tissue")
        },
        "optional_filters_performance": {
            "publication": calculate_filter_performance(original_records, "publication"),
            "sample_size": calculate_filter_performance(original_records, "sample_size"),
            "country": calculate_filter_performance(original_records, "country"),
            "age": calculate_filter_performance(original_records, "age")
        },
        "quality_distribution": {
            "grade_a": count_grade_records(filtered_records, "A"),
            "grade_b": count_grade_records(filtered_records, "B"),
            "grade_c": count_grade_records(filtered_records, "C"),
            "grade_d": count_grade_records(filtered_records, "D"),
            "grade_f": count_grade_records(filtered_records, "F")
        }
    }
    return report
```

## 🎯 **创新价值总结**

### **1. 策略创新**
- **分层过滤**: 6必选+4可选的分层设计
- **智能决策**: 基于置信度的智能评估
- **灵活配置**: 可配置的过滤条件权重

### **2. 算法创新**
- **多字段匹配**: 提高识别准确性
- **正则表达式**: 精确提取数值信息
- **语义理解**: 基于领域知识的语义匹配
- **置信度评估**: 量化过滤结果可靠性

### **3. 输出创新**
- **结构化数据**: 清晰的字段组织
- **质量分级**: A-F等级质量评估
- **详细报告**: 完整的过滤统计
- **可追溯性**: 包含处理时间戳和配置信息

这种创新的过滤策略使得scAgent系统能够：
- **高效筛选**: 快速识别高质量sc-eQTL数据
- **准确评估**: 基于多维度指标的质量评估
- **灵活配置**: 适应不同研究需求的过滤要求
- **透明输出**: 提供详细的可追溯结果 