"""
连接线图形项 - 表示硬件节点之间的连接关系

继承自 QGraphicsPathItem，提供：
1. 贝塞尔曲线连接线
2. 箭头表示方向
3. 多种线型和样式
4. 智能路径计算
"""

from PySide6.QtCore import Qt, QPointF, QRectF, QObject
from PySide6.QtCore import Signal as PySide6Signal
from PySide6.QtGui import QPainter, QPen, QBrush, QColor, QPainterPath, QPolygonF, QPainterPathStroker
from PySide6.QtWidgets import QGraphicsPathItem, QGraphicsItem, QMenu, QGraphicsSceneMouseEvent

from typing import Dict, Any, Optional, Tuple, TYPE_CHECKING

if TYPE_CHECKING:
    from .hardware_node import HardwareNodeItem


class ConnectionLineItem(QGraphicsPathItem, QObject):
    """连接线图形项，表示硬件节点之间的连接"""
    
    # 信号定义 - 使用重命名的Signal以避免可能的导入冲突
    connection_selected = PySide6Signal(str)  # 连接ID
    connection_double_clicked = PySide6Signal(str)  # 连接ID
    
    # 连接类型定义（基于PROJECT_PLAN.md）
    CONNECTION_TYPES = {
        "ethernet_cable": {
            "name": "网线连接",
            "description": "以太网电缆连接，用于数据传输",
            "line_style": Qt.SolidLine,
            "color": "#2196F3",
            "width": 2,
            "has_arrow": True
        },
        "can_bus": {
            "name": "CAN总线",
            "description": "控制器局域网连接，用于车辆控制信号",
            "line_style": Qt.SolidLine,
            "color": "#9C27B0",
            "width": 2,
            "has_arrow": False
        },
        "power_cable": {
            "name": "电源线",
            "description": "电力供应连接",
            "line_style": Qt.SolidLine,
            "color": "#F44336",
            "width": 3,
            "has_arrow": True
        },
        "usb_cable": {
            "name": "USB连接",
            "description": "通用串行总线连接，用于调试和数据传输",
            "line_style": Qt.DashLine,
            "color": "#FF9800",
            "width": 2,
            "has_arrow": True
        },
        "serial_cable": {
            "name": "串口线",
            "description": "串行通信连接，用于调试和配置",
            "line_style": Qt.DotLine,
            "color": "#795548",
            "width": 1,
            "has_arrow": True
        },
        "wireless": {
            "name": "无线连接",
            "description": "无线通信连接",
            "line_style": Qt.DashLine,
            "color": "#00BCD4",
            "width": 1,
            "has_arrow": True
        }
    }
    
    def __init__(self, connection_id: str, 
                 source_node: 'HardwareNodeItem', 
                 target_node: 'HardwareNodeItem',
                 conn_type: str = "ethernet_cable",
                 label: str = "",
                 properties: Optional[Dict[str, Any]] = None):
        """
        初始化连接线
        
        Args:
            connection_id: 连接线唯一标识符
            source_node: 源节点
            target_node: 目标节点
            conn_type: 连接类型（必须是CONNECTION_TYPES中的键）
            label: 连接标签
            properties: 附加属性字典
        """
        # 调用两个父类的__init__方法
        QGraphicsPathItem.__init__(self)
        QObject.__init__(self)
        
        self.connection_id = connection_id
        self.source_node = source_node
        self.target_node = target_node
        self.type = conn_type
        self.label = label
        self.properties = properties or {}
        
        # 设置标志
        self.setFlag(QGraphicsItem.ItemIsSelectable, True)
        self.setFlag(QGraphicsItem.ItemSendsScenePositionChanges, True)
        
        # 设置Z值确保连接线在节点下方
        self.setZValue(5)
        
        # 样式配置
        self._setup_style()
        
        # 计算初始路径
        self.update_path()
        
        # 连接节点移动信号
        self.source_node.node_moved.connect(self._on_node_moved)
        self.target_node.node_moved.connect(self._on_node_moved)
    
    def _setup_style(self):
        """设置连接线样式"""
        # 获取类型对应的配置
        type_config = self.CONNECTION_TYPES.get(self.type, {})
        
        # 基础样式
        self.line_color = QColor(type_config.get('color', '#607D8B'))
        self.line_width = type_config.get('width', 2)
        self.line_style = type_config.get('line_style', Qt.SolidLine)
        self.has_arrow = type_config.get('has_arrow', True)
        
        # 选中状态样式
        self.selected_color = QColor('#FF5722')
        self.selected_width = self.line_width + 1
        
        # 设置画笔
        self.normal_pen = QPen(self.line_color, self.line_width)
        self.normal_pen.setStyle(self.line_style)
        
        self.selected_pen = QPen(self.selected_color, self.selected_width)
        self.selected_pen.setStyle(self.line_style)
        
        # 箭头样式
        self.arrow_size = 10
        self.arrow_color = self.line_color.darker(120)
        self.selected_arrow_color = self.selected_color
        
    def paint(self, painter: QPainter, option, widget=None):
        """自定义绘制连接线"""
        # 保存painter状态
        painter.save()
        
        # 设置抗锯齿
        painter.setRenderHint(QPainter.Antialiasing)
        
        # 根据选中状态选择样式
        if self.isSelected():
            painter.setPen(self.selected_pen)
            arrow_color = self.selected_arrow_color
        else:
            painter.setPen(self.normal_pen)
            arrow_color = self.arrow_color
        
        # 绘制路径
        painter.drawPath(self.path())
        
        # 绘制箭头（如果有）
        if self.has_arrow:
            self._draw_arrow(painter, arrow_color)
        
        # 绘制标签（如果有）
        if self.label:
            self._draw_label(painter)
        
        # 恢复painter状态
        painter.restore()
    
    def _draw_arrow(self, painter: QPainter, color: QColor):
        """在连接线末端绘制箭头"""
        # 获取路径的最后一段
        path = self.path()
        element_count = path.elementCount()
        
        if element_count < 2:
            return
        
        # 获取最后两个元素（控制点和终点）
        elements = []
        for i in range(element_count):
            element = path.elementAt(i)
            elements.append((element.type, QPointF(element.x, element.y)))
        
        # 计算箭头方向
        if len(elements) >= 2:
            # 获取最后一段的终点和方向点
            if elements[-1][0] == 3:  # CurveToData元素
                end_point = elements[-2][1]
                control_point = elements[-3][1] if len(elements) >= 3 else elements[-2][1]
            else:
                end_point = elements[-1][1]
                control_point = elements[-2][1]
            
            # 计算方向向量
            direction = end_point - control_point
            if direction.manhattanLength() == 0:
                return
            
            # 归一化方向向量
            direction_length = (direction.x() ** 2 + direction.y() ** 2) ** 0.5
            direction = direction / direction_length
            
            # 计算箭头点
            arrow_tip = end_point
            arrow_left = QPointF(
                arrow_tip.x() - direction.x() * self.arrow_size + direction.y() * self.arrow_size / 2,
                arrow_tip.y() - direction.y() * self.arrow_size - direction.x() * self.arrow_size / 2
            )
            arrow_right = QPointF(
                arrow_tip.x() - direction.x() * self.arrow_size - direction.y() * self.arrow_size / 2,
                arrow_tip.y() - direction.y() * self.arrow_size + direction.x() * self.arrow_size / 2
            )
            
            # 绘制箭头
            painter.setBrush(QBrush(color))
            painter.setPen(Qt.NoPen)
            
            arrow_polygon = QPolygonF([arrow_tip, arrow_left, arrow_right])
            painter.drawPolygon(arrow_polygon)
    
    def _draw_label(self, painter: QPainter):
        """在连接线中间绘制标签"""
        # 获取路径的中点
        path = self.path()
        point_at_percent = path.pointAtPercent(0.5)
        
        if point_at_percent.isNull():
            return
        
        # 设置标签样式
        font = painter.font()
        font.setPointSize(8)
        painter.setFont(font)
        
        # 计算文本边界
        text_rect = painter.boundingRect(QRectF(), Qt.AlignCenter, self.label)
        text_rect.moveCenter(point_at_percent)
        
        # 绘制背景矩形
        bg_rect = text_rect.adjusted(-2, -2, 2, 2)
        painter.setBrush(QBrush(QColor(255, 255, 255, 200)))
        painter.setPen(QPen(QColor(0, 0, 0, 100), 1))
        painter.drawRoundedRect(bg_rect, 3, 3)
        
        # 绘制文本
        painter.setPen(QPen(QColor(0, 0, 0)))
        painter.drawText(text_rect, Qt.AlignCenter, self.label)
    
    def update_path(self):
        """更新连接线路径（基于节点位置）"""
        # 获取节点的连接点
        source_side, source_point = self.source_node.get_nearest_connection_point(
            self.target_node.pos()
        )
        target_side, target_point = self.target_node.get_nearest_connection_point(
            self.source_node.pos()
        )
        
        # 创建贝塞尔曲线路径
        path = QPainterPath()
        path.moveTo(source_point)
        
        # 计算控制点（创建平滑曲线）
        dx = abs(target_point.x() - source_point.x())
        dy = abs(target_point.y() - source_point.y())
        
        # 根据相对位置调整控制点
        if dx > dy:  # 水平方向为主
            ctrl1 = QPointF(
                source_point.x() + dx * 0.5,
                source_point.y()
            )
            ctrl2 = QPointF(
                target_point.x() - dx * 0.5,
                target_point.y()
            )
        else:  # 垂直方向为主
            ctrl1 = QPointF(
                source_point.x(),
                source_point.y() + dy * 0.5
            )
            ctrl2 = QPointF(
                target_point.x(),
                target_point.y() - dy * 0.5
            )
        
        # 绘制三次贝塞尔曲线
        path.cubicTo(ctrl1, ctrl2, target_point)
        
        self.setPath(path)
    
    def _on_node_moved(self, node_id: str, x: float, y: float):
        """处理节点移动事件"""
        self.update_path()
    
    def mousePressEvent(self, event: QGraphicsSceneMouseEvent):
        """处理鼠标按下事件"""
        if event.button() == Qt.LeftButton:
            # 选中连接线
            if not self.isSelected():
                self.setSelected(True)
            self.connection_selected.emit(self.connection_id)
        
        elif event.button() == Qt.RightButton:
            # 显示右键菜单
            self._show_context_menu(event)
            event.accept()
            return
            
        super().mousePressEvent(event)
    
    def mouseDoubleClickEvent(self, event: QGraphicsSceneMouseEvent):
        """处理鼠标双击事件"""
        self.connection_double_clicked.emit(self.connection_id)
        super().mouseDoubleClickEvent(event)
    
    def _show_context_menu(self, event: QGraphicsSceneMouseEvent):
        """显示右键上下文菜单"""
        menu = QMenu()
        
        # 添加菜单项
        edit_action = menu.addAction("编辑属性")
        menu.addSeparator()
        delete_action = menu.addAction("删除连接")
        
        # 显示菜单并获取选择
        action = menu.exec_(event.screenPos())
        
        # 处理菜单选择
        if action == edit_action:
            # TODO: 实现属性编辑
            pass
        elif action == delete_action:
            # TODO: 实现删除逻辑
            pass
    
    def boundingRect(self) -> QRectF:
        """返回连接线的边界矩形（包含箭头）"""
        rect = super().boundingRect()
        
        # 扩大边界以包含箭头和标签
        padding = self.arrow_size + 5
        return rect.adjusted(-padding, -padding, padding, padding)
    
    def shape(self) -> QPainterPath:
        """返回连接线的形状（用于命中测试）"""
        # 创建比实际线宽更宽的路径以便于选择
        stroked_path = QPainterPath()
        pen_width = max(self.line_width, 6)  # 最小6像素宽以便选择
        
        # 对路径进行描边
        stroker = QPainterPathStroker()
        stroker.setWidth(pen_width)
        stroker.setCapStyle(Qt.RoundCap)
        stroker.setJoinStyle(Qt.RoundJoin)
        
        return stroker.createStroke(self.path())
    
    def to_dict(self) -> Dict[str, Any]:
        """将连接线转换为字典表示（用于JSON序列化）"""
        type_config = self.CONNECTION_TYPES.get(self.type, {})
        
        # 处理PenStyle枚举，确保可以序列化为JSON
        line_style_value = self.line_style
        if hasattr(line_style_value, 'value'):
            line_style_value = line_style_value.value
        elif not isinstance(line_style_value, (int, str)):
            # 如果既不是整数也不是字符串，尝试转换为整数
            try:
                line_style_value = int(line_style_value)
            except (TypeError, ValueError):
                line_style_value = 1  # 默认SolidLine
        
        return {
            'id': self.connection_id,
            'from': self.source_node.hardware_id,
            'to': self.target_node.hardware_id,
            'type': self.type,
            'label': self.label,
            'properties': self.properties.copy(),
            'appearance': {
                'line_color': self.line_color.name(),
                'line_width': self.line_width,
                'line_style': line_style_value,
                'has_arrow': self.has_arrow
            },
            'metadata': {
                'type_name': type_config.get('name', self.type),
                'description': type_config.get('description', '')
            }
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any], 
                  node_map: Dict[str, 'HardwareNodeItem']) -> 'ConnectionLineItem':
        """从字典创建连接线实例"""
        source_node = node_map.get(data['from'])
        target_node = node_map.get(data['to'])
        
        if not source_node or not target_node:
            raise ValueError(f"无法找到节点: {data['from']} -> {data['to']}")
        
        connection = cls(
            connection_id=data['id'],
            source_node=source_node,
            target_node=target_node,
            conn_type=data['type'],
            label=data.get('label', ''),
            properties=data.get('properties', {})
        )
        
        # 恢复外观设置（如果存在）
        appearance = data.get('appearance')
        if appearance:
            connection.line_color = QColor(appearance.get('line_color', connection.line_color.name()))
            connection.line_width = appearance.get('line_width', connection.line_width)
            
            # 处理线型恢复
            line_style_value = appearance.get('line_style', 1)  # 默认SolidLine
            if isinstance(line_style_value, int):
                connection.line_style = Qt.PenStyle(line_style_value)
            elif hasattr(line_style_value, 'value'):
                connection.line_style = Qt.PenStyle(line_style_value.value)
            else:
                # 尝试转换为整数
                try:
                    connection.line_style = Qt.PenStyle(int(line_style_value))
                except (TypeError, ValueError):
                    connection.line_style = Qt.SolidLine  # 默认值
            
            connection.has_arrow = appearance.get('has_arrow', connection.has_arrow)
            
            # 重新设置样式
            connection._setup_style()
        
        return connection
    
    def __repr__(self):
        return (f"ConnectionLineItem(id={self.connection_id}, "
                f"from={self.source_node.hardware_id}, to={self.target_node.hardware_id}, "
                f"type={self.type})")