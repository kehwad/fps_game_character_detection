# 快速开始指南 / Quick Start Guide

## 如何适配你的游戏 / How to Adapt to Your Game

### 步骤1：准备环境 / Step 1: Setup Environment
```bash
# 克隆项目
git clone https://github.com/kehwad/fps_game_character_detection.git
cd fps_game_character_detection

# 安装依赖
cd yolov5-7.0
pip install -r requirements.txt
```

### 步骤2：收集数据 / Step 2: Collect Data
1. 复制并修改数据收集脚本：
```bash
cp templates/universal_data_collector.py my_game_collector.py
```

2. 编辑 `my_game_collector.py`，修改游戏相关配置：
```python
GAME_NAME = "YourGameName"  # 你的游戏名称
CATEGORIES = {
    0: "ENEMY",     # 敌方
    1: "FRIENDLY",  # 友方
}
```

3. 运行数据收集：
```bash
python my_game_collector.py
```

### 步骤3：标注数据 / Step 3: Label Data
1. 下载 [LabelImg](https://github.com/heartexlabs/labelImg/releases)
2. 设置YOLO格式
3. 标注收集的图片

### 步骤4：配置训练 / Step 4: Configure Training
1. 复制配置模板：
```bash
cp templates/csgo.yaml yolov5-7.0/data/my_game.yaml
```

2. 修改配置文件中的路径和类别

### 步骤5：训练模型 / Step 5: Train Model
```bash
cd yolov5-7.0
python train.py --img 640 --batch 16 --epochs 300 --data my_game.yaml --weights yolov5n.pt
```

### 步骤6：测试和部署 / Step 6: Test and Deploy
```bash
# 测试模型
python detect.py --weights runs/train/exp/weights/best.pt --source path/to/test/images

# 实时检测（修改predict.py中的模型路径）
python predict.py
```

## 常见问题 / FAQ

**Q: 需要多少训练数据？**
A: 每个类别建议至少500-1000张高质量标注图片。

**Q: 训练需要多长时间？**
A: 根据数据量和硬件，通常需要几小时到一天时间。

**Q: 如何提高检测精度？**
A: 1) 增加训练数据 2) 改进标注质量 3) 调整训练参数 4) 使用更大的模型

**Q: 检测速度太慢怎么办？**
A: 1) 使用更小的模型(yolov5n) 2) 降低输入分辨率 3) 优化代码

更多详细信息请查看 [GAME_ADAPTATION_GUIDE.md](GAME_ADAPTATION_GUIDE.md)