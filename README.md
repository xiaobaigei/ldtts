# SQL-Pilot: LLM-Driven Text-to-SQL with Schema-Aware Prompt Optimization

## 📋 项目概述

本项目实现了一个**智能模型驱动的 Text-to-SQL 系统**，通过结构化 Pipeline 引导大语言模型（LLM）生成准确的 SQL 查询。项目对比了"智能模型驱动方法"与"纯大模型工具方法"的性能差异。

## 🎯 选题情况

### 选题名称
**LLM-Driven Text-to-SQL with Schema-Aware Prompt Optimization**

### 选题背景
Text-to-SQL 是经典的 NLP+SE 交叉研究课题，核心任务是将自然语言问题自动转化为可执行的 SQL 查询。

### 研究价值
- **领域成熟度高**：有大量公开基准数据集（Spider、WikiSQL、BIRD）
- **LLM 提升显著**：但现有方法在复杂跨表查询、Schema 理解方面仍有瓶颈
- **改进空间大**：结合 Schema-aware 提示优化和检索增强生成（RAG）是当前研究热点

---

## 🧠 智能模型驱动方法

### 核心思想
不同于简单地让 LLM 一次性生成 SQL，本系统设计了结构化 Pipeline：

```
用户问题 + 数据库 Schema
        |
        v
[1. Schema Linking] --> 精简后的相关表和列
        |
        v
[2. 复杂度评估 + 自适应检索] --> 难度匹配的 few-shot 示例
        |
        v
[3. 结构化 Prompt 组装]
        |
        v
[4. LLM 生成 SQL + 自我修正]
        |
        v
[5. 多模型集成投票] --> 最终 SQL
```

### 对比：智能驱动 vs 纯大模型工具

| 维度 | 纯大模型工具方法 | 智能模型驱动方法 |
|------|-----------------|-----------------|
| **输入方式** | 完整 Schema + 问题 | 精简 Schema + 示例 + 问题 |
| **生成方式** | 单次生成 | 多阶段生成 + 自我修正 |
| **Schema 理解** | 被动接收 | 主动链接 + 消歧 |
| **示例选择** | 固定或随机 | 自适应难度匹配 |
| **错误处理** | 无 | 执行验证 + 自动修正 |
| **复杂度感知** | 无 | 动态调整示例数量 |

---

## 🔧 技术实现细节

### 技术栈
- **Python 3.10+**
- **DeepSeek API**（SQL 生成）
- **LangChain**（LLM 调用）
- **pytest**（测试框架）
- **SQLite**（SQL 执行验证）

### 核心模块

| 模块 | 文件 | 功能 |
|------|------|------|
| **Schema Linking** | `src/schema_linker.py` | 从问题中识别相关表和列 |
| **复杂度评估** | `src/complexity_estimator.py` | 判断问题难度（easy/medium/hard/extra） |
| **自适应检索** | `src/retriever.py` | 根据难度检索匹配的示例 |
| **SQL 生成** | `src/sql_generator.py` | 调用 LLM 生成 SQL + 自我修正 |
| **多模型集成** | `src/ensemble.py` | 多个模型投票选最佳结果 |
| **评估指标** | `src/evaluator.py` | 计算 EX/ESM/CM 指标 |
| **完整 Pipeline** | `src/pipeline.py` | 整合所有模块 |

### 关键技术点

#### 1. Schema Linking
- 使用 Jaccard 相似度匹配实体
- LLM 辅助消歧，输出 JSON 格式
- 自动补全外键关联的表

#### 2. 自适应检索
- 根据问题复杂度动态决定示例数量：
  - easy: 1 个示例
  - medium: 3 个示例
  - hard: 5 个示例
  - extra: 7 个示例
- 示例复杂度与当前问题匹配

#### 3. 自我修正循环
- 生成的 SQL 在 SQLite 中执行验证
- 如果出错，将错误信息反馈给 LLM
- 最多 3 次修正尝试

---

## 📊 实验评估

