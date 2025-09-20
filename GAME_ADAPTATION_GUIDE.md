# 游戏适配指南 / Game Adaptation Guide

本指南将帮助你将此FPS角色检测系统适配到其他游戏。

## 概述 / Overview

此项目基于YOLOv5对FPS游戏中的角色进行检测。要适配到其他游戏，主要需要：
1. 收集新游戏的训练数据
2. 修改配置文件
3. 训练新模型
4. 调整检测参数

## 1. 数据收集 / Data Collection

### 修改数据收集脚本
编辑 `sample_util/collecting_data.py` 文件：

```python
# 根据新游戏调整截图区域大小
# 原代码使用640x640，你可能需要调整
monitor = {'left': left, 'top': top, 'width': 640, 'height': 640}

# 修改类别标签和保存路径
def screenshot(share_dict):
    # 为你的游戏创建相应的目录
    os.makedirs('./data/TEAM_A', exist_ok=True)  # 替换为你的第一个类别
    os.makedirs('./data/TEAM_B', exist_ok=True)  # 替换为你的第二个类别
    
    # 修改按键绑定（可选）
    # 按'F'键截图，按'`'键切换类别
```

### 数据收集建议
1. **多样化场景**：收集不同地图、光照条件、角度的图片
2. **角色多样性**：包含不同皮肤、装备、姿势的角色
3. **数量建议**：每个类别至少500-1000张图片
4. **图片质量**：确保目标清晰可见，避免模糊图片

## 2. 数据标注 / Data Annotation

### 使用LabelImg标注工具
1. 下载 [LabelImg](https://github.com/heartexlabs/labelImg/releases)
2. 安装并运行LabelImg
3. 设置标注格式为YOLO格式
4. 为每个游戏角色/目标创建标注框
5. 标注时使用一致的类别名称

### 标注质量控制
- 确保标注框紧贴目标边界
- 保持标注一致性
- 定期检查和修正标注错误

## 3. 配置文件修改 / Configuration Files

### 创建新的数据配置文件
复制 `yolov5-7.0/data/cf.yaml` 并创建新文件（如 `your_game.yaml`）：

```yaml
# YOLOv5 🚀 by Ultralytics, GPL-3.0 license
# 你的游戏数据集配置

# 数据集根目录
path: ../your_game_data  # 替换为你的数据路径
train: images  # 训练图片路径
val: images    # 验证图片路径  
test:          # 测试图片路径（可选）

# 类别定义
names:
  0: enemy_team     # 替换为你的第一个类别
  1: friendly_team  # 替换为你的第二个类别
  # 添加更多类别如需要
```

### 修改模型配置文件
复制 `yolov5-7.0/models/yolov5n.yaml` 并修改：

```yaml
# 修改类别数量
nc: 2  # 改为你需要检测的类别数量

# 其他参数通常不需要修改
depth_multiple: 0.33
width_multiple: 0.25
```

## 4. 训练过程 / Training Process

### 基本训练命令
```bash
cd yolov5-7.0
python train.py --img 640 --batch 16 --epochs 300 --data your_game.yaml --weights yolov5n.pt --cache
```

### 训练参数说明
- `--img 640`: 输入图片尺寸
- `--batch 16`: 批次大小（根据显存调整）
- `--epochs 300`: 训练轮数
- `--data your_game.yaml`: 你的数据配置文件
- `--weights yolov5n.pt`: 预训练模型
- `--cache`: 缓存数据加速训练

### 高级训练选项
```bash
# 使用更大的模型（更好的精度但更慢）
python train.py --img 640 --batch 8 --epochs 300 --data your_game.yaml --weights yolov5s.pt

# 添加数据增强
python train.py --img 640 --batch 16 --epochs 300 --data your_game.yaml --weights yolov5n.pt --hyp data/hyps/hyp.scratch-med.yaml

# 继续训练（从中断点恢复）
python train.py --resume runs/train/exp/weights/last.pt
```

## 5. 模型测试与验证 / Model Testing

### 测试训练好的模型
```bash
# 在测试图片上运行检测
python detect.py --weights runs/train/exp/weights/best.pt --source path/to/test/images

