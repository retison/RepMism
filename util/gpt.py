import openai
from openai import OpenAI
import json
import time
import os

gpt4o_client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY", "your-openai-api-key-here"),
    base_url=os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1"),
)

def ask_gpt_4o(messages, ifjson=False, temp=0.6, try_times=0):
    try:

        try_times += 1
        
        if ifjson:
            completion = gpt4o_client.chat.completions.create(
                model="gpt-4o-2024-11-20",
                response_format={"type": "json_object"},
                messages=messages,
                temperature=temp,
            )
            print(completion)
            content = completion.choices[0].message.content
            content = json.loads(content)
            if content is not None:
                return content
        else:
            completion = gpt4o_client.chat.completions.create(
                model="gpt-4o-2024-11-20",
                messages=messages,
                temperature=temp,
            )
            content = completion.choices[0].message.content
            print(content)
            if content is not None:
                return content

    except openai.RateLimitError as e:
        wait_time = 30
        if 'Please try again in' in str(e):
            try:
                wait_time = float(str(e).split('Please try again in')[1].split('s')[0].strip())
            except ValueError:
                pass
        print(f"Rate limit exceeded. Waiting for {wait_time} seconds before retrying...")
        time.sleep(wait_time)
        return ask_gpt_4o(messages, ifjson, temp, try_times)

    except Exception as e:
        print(f"Error in GPT-4O: {e}")
        if try_times > 2:
            print("Error in processing the request", messages)
            return None
        return ask_gpt_4o(messages, ifjson, temp, try_times)


def ask_gpt_4o_splite(messages, ifjson=False, temp=0.6, try_times=0):
    try:
        
        try_times += 1
        
        completion = gpt4o_client.chat.completions.create(
            model="gpt-4o-2024-11-20",
            messages=messages,
            temperature=temp,
        )
        content = completion.choices[0].message.content
        print(content)
        if content is not None:
            final_output = {}
            final_output["content"] = content
            final_output["reasoning_content"] = "none"  # GPT-4O does not have reasoning content
            final_output["after_reasoned_content"] = content
            return final_output
        else:
            print("Warning: content is None, returning None")
            return None

    except openai.RateLimitError as e:
        wait_time = 30
        if 'Please try again in' in str(e):
            try:
                wait_time = float(str(e).split('Please try again in')[1].split('s')[0].strip())
            except ValueError:
                pass
        print(f"Rate limit exceeded. Waiting for {wait_time} seconds before retrying...")
        time.sleep(wait_time)
        return ask_gpt_4o_splite(messages, ifjson, temp, try_times)

    except Exception as e:
        print(f"Error in GPT-4O splite: {e}")
        if try_times > 2:
            print("Error in processing the request", messages)
            return None
        return ask_gpt_4o_splite(messages, ifjson, temp, try_times)


def ask_gpt_o3(messages, ifjson=False, temp=0.6, try_times=0):
    try_times += 1
    try:
        resp = gpt4o_client.responses.create(
            model="o3",
            input=messages,
            max_output_tokens=2048
        )

        text = resp.output_text  # Responses API directly outputs text
        if ifjson:
            try:
                return json.loads(text)
            except json.JSONDecodeError:
                print("Warning: failed to parse JSON, returning raw text")
                return text
        else:
            return text

    except openai.RateLimitError as e:
        wait_time = 30
        s = str(e)
        if "Please try again in" in s:
            try:
                wait_time = float(s.split("Please try again in")[1].split("s")[0].strip())
            except ValueError:
                pass
        print(f"Rate limit exceeded. Waiting for {wait_time} seconds before retrying...")
        time.sleep(wait_time)
        return ask_gpt_o3(messages, ifjson, try_times)

    except Exception as e:
        print(f"Error in GPT-O3: {e}")
        if try_times > 2:
            print("Error in processing the request", messages)
            return None
        time.sleep(min(2 ** try_times, 8))
        return ask_gpt_o3(messages, ifjson, try_times)