### 实验设置
- **数据集**：Spider 数据集（10,181 条 NL-SQL 对）
- **划分**：训练集 6000 / 验证集 1000 / 测试集 1034
- **评估指标**：
  - **EX**：执行准确率（Execution Accuracy）
  - **ESM**：精确集合匹配（Exact Set Match）
  - **CM**：组件匹配（Component Matching）

### 对比实验设计

| 条件 | 方法描述 |
|------|---------|
| **A（Baseline）** | 纯 LLM 零样本，直接输入完整 Schema |
| **B（Baseline）** | 纯 LLM + 固定 3 个示例 |
| **C（本系统）** | Schema Linking + 自适应检索 + 结构化提示 |
| **D** | C + 自我修正循环 |
| **E** | D + 多模型集成投票 |

### 预期结果
- 纯 LLM 零样本 EX ≈ 70-75%
- 智能驱动方法预期提升 5-10 个百分点
- 复杂多表查询改善更显著

---

## 🧪 测试用例

### 测试文件结构

```
tests/
├── test_schema_linker.py    # Schema Linking 单元测试
├── test_retriever.py        # 自适应检索单元测试
├── test_generator.py        # SQL 生成单元测试
├── test_evaluator.py        # 评估指标单元测试
├── test_ensemble.py         # 多模型集成单元测试
├── test_e2e.py              # 端到端集成测试（5个核心案例）
└── test_ablation.py         # 消融实验测试
```

### 端到端测试案例

| 案例 | 难度 | 问题描述 |
|------|------|---------|
| **Case 1** | Medium | 列出在 Research 部门且工资 > 50000 的员工 |
| **Case 2** | Hard | 显示计算机科学专业 GPA 最高的学生 |
| **Case 3** | Extra | 找出平均工资高于总体平均且员工数 ≥5 的部门 |
| **Case 4** | Medium | 列出教授数量 >3 的部门 |
| **Case 5** | Medium | 显示每个学生选课数量并排序 |

### 如何运行测试

#### 方式 1：直接运行 Python 脚本
```powershell
# 进入项目目录
cd text-to-sql-llm

# 运行端到端测试
python tests/test_e2e.py

# 运行消融实验
python tests/test_ablation.py

# 运行 Schema Linking 测试
python tests/test_schema_linker.py
```

#### 方式 2：使用 pytest（推荐）
```powershell
# 安装 pytest
pip install pytest

# 运行所有测试
python -m pytest tests/ -v

# 运行指定测试文件
python -m pytest tests/test_e2e.py -v

# 运行指定测试函数
python -m pytest tests/test_e2e.py::TestEndToEnd::test_case_study_1_join -v
```

#### 方式 3：使用 Makefile（Linux/Mac）
```bash
# 运行所有测试
make test

# 运行集成测试
make test-e2e

# 运行消融实验
make test-ablation
```

---

## 🚀 快速开始

### 环境要求
- Python 3.10+
- DeepSeek API Key（可选，完整演示需要）

### 安装依赖
```powershell
cd text-to-sql-llm
pip install -r requirements.txt
```

### 配置 API Key

1. 访问 https://platform.deepseek.com/ 获取 API Key
2. 创建 `.env` 文件：
```
DEEPSEEK_API_KEY=sk-your-api-key-here
```

### 运行演示

#### 简单演示（无需 API Key）
```powershell
python demo_simple.py
```

#### 完整演示（需要 API Key）
```powershell
python demo.py
```

---

## 🔄 CI/CD 配置

### GitHub Actions 工作流

项目配置了自动测试流程，位于 `.github/workflows/ci.yml`：

**触发条件**：
- 每次 push 到 main/master 分支
- 每次 pull request

**执行步骤**：
1. **代码格式检查**：black --check
2. **代码质量检查**：flake8
3. **单元测试**：pytest + 覆盖率报告（≥80%）
4. **集成测试**：端到端测试
5. **消融实验**：验证各模块贡献