# 在游戏截图上测试
python detect.py --weights runs/train/exp/weights/best.pt --source 0  # 使用摄像头
```

### 评估模型性能
```bash
# 运行验证脚本
python val.py --weights runs/train/exp/weights/best.pt --data your_game.yaml --img 640
```

## 6. 实时检测适配 / Real-time Detection Adaptation

### 修改预测脚本
编辑 `predict.py` 文件：

```python
# 1. 更新模型路径
weights = 'runs/train/exp/weights/best.pt'  # 你训练的模型路径

# 2. 调整检测区域（如果需要）
Detect = 640  # 根据你的游戏调整检测区域大小

# 3. 修改类别过滤
pred = non_max_suppression(pred, conf_thres=0.6, iou_thres=0.45, classes=(0,1), max_det=2)[0]
# 将classes参数改为你的类别索引

# 4. 调整置信度阈值
conf_thres = 0.6  # 根据你的模型性能调整

# 5. 修改目标选择逻辑（如果需要）
# 例如：优先攻击距离最近的敌人而不是最远的
x,y,w,h = target_list[dis_list.index(min(dis_list))]  # 最近的目标
```

## 7. 不同游戏的特殊考虑 / Game-Specific Considerations

### Counter-Strike系列
- 注意T方和CT方的不同皮肤
- 考虑烟雾弹和闪光弹的影响
- 调整检测区域避开UI元素

### Valorant
- 角色技能特效可能影响检测
- 考虑不同地图的光照条件
- 注意角色模型的多样性

### Apex Legends / Fortnite
- 第三人称视角需要不同的检测策略
- 建筑和地形遮挡更复杂
- 移动速度更快，需要更低的延迟

### 彩虹六号围攻
- 破坏环境和动态光照
- 角色装备和皮肤变化大
- 需要考虑防守和进攻方的不同

## 8. 性能优化 / Performance Optimization

### 提高检测速度
```python
# 使用更小的模型
weights = 'yolov5n.pt'  # nano版本最快

# 降低输入分辨率
im = letterbox(im0, (416, 416), stride=32, auto=True)[0]  # 从640降低到416

# 减少检测目标数量
pred = non_max_suppression(pred, conf_thres=0.7, iou_thres=0.45, classes=(0,1), max_det=1)[0]
```

### 提高检测精度
```python
# 使用更大的模型
weights = 'yolov5l.pt'  # large版本精度更高

# 提高输入分辨率
im = letterbox(im0, (832, 832), stride=32, auto=True)[0]  # 提高分辨率

# 降低置信度阈值
pred = non_max_suppression(pred, conf_thres=0.4, iou_thres=0.45, classes=(0,1), max_det=5)[0]
```

## 9. 常见问题解决 / Troubleshooting

### 检测精度低
1. 增加训练数据量
2. 改善数据标注质量
3. 调整训练参数（更多epochs，不同学习率）
4. 使用更大的模型

### 检测速度慢
1. 使用更小的模型（yolov5n）
2. 降低输入分辨率
3. 减少检测区域大小
4. 优化GPU/CPU使用

### 误检测过多
1. 提高置信度阈值
2. 调整NMS的IoU阈值
3. 增加负样本训练数据
4. 使用更精确的标注

### 漏检测较多
1. 降低置信度阈值
2. 增加训练数据的多样性
3. 检查标注质量
4. 考虑使用数据增强

## 10. 法律和道德考虑 / Legal and Ethical Considerations

### 重要提醒
1. **仅用于学习研究**：本项目仅供学习和研究目的
2. **遵守游戏规则**：使用前请查看游戏的服务条款
3. **公平竞争**：避免在正式比赛中使用
4. **尊重其他玩家**：保持良好的游戏环境

### 合规建议
- 仅在私人服务器或练习模式下测试
- 不要在排位或竞技模式中使用
- 尊重游戏开发者的权利
- 遵守当地法律法规

## 结论 / Conclusion

通过遵循此指南，你应该能够成功地将此检测系统适配到其他FPS游戏。记住，成功的关键在于：
1. 高质量的训练数据
2. 正确的配置设置
3. 充分的训练时间
4. 仔细的参数调优

如有问题，建议查看YOLOv5官方文档或在相关社区寻求帮助。

祝你训练愉快！ / Happy training!