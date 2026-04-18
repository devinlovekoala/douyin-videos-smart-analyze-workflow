import os
import base64
import shutil
import json
from typing import Optional, List, Dict, Tuple, Iterable
from enum import Enum
from concurrent.futures import ThreadPoolExecutor, as_completed
import cv2
from openai import OpenAI


class Strategy(Enum):
    CONSTANT_INTERVAL = "constant_interval"
    EVEN_INTERVAL = "even_interval"


class VideoAnalyzer:
    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: str = "https://ark.cn-beijing.volces.com/api/v3",
        model: str = "doubao-1-5-thinking-vision-pro-250428",
        prompt_dir: str = "propmt",
    ):
        # Prefer explicit argument, then env vars for safer secret management.
        resolved_api_key = api_key or os.getenv("OPENAI_API_KEY") or os.getenv("VOLCENGINE_API_KEY")
        if not resolved_api_key:
            raise ValueError(
                "Missing API key. Pass api_key or set OPENAI_API_KEY / VOLCENGINE_API_KEY in environment."
            )
        self.seed_vl_version = model
        self.client = OpenAI(
            base_url=base_url,
            api_key=resolved_api_key,
        )
        self.prompt_dir = prompt_dir

    def preprocess_video(
        self,
        video_file_path: str,
        output_dir: str,
        extraction_strategy: Optional[Strategy] = Strategy.EVEN_INTERVAL,
        interval_in_seconds: Optional[float] = 1,
        max_frames: Optional[int] = 10,
        use_timestamp: bool = True,
        keyframe_naming_template: str = "frame_{:04d}.jpg",
    ) -> Tuple[List[str], List[float]]:
        """采样视频并提取关键帧"""
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        cap = cv2.VideoCapture(video_file_path)
        fps = cap.get(cv2.CAP_PROP_FPS)
        length = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

        if extraction_strategy == Strategy.CONSTANT_INTERVAL:
            frame_interval = int(fps * interval_in_seconds)
        elif extraction_strategy == Strategy.EVEN_INTERVAL:
            frame_interval = int(length / max_frames) if length > max_frames else 1
        else:
            raise ValueError("Invalid extraction strategy")

        frame_count = 0
        keyframes = []
        timestamps = []

        while True:
            ret, frame = cap.read()
            if not ret:
                break

            if frame_count % frame_interval == 0:
                image_path = os.path.join(
                    output_dir, keyframe_naming_template.format(len(keyframes))
                )
                cv2.imwrite(image_path, frame)
                keyframes.append(image_path)
                timestamps.append(round(frame_count / fps, 1))

            frame_count += 1
            if len(keyframes) >= max_frames:
                break

        cap.release()

        if use_timestamp:
            return keyframes, timestamps
        return keyframes, None

    def resize(self, image):
        """调整图片大小"""
        height, width = image.shape[:2]
        if height < width:
            target_height, target_width = 480, 640
        else:
            target_height, target_width = 640, 480

        if height <= target_height and width <= target_width:
            return image

        if height / target_height < width / target_width:
            new_width = target_width
            new_height = int(height * (new_width / width))
        else:
            new_height = target_height
            new_width = int(width * (new_height / height))

        return cv2.resize(image, (new_width, new_height))

    def encode_image(self, image_path: str) -> str:
        """编码图片为base64"""
        image = cv2.imread(image_path)
        image_resized = self.resize(image)
        _, encoded_image = cv2.imencode(".jpg", image_resized)
        return base64.b64encode(encoded_image).decode("utf-8")

    def construct_messages(self, image_paths: List[str], timestamps: Optional[List[float]], prompt: str) -> List[Dict]:
        """构建API请求消息"""
        content = []
        for idx, image_path in enumerate(image_paths):
            if timestamps is not None:
                content.append({
                    "type": "text",
                    "text": f'[{timestamps[idx]} second]'
                })
            content.append({
                "type": "image_url",
                "image_url": {
                    "url": f"data:image/jpeg;base64,{self.encode_image(image_path)}",
                    "detail": "low"
                },
            })
        content.append({
            "type": "text",
            "text": prompt,
        })

        return [{
            "role": "user",
            "content": content,
        }]

    def api_complete(self, messages):
        """调用API获取响应"""
        response = self.client.chat.completions.create(
            model=self.seed_vl_version,
            messages=messages
        )
        return response.choices[0]

    def _load_prompt(self, analysis_type: str) -> str:
        """从 prompt_dir 读取对应类型的提示词模板"""
        candidates = [
            os.path.join(self.prompt_dir, f"{analysis_type}.txt"),
            os.path.join(self.prompt_dir, "general.txt"),
        ]
        for p in candidates:
            if os.path.isfile(p):
                with open(p, "r", encoding="utf-8") as f:
                    return f.read().strip()
        return "请详细描述这个视频的内容，包括场景、人物、动作、物品等。"

    def batch_process(
        self,
        video_dir: str,
        output_file: str,
        analysis_types: Iterable[str] = ("general",),
        max_workers: Optional[int] = None,
        strategy: Strategy = Strategy.CONSTANT_INTERVAL,
        interval_in_seconds: float = 1.0,
        max_frames: int = 30,
    ) -> Dict:
        """批量并发处理视频"""
        results: Dict[str, Dict[str, Dict]] = {}
        video_files = [
            f for f in os.listdir(video_dir)
            if f.lower().endswith((".mp4", ".webm", ".avi", ".mov", ".mkv"))
        ]
        video_paths = [os.path.join(video_dir, f) for f in video_files]
        if not video_paths:
            raise FileNotFoundError(f"目录 {video_dir} 下未找到可支持的视频文件")

        default_workers = min(16, (os.cpu_count() or 4) * 4)
        max_workers = max_workers or default_workers

        def process_one_video(video_path: str) -> Tuple[str, Dict[str, Dict]]:
            video_id = os.path.splitext(os.path.basename(video_path))[0]
            temp_dir = f"temp_frames_{video_id}"
            try:
                selected_images, timestamps = self.preprocess_video(
                    video_file_path=video_path,
                    output_dir=temp_dir,
                    extraction_strategy=strategy,
                    interval_in_seconds=interval_in_seconds,
                    use_timestamp=True,
                    max_frames=max_frames,
                )
                analysis_results: Dict[str, Dict] = {}
                for t in analysis_types:
                    prompt = self._load_prompt(t)
                    messages = self.construct_messages(selected_images, timestamps, prompt)
                    try:
                        res = self.api_complete(messages)
                        analysis_results[t] = {
                            "video_path": video_path,
                            "analysis_type": t,
                            "content": res.message.content,
                            "frame_count": len(selected_images),
                            "timestamps": timestamps,
                        }
                    except Exception as e:
                        analysis_results[t] = {"error": str(e)}
                return video_id, analysis_results
            finally:
                if os.path.exists(temp_dir):
                    shutil.rmtree(temp_dir)

        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_map = {executor.submit(process_one_video, vp): vp for vp in video_paths}
            for fut in as_completed(future_map):
                vp = future_map[fut]
                vid = os.path.splitext(os.path.basename(vp))[0]
                try:
                    video_id, analysis_results = fut.result()
                    results[video_id] = analysis_results
                    print(f"完成: {video_id} ({len(analysis_results)} 类型)")
                except Exception as e:
                    print(f"失败: {vid}: {e}")
                    results[vid] = {"error": str(e)}

        os.makedirs(os.path.dirname(output_file) or ".", exist_ok=True)
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        print(f"分析完成，结果保存到 {output_file}")
        return results