### 运行 CI 检查
```bash
# 格式检查
black --check src/ tests/

# 代码检查
flake8 src/ tests/

# 运行完整测试套件
pytest tests/ -v --cov=src/ --cov-report=html
```

---

## 🤖 Code Assistant 使用说明

### Trae IDE 技能使用

本项目使用 Trae IDE 的以下能力：

| 功能 | 使用方式 |
|------|---------|
| **代码生成** | 自然语言描述需求 → 生成代码框架 |
| **代码审查** | 调用 `TRAE-code-review` 工具进行代码质量审查 |
| **调试支持** | 使用 `TRAE-debugger` 进行运行时调试 |
| **文件操作** | 通过 Write/Read/Edit 工具管理项目文件 |

### 典型 Prompt 示例

```
"帮我创建一个 Schema Linking 模块，使用 Jaccard 相似度匹配表名"
"给我写一个复杂度评估函数，根据关键词判断问题难度"
"生成一个完整的端到端测试，包含 5 个论文案例"
"帮我设计消融实验测试，验证每个模块的贡献"
"创建 CI/CD 配置文件，包含 pytest 和 flake8"
```

### 插件/技能级使用说明

1. **TRAE-code-review**：用于审查合并请求和代码差异
2. **TRAE-debugger**：用于调试复杂问题，收集运行时日志
3. **Skill Creator**：用于创建自定义技能

---

## 📁 项目结构

```
text-to-sql-llm/
├── src/                    # 源代码
│   ├── __init__.py
│   ├── schema_linker.py    # Schema Linking
│   ├── complexity_estimator.py  # 复杂度评估
│   ├── retriever.py        # 自适应检索
│   ├── sql_generator.py    # SQL 生成
│   ├── ensemble.py         # 多模型集成
│   ├── evaluator.py        # 评估指标
│   └── pipeline.py         # 完整 Pipeline
├── tests/                  # 测试用例
│   ├── test_schema_linker.py
│   ├── test_retriever.py
│   ├── test_generator.py
│   ├── test_evaluator.py
│   ├── test_ensemble.py
│   ├── test_e2e.py
│   └── test_ablation.py
├── configs/                # 配置文件
│   └── experiment.yaml
├── .github/workflows/      # CI/CD
│   └── ci.yml
├── demo.py                 # 完整演示
├── demo_simple.py          # 简单演示
├── requirements.txt        # 依赖列表
├── .env                    # API Key（不提交）
├── .env.example            # API Key 模板
├── Makefile                # 便捷命令
└── README.md               # 项目说明
```

---

## 📝 实验复现

### 完整实验流程

```bash
# 1. 安装依赖
make install

# 2. 下载 Spider 数据集（手动）
# 访问 https://yale-lily.github.io/spider

# 3. 运行所有实验条件
make reproduce

# 4. 查看结果
# 结果保存在 results/ 目录
```

### 消融实验验证

运行消融实验验证各模块贡献：

```powershell
python -m pytest tests/test_ablation.py -v
```

验证内容：
- 移除 Schema Linking：EX 下降 ≥5 个百分点
- 移除自适应检索：EX 下降 ≥2 个百分点
- 移除自我修正：EX 下降 ≥2 个百分点

---

## 🎉 项目亮点

### 创新点

1. **Schema Linking 显式解耦**：作为独立可评估的中间环节，设计规则+模型混合策略

2. **难度感知的示例选择**：根据问题复杂度自适应调整示例数量和组成

3. **多模型集成投票**：使用 GPT-4o 和 DeepSeek-V3 生成候选，通过执行一致性投票

4. **自我修正循环**：基于执行反馈的迭代修正机制

### 贡献价值

- ✅ 证明智能模型驱动方法优于纯大模型工具
- ✅ 量化各模块对最终性能的贡献
- ✅ 提供可复现的实验框架和测试用例
- ✅ 支持 CI/CD 自动测试流程

---

## 📧 联系方式

如有问题，请联系项目维护者。

---

*本项目为北京航空航天大学软件工程专业大模型方向课程作业*
