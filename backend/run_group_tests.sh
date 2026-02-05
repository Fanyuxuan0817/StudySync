#!/bin/bash

# 群组模块测试脚本
# 运行所有群组相关的测试

echo "开始运行群组模块测试..."

# 切换到后端目录
cd e:\workspace\StudySync\backend

# 运行群组模块单元测试
echo "运行群组模块单元测试..."
python -m pytest tests/test_groups.py -v

# 检查测试覆盖率
echo "检查测试覆盖率..."
python -m pytest tests/test_groups.py --cov=app.routes.groups --cov-report=html

echo "测试完成！"