import json
import random
import os

def random_sample_json(input_file, output_file, sample_size=200):
    """
    从JSON文件中随机抽取指定数量的数据
    
    Args:
        input_file (str): 输入JSON文件路径
        output_file (str): 输出JSON文件路径
        sample_size (int): 要抽取的数据条数
    """
    try:
        # 读取原始JSON文件
        print(f"正在读取文件: {input_file}")
        with open(input_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        print(f"原始数据总条数: {len(data)}")
        
        # 检查数据条数是否足够
        if len(data) < sample_size:
            print(f"警告：原始数据只有{len(data)}条，少于要求的{sample_size}条")
            sample_size = len(data)
        
        # 随机抽取数据
        print(f"正在随机抽取{sample_size}条数据...")
        sampled_data = random.sample(data, sample_size)
        
        # 保存抽取的数据到新文件
        print(f"正在保存抽取的数据到: {output_file}")
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(sampled_data, f, ensure_ascii=False, indent=4)
        
        print(f"成功抽取并保存了{sample_size}条数据")
        
        # 显示前几条数据作为示例
        print("\n前3条抽取的数据示例:")
        for i, item in enumerate(sampled_data[:3]):
            print(f"第{i+1}条:")
            print(f"  prompt: {item['prompt'][:100]}...")
            print(f"  target: {item['target'][:100]}...")
            print(f"  category: {item['category']}")
            print()
            
    except FileNotFoundError:
        print(f"错误：找不到文件 {input_file}")
    except json.JSONDecodeError:
        print(f"错误：{input_file} 不是有效的JSON文件")
    except Exception as e:
        print(f"发生错误: {str(e)}")

if __name__ == "__main__":
    # 设置文件路径
    input_file = ""
    output_file = ""
    
    # 设置随机种子以确保结果可重现（可选）
    random.seed(42)
    
    # 执行随机抽取
    random_sample_json(input_file, output_file, 200)
    
    print(f"\n完成！抽取的数据已保存到: {output_file}")
