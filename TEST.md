# DiagnosticAssistant 图形基础类测试方案

## 概述

本文档提供DiagnosticAssistant项目中图形基础类的测试方案。根据PROJECT_PLAN.md，今天是3月2日（周日），已完成图形基础类的开发工作。本测试方案旨在确保图形基础类的功能完整性和稳定性。

## 测试目标

1. 验证图形基础类的核心功能
2. 确保用户交互的流畅性
3. 验证数据序列化/反序列化的正确性
4. 测试性能和稳定性
5. 确保代码质量符合项目标准

## 测试环境

### 硬件环境
- 操作系统：Windows 10/11, macOS, Linux
- 处理器：Intel i5或同等性能以上
- 内存：8GB以上
- 显卡：支持OpenGL 2.0以上

### 软件环境
- Python 3.8+
- PySide6 6.5.0+
- 依赖包：requirements.txt中列出的所有包

### 测试工具
- pytest 7.0.0+
- pytest-qt 4.0.0+
- coverage 7.0+

## 测试范围

### 1. HardwareNodeItem类测试
- 节点创建和初始化
- 自定义绘制功能
- 鼠标交互（拖拽、选择、右键菜单）
- 连接点管理
- 序列化/反序列化

### 2. ConnectionLineItem类测试
- 连接线创建和初始化
- 贝塞尔曲线路径计算
- 箭头绘制
- 标签显示
- 节点移动时的路径更新
- 序列化/反序列化

### 3. HardwareScene类测试
- 场景管理（节点和连接的生命周期）
- 连接创建逻辑
- 选择和多选功能
- 场景状态管理
- 序列化/反序列化

### 4. HardwareView类测试
- 视图缩放和平移
- 鼠标事件处理
- 网格和对齐功能
- 键盘快捷键
- 视图状态管理

### 5. 集成测试
- 组件间协作
- 完整工作流程
- 性能测试
- 用户体验测试

## 详细测试用例

### 单元测试用例

#### HardwareNodeItem测试用例

**TC-NODE-001: 节点创建测试**
- 输入：有效的硬件类型、名称、位置
- 预期：成功创建节点，正确设置属性
- 验证：节点ID、名称、类型、位置正确

**TC-NODE-002: 节点绘制测试**
- 输入：不同硬件类型的节点
- 预期：正确绘制圆角矩形、文本、连接点
- 验证：颜色、文本、连接点符合类型定义

**TC-NODE-003: 节点拖拽测试**
- 输入：鼠标拖拽节点
- 预期：节点跟随鼠标移动，发出移动信号
- 验证：位置更新，信号正确发出

**TC-NODE-004: 节点选择测试**
- 输入：鼠标点击节点
- 预期：节点被选中，显示选中样式
- 验证：选中状态正确，样式变化

**TC-NODE-005: 右键菜单测试**
- 输入：右键点击节点
- 预期：显示上下文菜单
- 验证：菜单项正确，功能可用

**TC-NODE-006: 连接点管理测试**
- 输入：请求不同侧的连接点
- 预期：返回正确的连接点坐标
- 验证：坐标计算正确

**TC-NODE-007: 序列化测试**
- 输入：节点实例
- 预期：生成正确的字典表示
- 验证：字典包含所有必要属性

**TC-NODE-008: 反序列化测试**
- 输入：节点字典数据
- 预期：成功创建节点实例
- 验证：节点属性与原始数据一致

#### ConnectionLineItem测试用例

**TC-CONN-001: 连接线创建测试**
- 输入：源节点、目标节点、连接类型
- 预期：成功创建连接线
- 验证：连接线属性正确设置

**TC-CONN-002: 路径计算测试**
- 输入：不同位置的节点
- 预期：计算正确的贝塞尔曲线路径
- 验证：路径平滑，连接点正确

**TC-CONN-003: 箭头绘制测试**
- 输入：需要箭头的连接类型
- 预期：正确绘制箭头
- 验证：箭头方向正确，样式符合类型

