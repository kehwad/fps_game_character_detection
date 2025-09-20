# 安全更新说明 / Security Updates

## 概述 / Overview

本次更新修复了项目中的多个安全漏洞，提高了代码的安全性和健壮性。

## 修复的漏洞 / Fixed Vulnerabilities

### 1. eval() 函数安全漏洞 (Critical)

**问题描述**：
- 在 `yolov5-7.0/models/yolo.py` 中使用了不安全的 `eval()` 函数
- 在 `yolov5-7.0/models/common.py` 中使用了不安全的 `eval()` 函数
- 这可能导致代码注入攻击

**修复措施**：
- 添加了安全的模块和激活函数映射表
- 实现了 `safe_eval()` 函数替代不安全的 `eval()` 调用
- 使用 `ast.literal_eval()` 处理字面量表达式
- 添加了输入验证和白名单机制

**受影响文件**：
- `yolov5-7.0/models/yolo.py`: 行304, 311, 314
- `yolov5-7.0/models/common.py`: 行373

### 2. 路径遍历漏洞 (Medium)

**问题描述**：
- 数据收集脚本直接使用时间戳作为文件名，未进行输入验证
- 可能存在路径遍历攻击风险

**修复措施**：
- 添加了 `sanitize_filename()` 函数
- 使用 `os.path.join()` 安全构建文件路径
- 限制文件名长度，移除危险字符
- 确保输出目录安全性

**受影响文件**：
- `sample_util/collecting_data.py`

### 3. 输入验证加强

**新增功能**：
- 添加了输入验证机制
- 改进了错误处理
- 增强了日志记录

## 安全改进详情 / Security Improvements Details

### safe_eval() 函数

```python
def safe_eval(expr, allowed_names=None):
    """Safely evaluate expressions using whitelisted names"""
    if not isinstance(expr, str):
        return expr
    
    # Try to parse as literal first
    try:
        return ast.literal_eval(expr)
    except (ValueError, SyntaxError):
        pass
    
    # Check against allowed mappings
    if allowed_names:
        if expr in allowed_names:
            return allowed_names[expr]
    
    # If it's a simple numeric or boolean expression, try to evaluate safely
    try:
        # Only allow safe expressions with numbers, basic operators, and brackets
        safe_chars = set('0123456789+-*/().[], ')
        if all(c in safe_chars for c in expr):
            return ast.literal_eval(expr)
    except (ValueError, SyntaxError):
        pass
    
    # If we can't safely evaluate, return the string as-is and log a warning
    LOGGER.warning(f"Could not safely evaluate expression: {expr}")
    return expr
```

### 安全模块映射

添加了预定义的安全模块映射，避免动态代码执行：

```python
MODULE_MAP = {
    'Conv': Conv,
    'DWConv': DWConv,
    'Bottleneck': Bottleneck,
    # ... 其他安全的模块映射
}

ACTIVATION_MAP = {
    'nn.SiLU()': nn.SiLU(),
    'nn.ReLU()': nn.ReLU(),
    # ... 其他安全的激活函数映射
}
```

### 文件名安全处理

```python
def sanitize_filename(filename):
    """Sanitize filename to prevent path traversal attacks"""
    # Remove any directory separators and special characters
    filename = re.sub(r'[<>:"/\\|?*]', '', str(filename))
    # Limit length to prevent filesystem issues
    filename = filename[:50] if len(filename) > 50 else filename
    return filename
```

## 向后兼容性 / Backward Compatibility

所有安全修复都保持了向后兼容性：
- 现有的模型配置文件仍然可以正常工作
- API接口保持不变
- 训练和推理流程不受影响

## 建议的最佳实践 / Recommended Best Practices

### 1. 定期更新依赖

```bash
# 更新Python包
pip install --upgrade -r requirements.txt

# 检查安全漏洞
pip audit
```

### 2. 验证输入数据

- 对所有外部输入进行验证
- 使用白名单而不是黑名单
- 限制文件路径和文件名

### 3. 监控和日志

- 启用详细日志记录
- 监控异常访问模式
- 定期检查日志文件

### 4. 运行环境安全

```bash
# 使用虚拟环境
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或
venv\Scripts\activate     # Windows

# 最小权限原则
# 仅给必要的文件和目录读写权限
```

## 测试验证 / Testing Validation

为确保安全修复不影响功能：

### 1. 模型加载测试
```bash
cd yolov5-7.0
python -c "
from models.yolo import Model
model = Model('models/yolov5n.yaml', ch=3, nc=2)
print('Model loaded successfully')
"
```

### 2. 数据收集测试
```bash
cd sample_util
python collecting_data.py
# 检查是否能正常创建目录和文件
```

### 3. 训练流程测试
```bash
cd yolov5-7.0
python train.py --img 640 --batch 1 --epochs 1 --data data/cf.yaml --weights yolov5n.pt --cache
```

## 已知限制 / Known Limitations

1. **性能影响**：安全检查可能带来轻微的性能开销
2. **兼容性**：某些非标准的模型配置可能需要更新
3. **动态加载**：不再支持动态代码执行，所有模块需要预定义

## 未来计划 / Future Plans

1. **持续监控**：定期扫描新的安全漏洞
2. **依赖更新**：保持依赖库的最新版本
3. **安全审计**：定期进行安全代码审查
4. **社区反馈**：收集和处理安全相关的问题报告

## 报告安全问题 / Reporting Security Issues

如果发现新的安全问题，请通过以下方式报告：
1. GitHub Issues（非敏感问题）
2. 私人邮件联系维护者（敏感问题）

## 更新日志 / Changelog

### v1.1.0 (当前版本)
- 修复了eval()安全漏洞
- 改进了文件路径处理
- 添加了输入验证
- 增强了错误处理和日志记录

### v1.0.0 (初始版本)
- 基本的FPS角色检测功能
- CF游戏适配
- YOLOv5集成

## 技术支持 / Technical Support

如需技术支持或有疑问，请：
1. 查看文档和FAQ
2. 搜索已有的Issues
3. 创建新的Issue并提供详细信息

**重要提醒**：请不要在Issue中分享敏感的安全信息。