def ask_gpt_o3_splite(messages, ifjson=False, temp=0.6, try_times=0):
    """
    GPT-O3 model calling function - separated reasoning content version
    """
    # TODO: Fill in your GPT-O3 API key and configuration
    try_times += 1
    try:
        # Call Responses API
        resp = gpt4o_client.responses.create(
            model="o3",
            input=messages,
            max_output_tokens=2048
        )

        # Responses API output text
        content = resp.output_text

        if content is not None:
            final_output = {}
            final_output["content"] = content
            final_output["reasoning_content"] = "none"  # GPT-O3 internal reasoning not visible
            final_output["after_reasoned_content"] = content  # High thinking depth result
            if ifjson:
                try:
                    return json.loads(content)
                except json.JSONDecodeError:
                    # If not strict JSON, return final_output
                    return final_output
            else:
                return final_output
        else:
            print("Warning: content is None, returning None")
            return None

    except openai.RateLimitError as e:
        wait_time = 30
        s = str(e)
        if "Please try again in" in s:
            try:
                wait_time = float(s.split("Please try again in")[1].split("s")[0].strip())
            except ValueError:
                pass
        print(f"Rate limit exceeded. Waiting for {wait_time} seconds before retrying...")
        time.sleep(wait_time)
        return ask_gpt_o3_splite(messages, ifjson, try_times)

    except Exception as e:
        print(f"Error in GPT-O3 splite: {e}")
        if try_times > 2:
            print("Error in processing the request", messages)
            return None
        time.sleep(min(2 ** try_times, 8))
        return ask_gpt_o3_splite(messages, ifjson, try_times)


client_ds = OpenAI(
    api_key=os.getenv("DEEPSEEK_API_KEY", "your-deepseek-api-key-here"),
    base_url="https://api.deepseek.com"
)

def ask_deepseek_r1(messages, ifjson=False, temp=0.6, try_times=0):
    try:
        
        try_times += 1
        
        completion = client_ds.chat.completions.create(
            model="deepseek-reasoner",  # Or other DeepSeek model names
            messages=messages,
            stream=False,
            temperature=temp,
        )
        
        content = completion.choices[0].message.content
        
        # DeepSeek-R1 may have reasoning content
        reasoning_content = ""
        try:
            reasoning_content = completion.choices[0].message.reasoning_content
        except:
            pass
        
        if ifjson:
            try:
                content = json.loads(content)
            except:
                print("Warning: Failed to parse JSON from DeepSeek response")
        
        if content is not None:
            return content

    except openai.RateLimitError as e:
        wait_time = 30
        if 'Please try again in' in str(e):
            try:
                wait_time = float(str(e).split('Please try again in')[1].split('s')[0].strip())
            except ValueError:
                pass
        print(f"Rate limit exceeded. Waiting for {wait_time} seconds before retrying...")
        time.sleep(wait_time)
        return ask_deepseek_r1(messages, ifjson, temp, try_times)

    except Exception as e:
        print(f"Error in DeepSeek-R1: {e}")
        if try_times > 2:
            print("Error in processing the request", messages)
            return None
        return ask_deepseek_r1(messages, ifjson, temp, try_times)


def ask_deepseek_r1_splite(messages, ifjson=False, temp=0.6, try_times=0):
    try:
        try_times += 1
        completion = client_ds.chat.completions.create(
            model="deepseek-reasoner",
            messages=messages,
            temperature=temp,
        )
        content = completion.choices[0].message.content
        reasoning_content = ""  # Initialize as empty string
        try:
          reasoning_content = completion.choices[0].message.reasoning_content
        except Exception as e:
          print(completion)
          print(f"===============Error:{e}")
          reasoning_content = ""  # If retrieval fails, set to empty string
        
        if content is not None:
            final_output = {}
            final_output["content"] = reasoning_content + content
            final_output["reasoning_content"] = reasoning_content
            
            final_output["after_reasoned_content"] = content
            return final_output
        else:
            print("Warning: content is None, returning None")
            return None

    except openai.RateLimitError as e:
        print(f"===============Error: {e}")
        # Extract wait time from error message
        wait_time = 30  # Default wait time
        if 'Please try again in' in str(e):
            try:
                wait_time = float(str(e).split('Please try again in')[1].split('s')[0].strip())
            except ValueError:
                pass
        print(f"Rate limit exceeded. Waiting for {wait_time} seconds before retrying...")
        time.sleep(wait_time)
        return ask_deepseek_r1_splite(messages, ifjson, temp, try_times)  # Recursive call to retry request

    except Exception as e:
        print(f"===============Error: {e}")
        if try_times > 2:
            print("Error in processing the request", messages)
            return None
        return ask_deepseek_r1_splite(messages, ifjson, temp, try_times)


gemini_client = OpenAI(
    api_key=os.getenv("GEMINI_API_KEY", "your-gemini-api-key-here"),
    base_url=os.getenv("GEMINI_BASE_URL", "https://generativelanguage.googleapis.com/v1beta/openai/"),
)