**TC-CONN-004: 标签显示测试**
- 输入：带标签的连接线
- 预期：在连接线中间显示标签
- 验证：标签位置正确，可读性好

**TC-CONN-005: 节点移动更新测试**
- 输入：移动连接的节点
- 预期：连接线路径自动更新
- 验证：路径保持连接，无断裂

**TC-CONN-006: 选择测试**
- 输入：点击连接线
- 预期：连接线被选中
- 验证：选中样式正确

**TC-CONN-007: 序列化测试**
- 输入：连接线实例
- 预期：生成正确的字典表示
- 验证：包含源节点、目标节点、类型等信息

**TC-CONN-008: 反序列化测试**
- 输入：连接线字典数据
- 预期：成功创建连接线实例
- 验证：连接线属性与原始数据一致

#### HardwareScene测试用例

**TC-SCENE-001: 场景初始化测试**
- 输入：创建HardwareScene实例
- 预期：成功初始化，设置默认属性
- 验证：场景矩形、网格设置正确

**TC-SCENE-002: 节点添加测试**
- 输入：添加新节点
- 预期：节点添加到场景和数据存储
- 验证：节点计数增加，信号发出

**TC-SCENE-003: 节点移除测试**
- 输入：移除节点
- 预期：节点及其连接被移除
- 验证：节点计数减少，相关连接被清理

**TC-SCENE-004: 连接创建测试**
- 输入：创建两个节点间的连接
- 预期：成功创建连接线
- 验证：连接计数增加，信号发出

**TC-SCENE-005: 连接移除测试**
- 输入：移除连接
- 预期：连接线被移除
- 验证：连接计数减少，信号发出

**TC-SCENE-006: 选择管理测试**
- 输入：选择多个项目
- 预期：正确管理选择状态
- 验证：选择信号正确发出

**TC-SCENE-007: 连接模式测试**
- 输入：进入连接模式，点击源节点和目标节点
- 预期：成功创建连接
- 验证：连接创建流程正确

**TC-SCENE-008: 框选测试**
- 输入：在空白区域拖拽框选
- 预期：框选矩形内的项目被选中
- 验证：选择正确，矩形显示正常

**TC-SCENE-009: 序列化测试**
- 输入：包含节点和连接的场景
- 预期：生成完整的字典表示
- 验证：包含所有节点、连接和场景设置

**TC-SCENE-010: 反序列化测试**
- 输入：场景字典数据
- 预期：成功恢复场景状态
- 验证：节点、连接、设置与原始一致

#### HardwareView测试用例

**TC-VIEW-001: 视图初始化测试**
- 输入：创建HardwareView实例
- 预期：成功初始化，设置默认属性
- 验证：渲染提示、交互模式正确

**TC-VIEW-002: 缩放测试**
- 输入：鼠标滚轮缩放
- 预期：视图正确缩放
- 验证：缩放比例更新，信号发出

**TC-VIEW-003: 平移测试**
- 输入：Alt+左键拖拽或中键拖拽
- 预期：视图平移
- 验证：视图位置更新，信号发出

**TC-VIEW-004: 网格显示测试**
- 输入：切换网格显示
- 预期：网格显示/隐藏
- 验证：网格状态正确更新

**TC-VIEW-005: 网格对齐测试**
- 输入：启用网格对齐，添加节点
- 预期：节点位置对齐到网格
- 验证：位置符合网格对齐规则

**TC-VIEW-006: 键盘快捷键测试**
- 输入：各种键盘快捷键
- 预期：执行相应操作
- 验证：快捷键功能正常

**TC-VIEW-007: 右键菜单测试**
- 输入：右键点击视图
- 预期：显示视图菜单
- 验证：菜单项正确，功能可用

**TC-VIEW-008: 适应视图测试**
- 输入：点击"适应视图"按钮
- 预期：缩放以适应所有内容
- 验证：所有内容在视图中可见

