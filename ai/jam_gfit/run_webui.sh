#!/bin/bash

# Stable Diffusion WebUI 실행 스크립트
# 커밋 해시 검증을 건너뛰고 WebUI를 시작합니다

export STABLE_DIFFUSION_COMMIT_HASH=""
export STABLE_DIFFUSION_XL_COMMIT_HASH=""
export K_DIFFUSION_COMMIT_HASH=""
export BLIP_COMMIT_HASH=""

cd "$(dirname "$0")/stable-diffusion-webui"
./webui.sh --skip-torch-cuda-test --listen "$@"