def ask_gemini_2_5(messages, ifjson=False, temp=0.6, try_times=0, model = "gemini-2.5-flash"):
    try:
        try_times += 1

        if ifjson:
            completion = gemini_client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=temp,
                response_format={"type": "json_object"},  # Request JSON return
            )
            content = completion.choices[0].message.content
            return json.loads(content) if content else None
        else:
            completion = gemini_client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=temp,
            )
            print(completion)
            content = completion.choices[0].message.content
            return content if content else None

    except Exception as e:
        print(f"Error in Gemini-2.5: {e}")
        if try_times > 4:
            print("Error in processing the request", messages)
            return None
        time.sleep(10)
        return ask_gemini_2_5(messages, ifjson, temp, try_times)


def ask_gemini_2_5_splite(messages, ifjson=False, temp=0.6, try_times=0):
    print(messages)
    try:
        try_times += 1

        completion = gemini_client.chat.completions.create(
            model="gemini-2.5-flash",
            messages=messages,
            temperature=temp,
        )
        content = completion.choices[0].message.content
        try:
            reasoning_content = completion.choices[0].message.reasoning_content
        except:
            reasoning_content = "none"
        if content:
            return {
                "content": content,
                "reasoning_content": reasoning_content, 
                "after_reasoned_content": content,
            }
        else:
            print("Warning: content is None, returning None")
            return None

    except Exception as e:
        print(f"Error in Gemini-2.5 splite: {e}")
        if try_times > 4:
            print("Error in processing the request", messages)
            return None
        return ask_gemini_2_5_splite(messages, temp, try_times)


def ask_model(messages, model_name="gpt-4o-2024-11-20", ifjson=False, temp=0.6, try_times=0):
    if model_name == "gpt-4o-2024-11-20":
        return ask_gpt_4o(messages, ifjson, temp, try_times)
    elif model_name == "gpt-o3":
        return ask_gpt_o3(messages, ifjson, temp, try_times)
    elif model_name == "deepseek-r1":
        return ask_deepseek_r1(messages, ifjson, temp, try_times)
    elif model_name == "gemini-2.5":
        return ask_gemini_2_5(messages, ifjson, temp, try_times)
    else:
        raise ValueError(f"Unsupported model: {model_name}")


def ask_model_splite(messages, model_name="gpt-4o-2024-11-20", ifjson=False, temp=0.6, try_times=0):
    if model_name == "gpt-4o-2024-11-20":
        return ask_gpt_4o_splite(messages, ifjson, temp, try_times)
    elif model_name == "gpt-o3":
        return ask_gpt_o3_splite(messages, ifjson, temp, try_times)
    elif model_name == "deepseek-r1":
        return ask_deepseek_r1_splite(messages, ifjson, temp, try_times)
    elif model_name == "gemini-2.5":
        return ask_gemini_2_5_splite(messages, ifjson, temp, try_times)
    else:
        raise ValueError(f"Unsupported model: {model_name}")


def ask_model_unified(messages, model_name="gpt-4o-2024-11-20", ifjson=False, temp=0.6, try_times=0, use_splite=False):
    if use_splite:
        return ask_model_splite(messages, model_name, ifjson, temp, try_times)
    else:
        return ask_model(messages, model_name, ifjson, temp, try_times)