### 集成测试用例

**TC-INT-001: 完整工作流程测试**
- 步骤：
  1. 创建新场景
  2. 添加多个节点
  3. 创建节点间的连接
  4. 拖拽节点移动位置
  5. 选择多个项目
  6. 保存场景为JSON
  7. 清空场景
  8. 从JSON加载场景
- 预期：所有操作成功，数据完整恢复
- 验证：操作流畅，数据一致性

**TC-INT-002: 性能测试**
- 输入：添加大量节点（100+）和连接
- 预期：界面响应流畅
- 验证：帧率>30fps，内存使用<200MB

**TC-INT-003: 用户体验测试**
- 输入：新手用户操作
- 预期：10分钟内完成基本操作
- 验证：操作符合直觉，无需查阅文档

**TC-INT-004: 错误处理测试**
- 输入：各种异常操作（如重复ID、无效类型等）
- 预期：优雅处理错误，不崩溃
- 验证：错误提示友好，恢复路径明确

## 测试执行计划

### 阶段一：单元测试（3月3日）
- 执行所有单元测试用例
- 目标：代码覆盖率>80%
- 工具：pytest + coverage

### 阶段二：集成测试（3月4日）
- 执行集成测试用例
- 目标：关键路径100%覆盖
- 工具：手动测试 + 自动化脚本

### 阶段三：性能测试（3月5日）
- 执行性能测试用例
- 目标：满足性能指标
- 工具：性能分析工具

### 阶段四：用户体验测试（3月6日）
- 邀请测试人员试用
- 收集反馈意见
- 优化用户体验

## 测试工具和脚本

### 单元测试脚本示例

```python
# test_hardware_node.py
import pytest
from PySide6.QtCore import Qt, QPointF
from gui.src.graphics.hardware_node import HardwareNodeItem

class TestHardwareNodeItem:
    def test_node_creation(self):
        """测试节点创建"""
        node = HardwareNodeItem(
            hardware_id="test_node",
            name="测试节点",
            hw_type="controller",
            x=100,
            y=100
        )
        
        assert node.hardware_id == "test_node"
        assert node.name == "测试节点"
        assert node.type == "controller"
        assert node.pos() == QPointF(100, 100)
    
    def test_node_paint(self, qtbot):
        """测试节点绘制"""
        node = HardwareNodeItem("test", "测试", "controller")
        
        # 模拟绘制（需要QApplication环境）
        # 这里可以测试绘制相关的逻辑
        
    def test_node_serialization(self):
        """测试节点序列化"""
        node = HardwareNodeItem(
            hardware_id="test_node",
            name="测试节点",
            hw_type="controller",
            x=100,
            y=100,
            properties={"protocol": "CAN"}
        )
        
        data = node.to_dict()
        
        assert data['id'] == "test_node"
        assert data['name'] == "测试节点"
        assert data['type'] == "controller"
        assert data['position']['x'] == 100
        assert data['position']['y'] == 100
        assert data['properties']['protocol'] == "CAN"
    
    def test_node_deserialization(self):
        """测试节点反序列化"""
        data = {
            'id': 'test_node',
            'name': '测试节点',
            'type': 'controller',
            'position': {'x': 100, 'y': 100},
            'size': {'width': 120, 'height': 60},
            'properties': {'protocol': 'CAN'}
        }
        
        node = HardwareNodeItem.from_dict(data)
        
        assert node.hardware_id == "test_node"
        assert node.name == "测试节点"
        assert node.type == "controller"
        assert node.pos() == QPointF(100, 100)
```

### 集成测试脚本示例

