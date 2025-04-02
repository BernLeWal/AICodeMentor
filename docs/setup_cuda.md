# Setup Huggingface Transformers library with local CUDA

To use the LLMs on your local machine with the installed GPU you need to fulfil the following installation steps:

## CUDA

* Install the latest drivers from NVIDIA with the `nvidia-smi` tool
* Run `nvidia-smi` tool, to check the supported CUDA versions.

On 4.8.2023 for my RTX2080 it was:
```
PS > nvidia-smi
+---------------------------------------------------------------------------------------+
| NVIDIA-SMI 531.79                 Driver Version: 531.79       CUDA Version: 12.1     |
|-----------------------------------------+----------------------+----------------------+
| GPU  Name                      TCC/WDDM | Bus-Id        Disp.A | Volatile Uncorr. ECC |
| Fan  Temp  Perf            Pwr:Usage/Cap|         Memory-Usage | GPU-Util  Compute M. |
|                                         |                      |               MIG M. |
|=========================================+======================+======================|
|   0  NVIDIA GeForce RTX 2080 Ti    WDDM | 00000000:01:00.0  On |                  N/A |
| 35%   30C    P8               27W / 260W|    469MiB / 11264MiB |     10%      Default |
|                                         |                      |                  N/A |
+-----------------------------------------+----------------------+----------------------+
```

## PyTorch

Fetch PIP install command from PyTorch Website: https://pytorch.org/get-started/locally/ 

On 4.8.2023 for my RTX2080 it was:
```
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
```

Alternative: If you have only a CPU (without GPU) then it is the following command:
```
pip install torch torchvision torchaudio
```

## Transformers

```
pip install transformers accelerate
```
