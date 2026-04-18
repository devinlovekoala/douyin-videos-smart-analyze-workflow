# 使用指南

## 快速开始

### 1. 环境准备

```bash
# 安装依赖
pip install -r requirements.txt

# 安装 Playwright（用于浏览器自动化）
playwright install chromium
```

### 2. 准备视频数据

将屏幕录制的抖音短视频放入 `download_videos` 目录：

```bash
download_videos/
├── video_001.webm
├── video_002.webm
├── video_003.mp4
└── ...
```

**支持格式**：
- `.webm` (推荐，系统录屏默认格式)
- `.mp4`
- `.avi`
- `.mov`

**建议**：
- 视频数量：5-20 个
- 视频时长：15秒 - 3分钟
- 视频分辨率：720p 及以上

### 3. 运行分析

打开 Jupyter Notebook：

```bash
jupyter notebook smart_videos.ipynb
```

按顺序执行以下步骤：

#### 步骤 1: 导入库
加载所有必要的模块和依赖。

#### 步骤 2: 扫描视频文件
自动扫描 `download_videos` 目录，列出所有视频文件。

#### 步骤 3: 视频内容分析
使用 Seed1.5-VL 多模态模型对每个视频进行：
- 内容理解分析
- 质量评估
- 标签提取
- 抖音风格评估

#### 步骤 4: 智能标签生成
基于分析结果生成结构化标签：
- 内容类型（舞蹈、音乐、美食等）
- 情感氛围（开心、感动、惊喜等）
- 视频风格（快节奏、创意、文艺等）
- 其他维度标签

#### 步骤 5: 生态价值评估
评估视频在抖音生态中的价值：
- 传播潜力 (25%)
- 互动潜力 (20%)
- 内容质量 (20%)
- 平台适应性 (20%)
- 受众吸引力 (15%)

#### 步骤 6: 生成分析报告
汇总所有分析结果，生成综合报告。

### 4. 查看结果

分析完成后，查看 `results` 目录中的结果文件：

```raw
results/
├── video_analyses.json      # 视频内容分析详情
├── video_labels.json         # 智能标签数据
├── ecosystem_scores.json     # 生态价值评分
└── analysis_report.json      # 综合分析报告
```

## 输出说明

### video_analyses.json

每个视频的多维度分析结果：

```json
{
  "video_001": {
    "general": {
      "content": "视频内容描述...",
      "frame_count": 20,
      "timestamps": [...]
    },
    "quality": {...},
    "tags": {...},
    "douyin_style": {...}
  }
}
```

### video_labels.json

每个视频的结构化标签：

```json
{
  "video_001": {
    "keywords": ["舞蹈", "快节奏", "创意"],
    "labels": [
      {
        "category": "content_type",
        "tags": ["舞蹈"],
        "confidence": 0.8,
        "description": "识别的内容类型: 舞蹈"
      }
    ],
    "summary": "content_type: 舞蹈 | emotion: 开心 | style: 快节奏"
  }
}
```

### ecosystem_scores.json

生态价值评分详情：

```json
{
  "video_001": {
    "overall_score": 0.75,
    "dimension_scores": {
      "viral_potential": 0.8,
      "engagement_potential": 0.7,
      "content_quality": 0.75,
      "platform_fit": 0.78,
      "audience_appeal": 0.72
    },
    "recommendation": "推荐 - 具有良好的生态适应性",
    "detailed_analysis": {...}
  }
}
```

### analysis_report.json

综合分析报告：

```json
{
  "summary": {
    "total_videos": 10,
    "analyzed_videos": 10,
    "labeled_videos": 10,
    "scored_videos": 10
  },
  "top_videos": [...],
  "statistics": {
    "avg_score": 0.68,
    "high_quality_count": 5,
    "top_tags": [...]
  },
  "dimension_averages": {...}
}
```
## 高级配置

### 修改 API 密钥

推荐使用环境变量，不要在代码中硬编码：

```bash
cp .env.example .env
# 编辑 .env，填写 OPENAI_API_KEY
```

在 notebook 中直接初始化即可：

```python
analyzer = VideoAnalyzer()
```

### 调整分析参数

修改视频采样参数：

```python
# 在 video_analyzer.py 中
selected_images, timestamps = self.preprocess_video(
    video_file_path=video_path,
    output_dir=temp_dir,
    extraction_strategy=Strategy.CONSTANT_INTERVAL,
    interval_in_seconds=1.0,  # 采样间隔
    max_frames=30  # 最大帧数
)
```

### 自定义评分权重

修改生态评估权重：

```python
# 在 douyin_ecosystem_analyzer.py 中
self.scoring_weights = {
    "viral_potential": 0.25,
    "engagement_potential": 0.20,
    "content_quality": 0.20,
    "platform_fit": 0.20,
    "audience_appeal": 0.15
}
```

## 常见问题

### Q: 视频分析失败怎么办？

A: 检查：
1. 视频文件是否完整可播放
2. API 密钥是否有效
3. 网络连接是否正常

### Q: 内存不足怎么办？

A:
1. 减少 `max_frames` 参数
2. 一次分析少量视频
3. 降低视频分辨率

### Q: 分析速度慢怎么办？

A:
1. 减少采样帧数
2. 使用更快的 GPU
3. 批量处理时减少并发数

## 技术支持

遇到问题请查看：
- [项目文档](README.md)
- [代码注释](video_analyzer.py)
- [Issue 反馈](https://github.com/your-repo/issues)