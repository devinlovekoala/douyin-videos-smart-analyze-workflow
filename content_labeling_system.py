import json
import os
from typing import Dict


class ContentLabelingSystem:
    def __init__(self):
        pass

    def extract_tags_from_json(self, analysis_results: Dict) -> Dict:
        """从结构化JSON分析结果中提取所有标签"""
        all_tags = {
            "content_tags": [],
            "emotion_tags": [],
            "visual_tags": [],
            "scene_tags": [],
            "audience_tags": [],
            "quality_tags": [],
        }

        for analysis_type, result in analysis_results.items():
            if "error" in result:
                continue

            try:
                content = result.get("content", "")
                data = json.loads(content) if isinstance(content, str) else content

                if analysis_type == "content_understanding":
                    all_tags["content_tags"].append(data.get("content_category", ""))
                    all_tags["emotion_tags"].append(data.get("emotion_tone", ""))
                    all_tags["audience_tags"].extend(data.get("target_audience", []))

                elif analysis_type == "visual_style":
                    all_tags["visual_tags"].append(data.get("visual_style", ""))
                    color_palette = data.get("color_palette", {})
                    all_tags["visual_tags"].extend([
                        color_palette.get("saturation", ""),
                        color_palette.get("brightness", ""),
                        color_palette.get("temperature", "")
                    ])
                    all_tags["visual_tags"].extend(data.get("style_tags", []))

                elif analysis_type == "quality":
                    score = data.get("overall_score", 0)
                    if score >= 8:
                        all_tags["quality_tags"].append("高质量")
                    elif score >= 6:
                        all_tags["quality_tags"].append("中等质量")
                    all_tags["quality_tags"].extend(data.get("key_strengths", []))

                elif analysis_type == "tags":
                    all_tags["content_tags"].extend(data.get("content_tags", []))
                    all_tags["emotion_tags"].extend(data.get("emotion_tags", []))
                    all_tags["visual_tags"].extend(data.get("visual_tags", []))
                    all_tags["scene_tags"].extend(data.get("scene_tags", []))
                    all_tags["audience_tags"].extend(data.get("audience_tags", []))

            except (json.JSONDecodeError, TypeError):
                continue

        for key in all_tags:
            all_tags[key] = list(filter(None, set(all_tags[key])))

        return all_tags

    def batch_label_videos(self, video_analyses: Dict, output_file: str) -> Dict:
        """批量为视频生成标签（复用已有的分析结果，避免重复调用模型）"""
        results = {}

        for video_id, analysis_results in video_analyses.items():
            if "error" in analysis_results:
                results[video_id] = {"error": analysis_results["error"]}
                continue

            tags = self.extract_tags_from_json(analysis_results)

            summary_parts = []
            if tags["content_tags"]:
                summary_parts.append(f"内容: {', '.join(tags['content_tags'][:3])}")
            if tags["visual_tags"]:
                summary_parts.append(f"风格: {', '.join(tags['visual_tags'][:3])}")
            if tags["emotion_tags"]:
                summary_parts.append(f"情感: {', '.join(tags['emotion_tags'][:2])}")

            results[video_id] = {
                "tags": tags,
                "summary": " | ".join(summary_parts) if summary_parts else "无法提取标签"
            }

        os.makedirs(os.path.dirname(output_file) or ".", exist_ok=True)
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(results, f, ensure_ascii=False, indent=2)

        print(f"标签生成完成，处理了 {len(results)} 个视频，结果保存到 {output_file}")
        return results
