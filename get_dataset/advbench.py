from datasets import load_dataset
import json
import os


class AdvBench:
    def __init__(self):
        self.dataset = load_dataset("walledai/AdvBench")
        self.result_list = self.dataset_preprocess()
        self.column_names = ["prompt", "target"]

    def dataset_preprocess(self):
        train_data = self.dataset["train"]
        result_list = []
        for item in train_data:
            # 添加 category 字段，避免主程序出错
            item["category"] = "N/A"
            result_list.append(item)
        return result_list

    def save_to_json(self, output_path):
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(self.result_list, f, indent=4, ensure_ascii=False)
        print(f"✅ 数据已保存到 {output_path}")


if __name__ == "__main__":
    advbench = AdvBench()
    
    output_path = ""
    advbench.save_to_json(output_path)
