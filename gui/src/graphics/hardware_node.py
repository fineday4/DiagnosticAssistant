"""
硬件节点图形项 - 表示车辆硬件设备的可视化矩形

继承自 QGraphicsRectItem，提供：
1. 自定义绘制和样式
2. 拖拽和选择功能
3. 右键菜单支持
4. 连接点管理
"""

from PySide6.QtCore import Qt, QRectF, QPointF, QObject
from PySide6.QtCore import Signal as PySide6Signal
from PySide6.QtGui import QPainter, QPen, QBrush, QColor, QFont, QPainterPath
from PySide6.QtWidgets import QGraphicsRectItem, QGraphicsItem, QMenu, QGraphicsSceneMouseEvent

from typing import Dict, Any, Optional, List


class HardwareNodeItem(QGraphicsRectItem, QObject):
    """硬件节点图形项，表示车辆硬件设备"""
    
    # 信号定义 - 使用重命名的Signal以避免可能的导入冲突
    node_moved = PySide6Signal(str, float, float)  # 节点ID, x, y
    node_selected = PySide6Signal(str)  # 节点ID
    node_double_clicked = PySide6Signal(str)  # 节点ID
    connection_started = PySide6Signal(str, QPointF)  # 节点ID, 起始点
    config_edit_requested = PySide6Signal(str)  # 节点ID，请求编辑配置
    
    # 硬件类型定义（基于PROJECT_PLAN.md）
    HARDWARE_TYPES = {
        "wireless_communication": {
            "name": "无线通信设备",
            "color": "#2196F3",
            "description": "无线通信设备，提供网络连接"
        },
        "debug_tool": {
            "name": "调试工具", 
            "color": "#4CAF50",
            "description": "调试和诊断工具"
        },
        "controller": {
            "name": "控制器",
            "color": "#FF9800",
            "description": "车辆控制系统"
        },
        "converter": {
            "name": "转换器",
            "color": "#9C27B0",
            "description": "协议转换设备"
        },
        "antenna": {
            "name": "天线",
            "color": "#795548",
            "description": "无线信号接收发送设备"
        },
        "sensor": {
            "name": "传感器",
            "color": "#00BCD4",
            "description": "环境感知传感器"
        },
        "compute_unit": {
            "name": "计算单元",
            "color": "#673AB7",
            "description": "数据处理和计算设备"
        },
        "power_supply": {
            "name": "电源设备",
            "color": "#F44336",
            "description": "电力供应设备"
        }
    }
    
    def __init__(self, hardware_id: str, name: str, hw_type: str, 
                 x: float = 0, y: float = 0, width: float = 120, height: float = 60,
                 properties: Optional[Dict[str, Any]] = None):
        """
        初始化硬件节点
        
        Args:
            hardware_id: 节点唯一标识符
            name: 节点显示名称
            hw_type: 硬件类型（必须是HARDWARE_TYPES中的键）
            x, y: 节点位置
            width, height: 节点大小
            properties: 附加属性字典
        """
        # 调用两个父类的__init__方法
        QGraphicsRectItem.__init__(self, 0, 0, width, height)
        QObject.__init__(self)
        
        self.hardware_id = hardware_id
        self.name = name
        self.type = hw_type
        self.properties = properties or {}
        
        # 设置位置和标志
        self.setPos(x, y)
        self.setFlag(QGraphicsItem.ItemIsMovable, True)
        self.setFlag(QGraphicsItem.ItemIsSelectable, True)
        self.setFlag(QGraphicsItem.ItemSendsGeometryChanges, True)
        self.setFlag(QGraphicsItem.ItemSendsScenePositionChanges, True)
        
        # 设置Z值确保节点在连接线上方
        self.setZValue(10)
        
        # 连接点（用于连接线的起始/结束点）
        self.connection_points = {
            'top': QPointF(width / 2, 0),
            'bottom': QPointF(width / 2, height),
            'left': QPointF(0, height / 2),
            'right': QPointF(width, height / 2)
        }
        
        # 样式配置
        self._setup_style()
        
        # 跟踪鼠标状态
        self._is_dragging = False
        self._drag_start_pos = QPointF()
        
    def _setup_style(self):
        """设置节点样式"""
        # 获取类型对应的颜色
        type_config = self.HARDWARE_TYPES.get(self.type, {})
        base_color = QColor(type_config.get('color', '#607D8B'))
        
        # 计算渐变颜色
        self.fill_color = base_color.lighter(130)  # 浅色填充
        self.border_color = base_color.darker(130)  # 深色边框
        self.text_color = QColor('#FFFFFF')
        
        # 选中状态颜色
        self.selected_fill_color = base_color.lighter(150)
        self.selected_border_color = QColor('#FF5722')
        
        # 设置画笔和画刷
        self.normal_pen = QPen(self.border_color, 2)
        self.selected_pen = QPen(self.selected_border_color, 3)
        self.normal_brush = QBrush(self.fill_color)
        self.selected_brush = QBrush(self.selected_fill_color)
        
    def paint(self, painter: QPainter, option, widget=None):
        """自定义绘制节点"""
        # 保存painter状态
        painter.save()
        
        # 设置抗锯齿
        painter.setRenderHint(QPainter.Antialiasing)
        
        # 根据选中状态选择样式
        if self.isSelected():
            painter.setPen(self.selected_pen)
            painter.setBrush(self.selected_brush)
        else:
            painter.setPen(self.normal_pen)
            painter.setBrush(self.normal_brush)
        
        # 绘制圆角矩形
        rect = self.rect()
        painter.drawRoundedRect(rect, 10, 10)
        
        # 绘制节点名称
        painter.setPen(QPen(self.text_color))
        font = QFont('Arial', 10, QFont.Bold)
        painter.setFont(font)
        
        # 计算文本位置
        text_rect = QRectF(rect)
        text_rect.setHeight(20)
        text_rect.moveTop(5)
        
        # 绘制名称（居中）
        painter.drawText(text_rect, Qt.AlignCenter, self.name)
        
        # 绘制硬件类型
        type_config = self.HARDWARE_TYPES.get(self.type, {})
        type_name = type_config.get('name', self.type)
        
        font = QFont('Arial', 8)
        painter.setFont(font)
        type_rect = QRectF(rect)
        type_rect.setHeight(15)
        type_rect.moveTop(30)
        
        painter.drawText(type_rect, Qt.AlignCenter, type_name)
        
        # 绘制连接点（小圆点）
        painter.setBrush(QBrush(QColor('#FFFFFF')))
        painter.setPen(QPen(QColor('#000000'), 1))
        
        for point_name, point_pos in self.connection_points.items():
            painter.drawEllipse(point_pos, 4, 4)
        
        # 恢复painter状态
        painter.restore()
    
    def mousePressEvent(self, event: QGraphicsSceneMouseEvent):
        """处理鼠标按下事件"""
        if event.button() == Qt.LeftButton:
            self._is_dragging = True
            self._drag_start_pos = event.scenePos()
            
            # 如果Ctrl键按下，开始创建连接
            if event.modifiers() & Qt.ControlModifier:
                self.connection_started.emit(self.hardware_id, event.scenePos())
                event.accept()
                return
        
        elif event.button() == Qt.RightButton:
            # 首先确保节点被选中
            if not self.isSelected():
                self.setSelected(True)
                self.node_selected.emit(self.hardware_id)
            
            # 显示右键菜单
            self._show_context_menu(event)
            event.accept()
            return
            
        super().mousePressEvent(event)
        
        # 发出选中信号
        if not self.isSelected():
            self.setSelected(True)
        self.node_selected.emit(self.hardware_id)
    
    def mouseMoveEvent(self, event: QGraphicsSceneMouseEvent):
        """处理鼠标移动事件"""
        super().mouseMoveEvent(event)
        
        # 如果正在拖拽，更新连接线位置
        if self._is_dragging:
            # 更新场景中所有与此节点相关的连接线
            scene = self.scene()
            if scene and hasattr(scene, 'update_connections_for_node'):
                scene.update_connections_for_node(self)
    
    def mouseReleaseEvent(self, event: QGraphicsSceneMouseEvent):
        """处理鼠标释放事件"""
        if event.button() == Qt.LeftButton and self._is_dragging:
            self._is_dragging = False
            
            # 发出节点移动信号
            pos = self.pos()
            self.node_moved.emit(self.hardware_id, pos.x(), pos.y())
        
        super().mouseReleaseEvent(event)
    
    def mouseDoubleClickEvent(self, event: QGraphicsSceneMouseEvent):
        """处理鼠标双击事件"""
        self.node_double_clicked.emit(self.hardware_id)
        super().mouseDoubleClickEvent(event)
    
    def _show_context_menu(self, event: QGraphicsSceneMouseEvent):
        """显示右键上下文菜单"""
        menu = QMenu()
        
        # 添加菜单项
        edit_config_action = menu.addAction("编辑配置 (JSON)")
        connect_action = menu.addAction("创建连接")
        menu.addSeparator()
        delete_action = menu.addAction("删除节点")
        duplicate_action = menu.addAction("复制节点")
        
        # 显示菜单并获取选择
        action = menu.exec_(event.screenPos())
        
        # 处理菜单选择
        if action == edit_config_action:
            # 发出配置编辑请求信号
            self.config_edit_requested.emit(self.hardware_id)
        elif action == connect_action:
            self.connection_started.emit(self.hardware_id, event.scenePos())
        elif action == delete_action:
            # TODO: 实现删除逻辑
            pass
        elif action == duplicate_action:
            # TODO: 实现复制逻辑
            pass
    
    def get_connection_point(self, side: str) -> QPointF:
        """
        获取指定侧的连接点（场景坐标）
        
        Args:
            side: 'top', 'bottom', 'left', 'right'
            
        Returns:
            连接点的场景坐标
        """
        local_point = self.connection_points.get(side, self.connection_points['top'])
        return self.mapToScene(local_point)
    
    def get_nearest_connection_point(self, scene_point: QPointF) -> tuple:
        """
        获取离给定场景点最近的连接点
        
        Args:
            scene_point: 场景坐标点
            
        Returns:
            (side, point): 连接点侧和场景坐标
        """
        min_distance = float('inf')
        nearest_side = 'top'
        nearest_point = None
        
        for side, local_point in self.connection_points.items():
            scene_connection_point = self.mapToScene(local_point)
            distance = (scene_point - scene_connection_point).manhattanLength()
            
            if distance < min_distance:
                min_distance = distance
                nearest_side = side
                nearest_point = scene_connection_point
        
        return nearest_side, nearest_point
    
    def to_dict(self) -> Dict[str, Any]:
        """将节点转换为字典表示（用于JSON序列化）"""
        pos = self.pos()
        rect = self.rect()
        
        return {
            'id': self.hardware_id,
            'name': self.name,
            'type': self.type,
            'position': {
                'x': pos.x(),
                'y': pos.y()
            },
            'size': {
                'width': rect.width(),
                'height': rect.height()
            },
            'properties': self.properties.copy(),
            'appearance': {
                'fill_color': self.fill_color.name(),
                'border_color': self.border_color.name(),
                'text_color': self.text_color.name()
            }
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'HardwareNodeItem':
        """从字典创建节点实例"""
        pos = data.get('position', {'x': 0, 'y': 0})
        size = data.get('size', {'width': 120, 'height': 60})
        
        node = cls(
            hardware_id=data['id'],
            name=data['name'],
            hw_type=data['type'],
            x=pos['x'],
            y=pos['y'],
            width=size['width'],
            height=size['height'],
            properties=data.get('properties', {})
        )
        
        # 恢复外观设置（如果存在）
        appearance = data.get('appearance')
        if appearance:
            node.fill_color = QColor(appearance.get('fill_color', node.fill_color.name()))
            node.border_color = QColor(appearance.get('border_color', node.border_color.name()))
            node.text_color = QColor(appearance.get('text_color', node.text_color.name()))
            
            # 重新设置样式
            node._setup_style()
        
        return node
    
    def __repr__(self):
        return f"HardwareNodeItem(id={self.hardware_id}, name={self.name}, type={self.type}, pos={self.pos()})"