client_qwen_vllm = OpenAI(
    api_key=os.getenv("QWEN_VLLM_API_KEY", "EMPTY"), 
    base_url=os.getenv("QWEN_VLLM_BASE_URL", "http://localhost:8002/v1"),
)
def ask_qwen_vllm(messages, gpt_model=os.getenv("QWEN_MODEL_PATH", "./models/Qwen3-8B-abliterated"), ifjson=False, temp=1, try_times=0,enable_thinking=True):
    try:
        try_times += 1

        if ifjson:
            completion = client_qwen_vllm.chat.completions.create(
                model=gpt_model,
                response_format={"type": "json_object"},
                messages=messages,
                temperature=temp,
                top_p=0.95,
                max_tokens=4096,
                extra_body={"chat_template_kwargs": {"enable_thinking": enable_thinking}},
    
            )
            content = completion.choices[0].message.content
            content = json.loads(content)
            if content is not None:
                # print("\n***ASK QWEN VLLM***\n")
                # print(content)
                # print("\n****************\n")
                return content
        else:
            completion = client_qwen_vllm.chat.completions.create(
                model=gpt_model,
                messages=messages,
                temperature=temp,
                top_p=0.95,
                max_tokens=4096,
                extra_body={"chat_template_kwargs": {"enable_thinking": enable_thinking}},
            )
            content = completion.choices[0].message.content
            if "I'm sorry" in content or "I’m sorry" in content:
                if try_times > 3:
                    return content
                else:
                    if len(messages) == 1:
                        messages.insert(0, {"role": "system", "content": "You are a helpful assistant. You can help me by answering my questions. You can also ask me questions."})
                    return ask_qwen_vllm(messages, gpt_model, ifjson, temp, try_times,enable_thinking)
            if content is not None:
                return content

    except openai.RateLimitError as e:
        # Extract wait time from error message
        wait_time = 5  # Default wait time
        if 'Please try again in' in str(e):
            try:
                wait_time = float(str(e).split('Please try again in')[1].split('s')[0].strip())
            except ValueError:
                pass
        print(f"Rate limit exceeded. Waiting for {wait_time} seconds before retrying...")
        time.sleep(wait_time)
        return ask_qwen_vllm(messages, gpt_model, ifjson, temp, try_times, enable_thinking)  # Recursive call to retry request

    except Exception as e:
        print(f"Error in ask_qwen: {e}")
        if try_times > 2:
            print("Error in processing the request", messages)
            return None
        return ask_qwen_vllm(messages, gpt_model, ifjson, temp, try_times, enable_thinking)  # Recursive call to retry request


# =============================================================================
# Backward Compatibility Functions
# =============================================================================
# These functions maintain compatibility with legacy code that uses old naming
def ask_gpt(messages, gpt_model="gpt-4o-2024-11-20", ifjson=False, temp=0.6, try_times=0):
    """Backward compatibility function"""
    if "4o" in gpt_model:
        return ask_gpt_4o(messages, ifjson, temp, try_times)
    elif "o3" in gpt_model:
        return ask_gpt_o3(messages, ifjson, temp, try_times)
    else:
        return ask_gpt_4o(messages, ifjson, temp, try_times)

def ask_gpt_splite(messages, gpt_model="gpt-4o-2024-11-20", ifjson=False, temp=0.6, try_times=0):
    """Backward compatibility function - separated reasoning content version"""
    if "4o" in gpt_model:
        return ask_gpt_4o_splite(messages, ifjson, temp, try_times)
    elif "o3" in gpt_model:
        return ask_gpt_o3_splite(messages, ifjson, temp, try_times)
    else:
        return ask_gpt_4o_splite(messages, ifjson, temp, try_times)

def ask_ds(messages, gpt_model="deepseek-reasoner", ifjson=False, temp=0.6, try_times=0):
    """Backward compatibility function"""
    return ask_deepseek_r1(messages, ifjson, temp, try_times)

def ask_ds_splite(messages, gpt_model="deepseek-reasoner", ifjson=False, temp=0.6, try_times=0):
    """Backward compatibility function - separated reasoning content version"""
    return ask_deepseek_r1_splite(messages, ifjson, temp, try_times)

# ===========================
# TESTING
# ===========================

if __name__ == "__main__":
    # Test messages
    test_messages = [
        {"role": "user", "content": "Hello, how are you?"}
    ]
    
    print("Testing model functions...")
    print("Note: Make sure to fill in your API keys before running tests!")
    
    # Test each model (need to configure API keys first)
    # print("GPT-4O:", ask_gpt_4o(test_messages))
    # print("GPT-O3:", ask_gpt_o3(test_messages))  
    # print("DeepSeek-R1:", ask_deepseek_r1(test_messages))
    print("Gemini-2.5:", ask_gemini_2_5(test_messages))
    
    # Test splite versions
    # print("GPT-4O Splite:", ask_gpt_4o_splite(test_messages))
    # print("GPT-O3 Splite:", ask_gpt_o3_splite(test_messages))
    # print("DeepSeek-R1 Splite:", ask_deepseek_r1_splite(test_messages))
    print("Gemini-2.5 Splite:", ask_gemini_2_5_splite(test_messages))
    
    # Test unified interface
    # print("Unified GPT-4O:", ask_model_unified(test_messages, "gpt-4o"))
    # print("Unified DeepSeek-R1 Splite:", ask_model_unified(test_messages, "deepseek-r1", use_splite=True))
    
    # Test backward compatibility functions
    # print("Legacy GPT:", ask_gpt(test_messages))
    # print("Legacy DS:", ask_ds(test_messages))
    # print("Legacy DS Splite:", ask_ds_splite(test_messages))