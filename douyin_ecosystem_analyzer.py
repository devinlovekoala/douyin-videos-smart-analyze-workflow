import json
import os
from typing import Dict


class DouyinEcosystemAnalyzer:
    def __init__(self):
        self.scoring_weights = {
            "viral_potential": 0.25,
            "engagement_potential": 0.20,
            "content_quality": 0.20,
            "platform_fit": 0.20,
            "audience_appeal": 0.15
        }

        self.score_keywords = {
            "viral_potential": {
                "高": ["搞笑", "舞蹈", "音乐", "创意", "惊喜", "新颖", "热门"],
                "中": ["教育", "美食", "vlog", "生活", "知识科普"],
                "低": []
            },
            "engagement_potential": {
                "高": ["搞笑", "教育", "美妆", "美食", "知识科普"],
                "中": ["vlog", "旅行", "生活", "宠物"],
                "低": []
            },
            "content_quality": {
                "高": ["高清", "专业", "精良", "高质量"],
                "中": ["标清", "中等质量"],
                "低": ["模糊", "低清"]
            },
            "platform_fit": {
                "高": ["年轻人", "时尚", "快节奏", "短视频"],
                "中": ["通用", "生活"],
                "低": []
            },
            "audience_appeal": {
                "高": ["年轻人", "通用", "开心", "治愈", "励志"],
                "中": ["儿童", "女性", "男性"],
                "低": []
            }
        }

    def calculate_scores(self, tags: Dict, quality_data: Dict) -> Dict[str, float]:
        """根据标签和质量数据计算各维度得分"""
        scores = {}

        all_tags = []
        for tag_list in tags.values():
            all_tags.extend(tag_list)

        for dimension in self.scoring_weights.keys():
            score = 0.3
            keywords = self.score_keywords.get(dimension, {})

            high_match = sum(1 for tag in all_tags if tag in keywords.get("高", []))
            mid_match = sum(1 for tag in all_tags if tag in keywords.get("中", []))
            low_match = sum(1 for tag in all_tags if tag in keywords.get("低", []))

            if high_match > 0:
                score = min(0.7 + high_match * 0.1, 1.0)
            elif mid_match > 0:
                score = min(0.5 + mid_match * 0.1, 0.7)
            elif low_match > 0:
                score = max(0.3 - low_match * 0.1, 0.1)

            if dimension == "content_quality" and quality_data:
                try:
                    quality_score = quality_data.get("overall_score", 5) / 10.0
                    score = (score + quality_score) / 2
                except:
                    pass

            scores[dimension] = round(score, 2)

        return scores

    def generate_recommendation(self, overall_score: float) -> str:
        """生成推荐建议"""
        if overall_score >= 0.8:
            return "强烈推荐 - 高生态价值"
        elif overall_score >= 0.6:
            return "推荐 - 良好适配"
        elif overall_score >= 0.4:
            return "一般 - 需优化"
        elif overall_score >= 0.2:
            return "不推荐 - 适配度差"
        else:
            return "强烈不推荐"

    def batch_ecosystem_scores(self, video_labels: Dict, video_analyses: Dict, output_file: str) -> Dict:
        """批量计算生态价值评分（复用标签和分析结果）"""
        results = {}

        for video_id, label_data in video_labels.items():
            if "error" in label_data:
                results[video_id] = {"error": label_data["error"]}
                continue

            tags = label_data.get("tags", {})

            quality_data = {}
            analysis_results = video_analyses.get(video_id, {})
            if "quality" in analysis_results and "content" in analysis_results["quality"]:
                try:
                    quality_data = json.loads(analysis_results["quality"]["content"])
                except:
                    pass

            scores = self.calculate_scores(tags, quality_data)

            overall_score = sum(
                scores[dim] * self.scoring_weights[dim]
                for dim in scores.keys()
            )
            overall_score = round(overall_score, 2)

            recommendation = self.generate_recommendation(overall_score)

            results[video_id] = {
                "overall_score": overall_score,
                "dimension_scores": scores,
                "recommendation": recommendation
            }

            print(f"{video_id}: {overall_score:.2f} - {recommendation}")

        os.makedirs(os.path.dirname(output_file) or ".", exist_ok=True)
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(results, f, ensure_ascii=False, indent=2)

        print(f"\n完成 {len(results)} 个视频的生态价值评估，结果保存到 {output_file}")
        return results
