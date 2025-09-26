#!/bin/bash

# Configure your environment
export CUDA_VISIBLE_DEVICES=0  # Modify according to your GPU setup
export NCCL_SOCKET_IFNAME=eth0  # Modify according to your network interface            
export NCCL_DEBUG=INFO  
export NCCL_IB_DISABLE=1             
export NCCL_P2P_DISABLE=1

# Set your conda/python environment path
# export PATH="/path/to/your/conda/envs/your_env/bin:$PATH"

# TODO: Replace with your actual Qwen3-8B-abliterated model path
MODEL_PATH="./models/Qwen3-8B-abliterated"

vllm serve \
  $MODEL_PATH \
  --tensor-parallel-size 1 \
  --port 8002
