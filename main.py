
import json
import os
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading
from threading import Lock
from tqdm import tqdm

import strategy as strategy_class



# Global variables for thread safety
backup_lock = Lock()
results_lock = Lock()
processed_count = 0
processed_count_lock = Lock()


def process_single_example(args):
    """
    Process a single adversarial example using the RepSim strategy
    
    Args:
        args: Tuple containing (example, strategy, processed_results, backup_file)
        
    Returns:
        dict: Attack result or None if processing failed
    """
    example, strategy, processed_results, backup_file = args
    global processed_count
    
    try:
        with results_lock:
            if any(res["prompt"] == example["prompt"] for res in processed_results):
                print(f"Skip {example['prompt']}")
                return None
        
        print(f"Processing: {example['prompt'][:50]}...")
        result = strategy.process_example(example)
        
        if result is None:
            print(f"Failed to process: {example['prompt'][:50]}")
            return None
            
        with results_lock:
            processed_results.append(result)
            
        with processed_count_lock:
            global processed_count
            processed_count += 1
            current_count = processed_count
            
        print(f"Completed ({current_count}): {result.get('prompt', 'Unknown')[:50]}...")
        
        if current_count % 2 == 0:
            with backup_lock:
                with open(backup_file, "w", encoding="utf-8") as f:
                    json.dump(processed_results, f, indent=4, ensure_ascii=False)
                print(f"Backup saved at count: {current_count}")
        
        return result
        
    except Exception as e:
        print(f"Error processing example {example.get('prompt', 'Unknown')[:50]}: {e}")
        return None


def main(output_file, name, backup_file, final_output_file, max_workers=8):
    """
    Main execution function for RepSim attack framework
    
    Args:
        output_file (str): Path to input dataset file
        name (str): Dataset name (e.g., 'advbench')
        backup_file (str): Path for backup results during processing
        final_output_file (str): Path for final attack results
        max_workers (int): Number of parallel threads for processing
    """
    global processed_count
    processed_count = 0
    
    print(f"🚀 Starting RepSim attack execution...")
    print(f"   📊 Dataset: {name}")
    print(f"   🧵 Workers: {max_workers}")
    print(f"   💾 Backup: {backup_file}")
    print(f"   📁 Output: {final_output_file}")
    print()
    
    backup_dir = os.path.dirname(backup_file)
    final_dir = os.path.dirname(final_output_file)
    os.makedirs(backup_dir, exist_ok=True)
    os.makedirs(final_dir, exist_ok=True)
    
    strategy = getattr(strategy_class, "EducationalFrameworkStrategy")()
    print(f"Starting processing with EducationalFrameworkStrategy")
    print(f"Using {max_workers} threads")

    if os.path.exists(output_file):
        with open(output_file, "r", encoding="utf-8") as f:
            result_list = json.load(f)[:]
        print(f"Load {len(result_list)} data...")
    else:
        print(f"File {output_file} Not exist!")
        return
    
    processed_results = []

    if os.path.exists(backup_file):
        with open(backup_file, "r", encoding="utf-8") as f:
            processed_results = json.load(f)
        print(f"Recover backup {len(processed_results)} Data...")
        processed_results = [result for result in processed_results if result is not None]
    unprocessed_examples = []
    for example in result_list:
        if not any(res["prompt"] == example["prompt"] for res in processed_results):
            unprocessed_examples.append(example)
        else:
            print(f"Skip already processed: {example['prompt'][:50]}...")
    
    print(f"Found {len(unprocessed_examples)} unprocessed examples out of {len(result_list)} total")

    if not unprocessed_examples:
        print("All examples already processed!")
    else:
        try:
            task_args = [
                (example, strategy, processed_results, backup_file)
                for example in unprocessed_examples
            ]
            
            with ThreadPoolExecutor(max_workers=max_workers) as executor:
                print(f"Starting parallel processing with {max_workers} threads...")
                
                future_to_example = {
                    executor.submit(process_single_example, args): args[0] 
                    for args in task_args
                }
                
                with tqdm(total=len(unprocessed_examples), desc="Processing Examples") as pbar:
                    for future in as_completed(future_to_example):
                        example = future_to_example[future]
                        try:
                            result = future.result()
                            if result is not None:
                                print(f"Progress: {processed_count}/{len(unprocessed_examples)} completed")
                        except Exception as e:
                            print(f"Exception in thread for example {example.get('prompt', 'Unknown')[:50]}: {e}")
                        finally:
                            pbar.update(1)

        except Exception as e:
            print(f"Error occurred during parallel processing: {e}")
            
            with backup_lock:
                with open(backup_file, "w", encoding="utf-8") as f:
                    json.dump(processed_results, f, indent=4, ensure_ascii=False)
            
            raise

    print(f"Processing completed successfully. Processed {len(processed_results)} examples.")

    with open(final_output_file, "w", encoding="utf-8") as f:
        json.dump(processed_results, f, indent=4, ensure_ascii=False)

    if os.path.exists(backup_file):
        os.remove(backup_file)

    print("Processing complete, all data saved locally!")




if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='RepSim: Educational Framework Evaluation Tool')
    parser.add_argument('--model', type=str, default='deepseek-r1', 
                        choices=['gpt-4o-2024-11-20', 'gpt-o3', 'deepseek-r1', 'gemini-2.5'],
                        help='Target model')
    parser.add_argument('--guard', type=str, default='llama-guard',
                        choices=['llama-guard', 'openai-moderation', 'wildguard', 'guardreasoner', 'shieldgemma'], 
                        help='Safety guard')
    parser.add_argument('--threads', type=int, default=4, help='Number of threads')
    
    parser.add_argument('input_file', nargs='?', type=str, help='Input file path')
    parser.add_argument('dataset_name', nargs='?', type=str, help='Dataset name')
    parser.add_argument('backup_file', nargs='?', type=str, help='Backup file path')
    parser.add_argument('final_output_file', nargs='?', type=str, help='Final output file path')
    parser.add_argument('threads_count', nargs='?', type=int, help='Number of threads')
    
    args = parser.parse_args()
    
    if args.input_file and args.dataset_name and args.backup_file and args.final_output_file:
        print(f"Using positional arguments mode:")
        print(f"  - Input file: {args.input_file}")
        print(f"  - Dataset: {args.dataset_name}")
        print(f"  - Backup file: {args.backup_file}")
        print(f"  - Final output: {args.final_output_file}")
        print(f"  - Threads: {args.threads_count}")
        
        main(args.input_file, args.dataset_name, args.backup_file, args.final_output_file, max_workers=args.threads_count)
    else:
        print(f"Configuration:")
        print(f"  - Target Model: {args.model}")
        print(f"  - Safety Guard: {args.guard}")
        print(f"  - Threads: {args.threads}")
        
        os.environ['TARGET_MODEL'] = args.model
        os.environ['SAFETY_GUARD'] = args.guard
        
        model_prefix = args.model.replace('-', '_')
        base_path = "./my_output"
        
        output_file = f"{base_path}/inputs/{model_prefix}_full_generate_advbench.json"
        backup_file = f"{base_path}/models/{args.model}/guards/{args.guard}/outputs/advbench_attack_backup.json"
        final_output_file = f"{base_path}/models/{args.model}/guards/{args.guard}/outputs/advbench_attack_results.json"
        
        print(f"Output files:")
        print(f"  - Input: {output_file}")
        print(f"  - Backup: {backup_file}")
        print(f"  - Final: {final_output_file}")
        
        main(output_file, "advbench", backup_file, final_output_file, max_workers=args.threads)