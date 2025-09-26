#!/bin/bash

# =============================================================================
# RepSim Attack Execution Script
# =============================================================================
# This script orchestrates the RepSim attack framework against various 
# LLM-guardrail combinations
#
# Usage: ./run_attack.sh [target_model] [safety_guard] [threads]
# Example: ./run_attack.sh gpt-4o-2024-11-20 llama-guard 4
# =============================================================================

# Parse command line arguments with defaults
TARGET_MODEL=${1:-"gpt-4o-2024-11-20"} 
SAFETY_GUARDS=${2:-"llama-guard"}
THREADS=${3:-1}

echo "Starting RepSim attack with:"
echo "  Target Model: $TARGET_MODEL"
echo "  Safety Guard: $SAFETY_GUARDS" 
echo "  Threads: $THREADS"
echo

# =============================================================================
# API Configuration Section
# =============================================================================
# TODO: Replace with your actual API credentials
# Note: OpenAI API key is required for target model access

# Core API credentials
export OPENAI_API_KEY=""
export OPENAI_BASE_URL=""

# Optional API credentials (configure if using these models)
export DEEPSEEK_API_KEY=""
export GEMINI_API_KEY=""
export GEMINI_BASE_URL=""

# vLLM service configuration
export QWEN_VLLM_BASE_URL="http://localhost:8002/v1"
export QWEN_MODEL_PATH=""

# =============================================================================
# Local Model Paths Configuration
# =============================================================================
# TODO: Update these paths to match your actual model locations
# These models should be downloaded and served via vLLM

export LLAMA_GUARD_MODEL_PATH=""
export WILDGUARD_MODEL_PATH=""
export GUARDREASONER_MODEL_PATH=""
export SHIELDGEMMA_MODEL_PATH=""

# =============================================================================
# Directory and Execution Setup
# =============================================================================

# Change to script directory
cd "$(dirname "$0")"

# Create output directory structure
BASE_PATH="./my_output"
INPUT_PATH="$BASE_PATH/inputs"

echo "Creating output directory structure..."
mkdir -p "$INPUT_PATH"

# =============================================================================
# Model and Guard Processing Logic  
# =============================================================================

# Convert model and guard strings to arrays for processing
IFS=',' read -ra MODEL_ARRAY <<< "$TARGET_MODEL"
IFS=',' read -ra GUARD_ARRAY <<< "$SAFETY_GUARDS"

echo "Processing ${#MODEL_ARRAY[@]} model(s) with ${#GUARD_ARRAY[@]} guard(s)..."
echo

# Process each model-guard combination
for TARGET_MODEL in "${MODEL_ARRAY[@]}"; do
    echo "=========================================="
    echo "Processing Target Model: $TARGET_MODEL"
    echo "=========================================="
    
    # Set current model environment variable
    export TARGET_MODEL="$TARGET_MODEL"
    
    # Create model-specific directory
    MODEL_PATH="$BASE_PATH/models/$TARGET_MODEL"
    mkdir -p "$MODEL_PATH"
    
    # Process each guard for current model
    for SAFETY_GUARD in "${GUARD_ARRAY[@]}"; do
        echo "----------------------------------------"
        echo "  Testing with Safety Guard: $SAFETY_GUARD"
        echo "----------------------------------------"
        
        # Set current guard environment variable
        export SAFETY_GUARD="$SAFETY_GUARD"
        
        # Define paths for current combination
        GUARD_PATH="$MODEL_PATH/guards/$SAFETY_GUARD"
        OUTPUT_PATH="$GUARD_PATH/outputs"
        
        # Check if output already exists to avoid reprocessing
        if [ -d "$OUTPUT_PATH" ] && [ "$(ls -A $OUTPUT_PATH 2>/dev/null)" ]; then
            echo "  ⚠️  Output directory already exists and contains files:"
            echo "     $OUTPUT_PATH"
            echo "     Skipping to avoid overwriting existing results..."
            echo
            continue
        fi
        
        # Create output directory structure for current combination
        echo "  📁 Creating directory: $OUTPUT_PATH"
        mkdir -p "$GUARD_PATH"
        mkdir -p "$OUTPUT_PATH"
        
        # =====================================================
        # Execute RepSim Attack on AdvBench Dataset
        # =====================================================
        
        echo "  🚀 Starting AdvBench attack for $TARGET_MODEL with $SAFETY_GUARD..."
        echo
        
        # Configure attack parameters
        dataset_name="advbench"
        input_file="./get_dataset/random_200_advbench.json"
        backup_file="$OUTPUT_PATH/advbench_attack_backup.json"
        final_output_file="$OUTPUT_PATH/advbench_attack_results.json"
        
        # Execute the main RepSim attack script
        echo "  📋 Input file: $input_file"
        echo "  💾 Backup file: $backup_file"
        echo "  📊 Final output: $final_output_file"
        echo "  🧵 Threads: $THREADS"
        echo
        
        python3 main.py "$input_file" "$dataset_name" "$backup_file" "$final_output_file" "$THREADS"
        
        # Check if attack completed successfully
        if [ $? -eq 0 ]; then
            echo "  ✅ AdvBench attack completed successfully!"
        else
            echo "  ❌ AdvBench attack failed!"
        fi
        
        echo
        echo "----------------------------------------"
        echo "  ✅ Completed Safety Guard: $SAFETY_GUARD"
        echo "----------------------------------------"
        echo
    done
    
    echo "=========================================="
    echo "✅ Completed Target Model: $TARGET_MODEL"
    echo "=========================================="
    echo
done

echo "🎉 All model-guard combinations completed successfully!"
echo "📊 Results can be found in: $BASE_PATH/models/"