```python
# test_integration.py
import pytest
import json
from PySide6.QtWidgets import QApplication
from gui.src.graphics import HardwareScene, HardwareView

class TestIntegration:
    def test_complete_workflow(self, qtbot):
        """测试完整工作流程"""
        # 创建场景
        scene = HardwareScene()
        
        # 添加节点
        node1 = scene.add_node("节点1", "controller", 100, 100)
        node2 = scene.add_node("节点2", "sensor", 300, 100)
        
        assert len(scene.nodes) == 2
        
        # 创建连接
        connection = scene.create_connection(node1, node2, "ethernet_cable", "测试连接")
        
        assert len(scene.connections) == 1
        
        # 序列化
        scene_data = scene.to_dict()
        
        assert scene_data['metadata']['node_count'] == 2
        assert scene_data['metadata']['connection_count'] == 1
        
        # 反序列化
        new_scene = HardwareScene()
        new_scene.from_dict(scene_data)
        
        assert len(new_scene.nodes) == 2
        assert len(new_scene.connections) == 1
```

### 性能测试脚本示例

```python
# test_performance.py
import time
from gui.src.graphics import HardwareScene

def test_performance_large_scene():
    """测试大量节点的性能"""
    scene = HardwareScene()
    
    # 添加100个节点
    start_time = time.time()
    
    for i in range(100):
        scene.add_node(f"节点{i}", "controller", i*20, i*20)
    
    add_time = time.time() - start_time
    print(f"添加100个节点耗时: {add_time:.2f}秒")
    
    # 添加连接（每两个节点连接）
    start_time = time.time()
    
    nodes = list(scene.nodes.values())
    for i in range(len(nodes) - 1):
        scene.create_connection(nodes[i], nodes[i+1], "ethernet_cable")
    
    conn_time = time.time() - start_time
    print(f"添加99个连接耗时: {conn_time:.2f}秒")
    
    # 序列化性能
    start_time = time.time()
    scene_data = scene.to_dict()
    serialize_time = time.time() - start_time
    print(f"序列化耗时: {serialize_time:.2f}秒")
    
    # 性能要求
    assert add_time < 2.0  # 添加100个节点应在2秒内
    assert conn_time < 3.0  # 添加99个连接应在3秒内
    assert serialize_time < 1.0  # 序列化应在1秒内
```

## 测试数据

### 测试配置文件示例

```json
{
  "test_cases": {
    "basic_operation": {
      "description": "基本操作测试",
      "nodes": [
        {"name": "5G WiFi路由器", "type": "wireless_communication", "x": 100, "y": 100},
        {"name": "Debug BOX", "type": "debug_tool", "x": 300, "y": 100},
        {"name": "车辆控制器", "type": "controller", "x": 500, "y": 100}
      ],
      "connections": [
        {"from": "5G WiFi路由器", "to": "Debug BOX", "type": "ethernet_cable"},
        {"from": "Debug BOX", "to": "车辆控制器", "type": "ethernet_cable"}
      ]
    },
    "complex_scene": {
      "description": "复杂场景测试",
      "nodes": 50,
      "connections": 75,
      "node_types": ["controller", "sensor", "debug_tool", "wireless_communication"],
      "connection_types": ["ethernet_cable", "can_bus", "usb_cable"]
    }
  }
}
```

## 测试报告模板

### 测试执行报告

```
测试执行报告
============

项目名称: DiagnosticAssistant
测试阶段: 图形基础类测试
测试日期: 2025年3月2日
测试人员: [测试人员姓名]

测试概要
--------
- 总测试用例数: 38
- 执行用例数: 38
- 通过用例数: [数字]
- 失败用例数: [数字]
- 跳过用例数: [数字]
- 测试覆盖率: [百分比]%

详细结果
--------
1. 单元测试
   - HardwareNodeItem: [通过/失败数]
   - ConnectionLineItem: [通过/失败数]
   - HardwareScene: [通过/失败数]
   - HardwareView: [通过/失败数]

2. 集成测试
   - 完整工作流程: [通过/失败]
   - 性能测试: [通过/失败]
   - 用户体验测试: [通过/失败]

3. 性能指标
   - 响应时间: [数值]
   - 内存使用: [数值]
   -