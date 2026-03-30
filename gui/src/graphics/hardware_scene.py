"""
硬件场景管理类 - 管理所有硬件节点和连接线

继承自 QGraphicsScene，提供：
1. 节点和连接的生命周期管理
2. 连接创建逻辑
3. 选择和多选功能
4. 场景状态管理
"""

from datetime import datetime
from PySide6.QtCore import Qt, QPointF, QRectF, QLineF, QObject
from PySide6.QtCore import Signal as PySide6Signal
from PySide6.QtGui import QPainter, QPen, QBrush, QColor, QPainterPath, QPainterPathStroker
from PySide6.QtWidgets import QGraphicsScene, QGraphicsSceneMouseEvent, QGraphicsItem

from typing import Dict, Any, Optional, List, Tuple

from .hardware_node import HardwareNodeItem
from .connection_line import ConnectionLineItem


class HardwareScene(QGraphicsScene):
    """硬件场景管理类"""
    
    # 信号定义 - 使用重命名的Signal以避免可能的导入冲突
    # 使用QObject而不是具体类型，避免类型注册问题
    node_added = PySide6Signal(QObject)  # 传递HardwareNodeItem（QObject子类）
    node_removed = PySide6Signal(str)  # 节点ID
    connection_added = PySide6Signal(QObject)  # 传递ConnectionLineItem（QObject子类）
    connection_removed = PySide6Signal(str)  # 连接ID
    selection_changed = PySide6Signal(list, list)  # 选中节点列表, 选中连接列表
    scene_modified = PySide6Signal()  # 场景内容修改
    
    def __init__(self, parent=None):
        """初始化硬件场景"""
        super().__init__(parent)
        
        # 场景设置
        self.setSceneRect(0, 0, 2000, 2000)
        
        # 数据存储
        self.nodes: Dict[str, HardwareNodeItem] = {}
        self.connections: Dict[str, ConnectionLineItem] = {}
        
        # 连接创建状态
        self._connection_mode = False
        self._connection_source_node: Optional[HardwareNodeItem] = None
        self._connection_temp_line: Optional[QGraphicsItem] = None
        self._connection_start_point: Optional[QPointF] = None
        
        # 选择状态
        self._selection_rect: Optional[QGraphicsItem] = None
        self._selection_start_point: Optional[QPointF] = None
        
        # 网格设置
        self.grid_enabled = True
        self.grid_size = 20
        self.grid_color = QColor(200, 200, 200, 50)
        
        # 场景背景
        self.background_color = QColor(245, 245, 245)
        
        # 连接计数器（用于生成唯一ID）
        self._connection_counter = 0
        self._node_counter = 0
        
        # 设置场景属性
        self._setup_scene()
    
    def _setup_scene(self):
        """设置场景属性"""
        # 连接信号
        self.selectionChanged.connect(self._on_selection_changed)
    
    def drawBackground(self, painter: QPainter, rect: QRectF):
        """绘制场景背景（包括网格）"""
        # 绘制背景颜色
        painter.fillRect(rect, self.background_color)
        
        # 绘制网格
        if self.grid_enabled:
            painter.setPen(QPen(self.grid_color, 1, Qt.DotLine))
            
            # 计算网格线起始位置
            left = int(rect.left()) - (int(rect.left()) % self.grid_size)
            top = int(rect.top()) - (int(rect.top()) % self.grid_size)
            
            # 绘制垂直线
            x = left
            while x < rect.right():
                painter.drawLine(x, rect.top(), x, rect.bottom())
                x += self.grid_size
            
            # 绘制水平线
            y = top
            while y < rect.bottom():
                painter.drawLine(rect.left(), y, rect.right(), y)
                y += self.grid_size
    
    def mousePressEvent(self, event: QGraphicsSceneMouseEvent):
        """处理鼠标按下事件"""
        scene_pos = event.scenePos()
        
        if event.button() == Qt.LeftButton:
            # 检查是否点击了空白区域
            item = self.itemAt(scene_pos, self.views()[0].transform())
            
            if not item:
                # 开始框选
                self._start_selection_rect(scene_pos)
                event.accept()
                return
            
            # 检查是否在连接模式下点击了节点
            if self._connection_mode and isinstance(item, HardwareNodeItem):
                self._handle_connection_click(item, scene_pos)
                event.accept()
                return
        
        super().mousePressEvent(event)
    
    def mouseMoveEvent(self, event: QGraphicsSceneMouseEvent):
        """处理鼠标移动事件"""
        scene_pos = event.scenePos()
        
        # 更新临时连接线
        if self._connection_temp_line and self._connection_start_point:
            self._update_temp_connection_line(scene_pos)
        
        # 更新选择矩形
        if self._selection_rect and self._selection_start_point:
            self._update_selection_rect(scene_pos)
        
        super().mouseMoveEvent(event)
    
    def mouseReleaseEvent(self, event: QGraphicsSceneMouseEvent):
        """处理鼠标释放事件"""
        if event.button() == Qt.LeftButton:
            # 结束连接创建
            if self._connection_temp_line:
                self._finish_connection_creation(event.scenePos())
            
            # 结束框选
            if self._selection_rect:
                self._finish_selection()
        
        super().mouseReleaseEvent(event)
    
    def _start_selection_rect(self, start_point: QPointF):
        """开始框选操作"""
        self._selection_start_point = start_point
        self._selection_rect = self.addRect(
            QRectF(start_point, start_point),
            QPen(QColor(100, 100, 255, 150), 1, Qt.DashLine),
            QBrush(QColor(200, 200, 255, 50))
        )
        self._selection_rect.setZValue(1000)  # 确保在最上层
    
    def _update_selection_rect(self, current_point: QPointF):
        """更新选择矩形"""
        if self._selection_rect and self._selection_start_point:
            rect = QRectF(self._selection_start_point, current_point).normalized()
            self._selection_rect.setRect(rect)
    
    def _finish_selection(self):
        """结束框选操作"""
        if self._selection_rect:
            # 获取矩形内的所有项
            selected_items = self.items(self._selection_rect.rect())
            
            # 清除现有选择
            self.clearSelection()
            
            # 选择矩形内的项
            for item in selected_items:
                if isinstance(item, (HardwareNodeItem, ConnectionLineItem)):
                    item.setSelected(True)
            
            # 移除选择矩形
            self.removeItem(self._selection_rect)
            self._selection_rect = None
            self._selection_start_point = None
    
    def start_connection_mode(self, source_node: HardwareNodeItem):
        """开始连接创建模式"""
        self._connection_mode = True
        self._connection_source_node = source_node
        self._connection_start_point = source_node.get_nearest_connection_point(
            self.views()[0].mapToScene(self.views()[0].mapFromGlobal(QPointF()))
        )[1]
        
        # 创建临时连接线
        self._connection_temp_line = self.addLine(
            QLineF(self._connection_start_point, self._connection_start_point),
            QPen(QColor(100, 100, 255), 2, Qt.DashLine)
        )
        self._connection_temp_line.setZValue(1000)
    
    def _handle_connection_click(self, target_node: HardwareNodeItem, click_pos: QPointF):
        """处理连接模式下的节点点击"""
        if not self._connection_source_node or self._connection_source_node == target_node:
            return
        
        # 创建连接
        self.create_connection(self._connection_source_node, target_node)
        
        # 结束连接模式
        self.cancel_connection_mode()
    
    def _update_temp_connection_line(self, current_point: QPointF):
        """更新临时连接线"""
        if self._connection_temp_line and self._connection_start_point:
            # 更新临时线
            line = QLineF(self._connection_start_point, current_point)
            self._connection_temp_line.setLine(line)
    
    def _finish_connection_creation(self, end_point: QPointF):
        """结束连接创建"""
        # 查找最近的节点作为目标
        items = self.items(end_point)
        target_node = None
        
        for item in items:
            if isinstance(item, HardwareNodeItem) and item != self._connection_source_node:
                target_node = item
                break
        
        if target_node and self._connection_source_node:
            # 创建连接
            self.create_connection(self._connection_source_node, target_node)
        
        # 清理临时资源
        self.cancel_connection_mode()
    
    def cancel_connection_mode(self):
        """取消连接创建模式"""
        self._connection_mode = False
        
        if self._connection_temp_line:
            self.removeItem(self._connection_temp_line)
            self._connection_temp_line = None
        
        self._connection_source_node = None
        self._connection_start_point = None
    
    def create_connection(self, source_node: HardwareNodeItem, 
                         target_node: HardwareNodeItem,
                         conn_type: str = "ethernet_cable",
                         label: str = "") -> ConnectionLineItem:
        """创建两个节点之间的连接"""
        # 生成唯一连接ID
        self._connection_counter += 1
        connection_id = f"conn_{self._connection_counter}"
        
        # 创建连接线
        connection = ConnectionLineItem(
            connection_id=connection_id,
            source_node=source_node,
            target_node=target_node,
            conn_type=conn_type,
            label=label
        )
        
        # 添加到场景和数据存储
        self.addItem(connection)
        self.connections[connection_id] = connection
        
        # 连接信号
        connection.connection_selected.connect(self._on_connection_selected)
        connection.connection_double_clicked.connect(self._on_connection_double_clicked)
        
        # 发出信号
        self.connection_added.emit(connection)
        self.scene_modified.emit()
        
        return connection
    
    def add_node(self, name: str, hw_type: str, 
                x: float = 0, y: float = 0,
                properties: Optional[Dict[str, Any]] = None) -> HardwareNodeItem:
        """添加硬件节点到场景"""
        # 生成唯一节点ID
        self._node_counter += 1
        node_id = f"node_{self._node_counter}"
        
        # 创建节点
        node = HardwareNodeItem(
            hardware_id=node_id,
            name=name,
            hw_type=hw_type,
            x=x,
            y=y,
            properties=properties
        )
        
        # 添加到场景和数据存储
        self.addItem(node)
        self.nodes[node_id] = node
        
        # 连接信号
        node.node_moved.connect(self._on_node_moved)
        node.node_selected.connect(self._on_node_selected)
        node.node_double_clicked.connect(self._on_node_double_clicked)
        node.connection_started.connect(self._on_node_connection_started)
        
        # 发出信号
        self.node_added.emit(node)
        self.scene_modified.emit()
        
        return node
    
    def remove_node(self, node_id: str):
        """移除节点及其所有连接"""
        node = self.nodes.get(node_id)
        if not node:
            return
        
        # 移除所有与此节点相关的连接
        connections_to_remove = []
        for conn_id, connection in self.connections.items():
            if (connection.source_node == node or 
                connection.target_node == node):
                connections_to_remove.append(conn_id)
        
        for conn_id in connections_to_remove:
            self.remove_connection(conn_id)
        
        # 移除节点
        self.removeItem(node)
        del self.nodes[node_id]
        
        # 发出信号
        self.node_removed.emit(node_id)
        self.scene_modified.emit()
    
    def remove_connection(self, connection_id: str):
        """移除连接"""
        connection = self.connections.get(connection_id)
        if not connection:
            return
        
        # 移除连接
        self.removeItem(connection)
        del self.connections[connection_id]
        
        # 发出信号
        self.connection_removed.emit(connection_id)
        self.scene_modified.emit()
    
    def update_connections_for_node(self, node: HardwareNodeItem):
        """更新与指定节点相关的所有连接线"""
        for connection in self.connections.values():
            if (connection.source_node == node or 
                connection.target_node == node):
                connection.update_path()
    
    def clear_scene(self):
        """清空场景"""
        # 清除所有项
        self.clear()
        
        # 重置数据存储
        self.nodes.clear()
        self.connections.clear()
        
        # 重置计数器
        self._node_counter = 0
        self._connection_counter = 0
        
        # 发出信号
        self.scene_modified.emit()
    
    def get_selected_nodes(self) -> List[HardwareNodeItem]:
        """获取所有选中的节点"""
        return [item for item in self.selectedItems() 
                if isinstance(item, HardwareNodeItem)]
    
    def get_selected_connections(self) -> List[ConnectionLineItem]:
        """获取所有选中的连接"""
        return [item for item in self.selectedItems() 
                if isinstance(item, ConnectionLineItem)]
    
    def to_dict(self) -> Dict[str, Any]:
        """将场景转换为字典表示（用于JSON序列化）"""
        nodes_data = [node.to_dict() for node in self.nodes.values()]
        connections_data = [conn.to_dict() for conn in self.connections.values()]
        
        return {
            'metadata': {
                'node_count': len(nodes_data),
                'connection_count': len(connections_data),
                'created_at': datetime.now().isoformat()
            },
            'nodes': nodes_data,
            'connections': connections_data,
            'scene_settings': {
                'grid_enabled': self.grid_enabled,
                'grid_size': self.grid_size,
                'background_color': self.background_color.name()
            }
        }
    
    def from_dict(self, data: Dict[str, Any]):
        """从字典加载场景"""
        # 清空当前场景
        self.clear_scene()
        
        # 创建节点
        node_map = {}
        for node_data in data.get('nodes', []):
            node = HardwareNodeItem.from_dict(node_data)
            self.addItem(node)
            self.nodes[node.hardware_id] = node
            node_map[node.hardware_id] = node
            
            # 连接信号
            node.node_moved.connect(self._on_node_moved)
            node.node_selected.connect(self._on_node_selected)
            node.node_double_clicked.connect(self._on_node_double_clicked)
            node.connection_started.connect(self._on_node_connection_started)
        
        # 创建连接
        for conn_data in data.get('connections', []):
            try:
                connection = ConnectionLineItem.from_dict(conn_data, node_map)
                self.addItem(connection)
                self.connections[connection.connection_id] = connection
                
                # 连接信号
                connection.connection_selected.connect(self._on_connection_selected)
                connection.connection_double_clicked.connect(self._on_connection_double_clicked)
            except ValueError as e:
                print(f"警告: 无法创建连接: {e}")
        
        # 更新计数器
        self._node_counter = len(self.nodes)
        self._connection_counter = len(self.connections)
        
        # 应用场景设置
        scene_settings = data.get('scene_settings', {})
        self.grid_enabled = scene_settings.get('grid_enabled', True)
        self.grid_size = scene_settings.get('grid_size', 20)
        
        bg_color = scene_settings.get('background_color')
        if bg_color:
            self.background_color = QColor(bg_color)
        
        # 发出信号
        self.scene_modified.emit()
    
    # 信号处理函数
    def _on_node_moved(self, node_id: str, x: float, y: float):
        """处理节点移动"""
        self.scene_modified.emit()
    
    def _on_node_selected(self, node_id: str):
        """处理节点选中"""
        pass  # 选择变化通过selectionChanged信号处理
    
    def _on_node_double_clicked(self, node_id: str):
        """处理节点双击"""
        # TODO: 打开节点属性编辑器
        pass
    
    def _on_node_connection_started(self, node_id: str, start_point: QPointF):
        """处理节点连接开始"""
        node = self.nodes.get(node_id)
        if node:
            self.start_connection_mode(node)
    
    def _on_connection_selected(self, connection_id: str):
        """处理连接选中"""
        pass  # 选择变化通过selectionChanged信号处理
    
    def _on_connection_double_clicked(self, connection_id: str):
        """处理连接双击"""
        # TODO: 打开连接属性编辑器
        pass
    
    def _on_selection_changed(self):
        """处理选择变化"""
        selected_nodes = self.get_selected_nodes()
        selected_connections = self.get_selected_connections()
        
        self.selection_changed.emit(selected_nodes, selected_connections)
    
    def __repr__(self):
        return (f"HardwareScene(nodes={len(self.nodes)}, "
                f"connections={len(self.connections)})")