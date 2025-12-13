#!/bin/bash
cp -f /workspaces/ComfyUI_KuAi_Power/.env.sample /workspaces/ComfyUI_KuAi_Power/.env

code server /workspaces/ComfyUI_KuAi_Power/.env

read -p "修改.env中的api信息及项目地址，完成了后请输入y：" yn
if [ "$yn" == "y" ] || [ "$yn" == "Y" ]; then
    bash /workspaces/ComfyUI_KuAi_Power/start.sh
fi