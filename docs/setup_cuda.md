# Setup Huggingface Transformers library with local CUDA

To use the LLMs on your local machine with the installed GPU you need to fulfil the following installation steps:

## CUDA

* Install the latest drivers from NVIDIA with the `nvidia-smi` tool
* Run `nvidia-smi` tool, to check the supported CUDA versions.

On 3.4.2025 for my RTX2080 it was:
```
PS > nvidia-smi
Thu Apr  3 07:30:25 2025       
+-----------------------------------------------------------------------------------------+
| NVIDIA-SMI 572.83                 Driver Version: 572.83         CUDA Version: 12.8     |
|-----------------------------------------+------------------------+----------------------+
| GPU  Name                  Driver-Model | Bus-Id          Disp.A | Volatile Uncorr. ECC |
| Fan  Temp   Perf          Pwr:Usage/Cap |           Memory-Usage | GPU-Util  Compute M. |
|                                         |                        |               MIG M. |
|=========================================+========================+======================|
|   0  NVIDIA GeForce RTX 2080 Ti   WDDM  |   00000000:01:00.0  On |                  N/A |
| 35%   33C    P8             33W /  260W |     497MiB /  11264MiB |      2%      Default |
|                                         |                        |                  N/A |
+-----------------------------------------+------------------------+----------------------+
```

## PyTorch

Fetch PIP install command from PyTorch Website: https://pytorch.org/get-started/locally/ 

For my RTX2080 it was:
```
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu126
```

Alternative: If you have only a CPU (without GPU) then it is the following command:
```
pip install torch torchvision torchaudio
```

## Transformers

```
pip install transformers accelerate
```

## Monitoring

To monitor GPU/CPU, VRAM/RAM usage under Windows you may use the "Game Bar":
- Press Win + G to open the Game Bar.
- Click on the hamburger menu near the clock (4 bars).
- Next, select “performance” from the list.
- You will see the monitoring of CPU, GPU and RAM.


