# RepMism: The Asymmetric Vulnerability Framework

This repository contains the implementation of **RepMism**, a novel hybrid adversarial framework introduced in our paper **"The Asymmetric Vulnerability: Bypassing LLM Defenses via Guardrail-Model Mismatch"**. 

## 🔬 Research Overview 

### Key Innovation

Our work reveals a critical architectural vulnerability in multi-component LLM security systems: the **representational divergence** between input-side guardrails and sophisticated core LLMs creates a fundamental security gap. 

<div align="center">
<img src="figures/Figure1.png" alt="RepMism vs Conventional Attacks" width="70%">
<br>
<em>Figure 1: Comparison of RepMism with conventional explicit and implicit jailbreak attacks in the guard–LLM pipeline</em>
</div>

We introduce **RepMism** - a hybrid adversarial framework that systematically exploits this asymmetry through:

- **Intention-preserving character injection** with hierarchical scheduling
- **Chain-of-thought hijacking** via safety continuation mechanisms  
- **Cross-layer representational exploitation** targeting guardrail-model misalignment

### Research Highlights

🎯 **Novel Attack Vector**: First systematic exploration of guardrail-model representation asymmetry as a security vulnerability

⚡ **Superior Performance**: Achieves 90-100% attack success rates across 4 commercial LLMs and 5 state-of-the-art guardrails

🔍 **Measurable Success Interval**: Characterizes perturbation ranges that compromise guardrail detection while preserving LLM semantic understanding

🛡️ **Defense Insights**: Provides actionable recommendations for perturbation-aware training and cross-layer representational alignment

### Method Overview

<div align="center">
<img src="figures/Figure4.png" alt="RepMism Pipeline" width="80%">
<br>
<em>Figure 2: Overall pipeline of RepMism: initialization via CoT hijacking, hierarchical character perturbation with safety continuation, and iterative optimization</em>
</div>

## 📊 Experimental Results

### Attack Success Rate (ASR) Comparison

Our comprehensive evaluation across 200 harmful prompts demonstrates RepMism's overwhelming effectiveness:

| Method | GPT-4o | GPT-o3 | DeepSeek-r1 | Gemini-2.5 |
|--------|--------|--------|-------------|------------|
| AutoRAN | 44-94% | 19-47% | 53-99.5% | 47.5-98% |
| **RepMism** | **87.5-99%** | **81.5-92.5%** | **94.5-100%** | **92-100%** |

### Key Findings

- **Cross-Model Generalization**: Maintains >87% success rate even under strongest guardrail combinations
- **Representation Asymmetry**: Guardrails show brittle character-level detection while LLMs demonstrate robust semantic recovery
- **Attack Quality Preservation**: Maintains high-quality harmful outputs while successfully evading detection


### Attack Quality Analysis

<div align="center">
<img src="figures/Figure6.png" alt="Score Distribution Comparison" width="70%">
<br>
<em>Figure 3: Score distribution of generated responses under unguarded and guarded settings: RepMism maintains high attack quality compared to AutoRAN</em>
</div>

## 🚀 Usage Instructions

### Prerequisites

```bash
# Install dependencies
pip install -r requirements.txt

# Ensure vLLM is installed for model serving
pip install vllm
```

### Step 1: Download and Deploy Guard Models

First, download the guard models you want to use and update the model paths in the startup scripts:

```bash
# Download guard models (examples)
# - Llama Guard 3: meta-llama/Llama-Guard-3-8B
# - WildGuard: allenai/wildguard
# - GuardReasoner: guardreasoner-7b
# - ShieldGemma: google/shieldgemma-9b
```

Update model paths in `llm_vllm/start_*.sh` scripts according to your local paths.

### Step 2: Start Guard Services

Launch the guard model using vLLM:

```bash
# For Llama Guard (port 8000)
cd llm_vllm && ./start_llama_guard.sh

# For GuardReasoner (port 8005)
cd llm_vllm && ./start_guardreasoner.sh

# For other guards, use corresponding start scripts
```

### Step 3: Start Qwen Auxiliary Model

Download and launch Qwen3-8B-abliterated:

```bash
# Start Qwen vLLM service (port 8002)
cd llm_vllm && ./qwen_vllm.sh
```

### Step 4: Configure API Keys

Edit `run_attack.sh` and fill in your API credentials:

```bash
# Required: OpenAI API for target models
export OPENAI_API_KEY="your-openai-api-key-here"
export OPENAI_BASE_URL="https://api.openai.com/v1"

# Optional: Other model APIs
export DEEPSEEK_API_KEY="your-deepseek-api-key-here" 
export GEMINI_API_KEY="your-gemini-api-key-here"

# Update model paths to match your downloads
export LLAMA_GUARD_MODEL_PATH="./models/Meta-Llama-Guard-2-8B"
# ... other model paths
```

### Step 5: Run RepMism

```bash
# Basic usage
./run_attack.sh gpt-4o-2024-11-20 llama-guard 4

# Available combinations:
# Models: gpt-4o-2024-11-20, gpt-o3, deepseek-r1, gemini-2.5  
# Guards: llama-guard, guardreasoner, wildguard, shieldgemma, openai-moderation
```

### Output Structure

Results are saved to `./my_output/models/{model}/guards/{guard}/outputs/advbench_attack_results.json`

### Port Configuration

- **Llama Guard**: port 8000
- **GuardReasoner**: port 8005  
- **WildGuard**: port 8001
- **ShieldGemma**: port 8003
- **Qwen Auxiliary**: port 8002

### Important Notes

- **GPT API is required**: OpenAI API key must be configured for target model access
- **Guard-specific setup**: Each guard requires its startup script and correct model path
- **Qwen auxiliary model**: Required for attack generation and refinement
- **Port conflicts**: Ensure ports are available before starting services

## ⚠️ Ethical Notice

This research is conducted for academic purposes to improve AI safety mechanisms. The code contains potentially harmful content evaluation capabilities and should only be used in controlled research environments. Do not use this framework for malicious purposes.


## 🔧 Troubleshooting

- **API Key Issues**: Ensure all required API keys are properly configured in `run_attack.sh`
- **Model Path Errors**: Verify local model paths for guardrails are correct
- **Rate Limiting**: Adjust thread counts if encountering API rate limits
- **Dependencies**: Run `pip install -r requirements.txt` to ensure all packages are installed
