"""
图形基础类演示脚本

此脚本演示如何使用图形基础类创建硬件连接图。
"""

import sys
import os
import json
from datetime import datetime

# 添加项目根目录到Python路径，以便能够正确导入模块
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(os.path.dirname(current_dir)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from PySide6.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QWidget, QPushButton, QHBoxLayout,
    QDialog, QTextEdit, QVBoxLayout, QHBoxLayout, QLabel, QMessageBox,
    QFileDialog, QPlainTextEdit, QDialogButtonBox
)
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QFont, QTextCursor, QColor

from gui.src.graphics.hardware_scene import HardwareScene
from gui.src.graphics.hardware_view import HardwareView


class JsonEditorDialog(QDialog):
    """JSON编辑器对话框"""
    
    def __init__(self, node_data: dict, parent=None):
        super().__init__(parent)
        
        self.node_data = node_data.copy()
        self.original_data = node_data.copy()
        
        self.setWindowTitle(f"编辑节点配置 - {node_data.get('name', '未知节点')}")
        self.setGeometry(200, 200, 800, 600)
        
        # 创建布局
        layout = QVBoxLayout(self)
        
        # 标题
        title_label = QLabel(f"编辑节点: {node_data.get('name', '未知节点')} (ID: {node_data.get('id', '未知')})")
        title_label.setStyleSheet("font-weight: bold; font-size: 14px;")
        layout.addWidget(title_label)
        
        # JSON编辑器
        self.json_edit = QPlainTextEdit()
        self.json_edit.setFont(QFont("Monospace", 10))
        
        # 设置初始JSON内容（格式化）
        json_text = json.dumps(node_data, indent=2, ensure_ascii=False)
        self.json_edit.setPlainText(json_text)
        
        # 语法高亮（简单实现）
        self._setup_syntax_highlighting()
        
        layout.addWidget(self.json_edit)
        
        # 状态标签
        self.status_label = QLabel("就绪")
        self.status_label.setStyleSheet("color: gray;")
        layout.addWidget(self.status_label)
        
        # 按钮
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel | QDialogButtonBox.Reset)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        button_box.button(QDialogButtonBox.Reset).clicked.connect(self.reset_to_original)
        
        layout.addWidget(button_box)
        
        # 定时器用于实时验证JSON
        self.validation_timer = QTimer(self)
        self.validation_timer.timeout.connect(self.validate_json)
        self.validation_timer.start(500)  # 每500ms验证一次
    
    def _setup_syntax_highlighting(self):
        """设置简单的语法高亮"""
        # 这是一个简化的实现，实际项目中可以使用更高级的语法高亮
        pass
    
    def validate_json(self):
        """验证JSON格式"""
        try:
            json_text = self.json_edit.toPlainText()
            parsed = json.loads(json_text)
            self.status_label.setText("✓ JSON格式正确")
            self.status_label.setStyleSheet("color: green;")
            return True
        except json.JSONDecodeError as e:
            self.status_label.setText(f"✗ JSON格式错误: {str(e)}")
            self.status_label.setStyleSheet("color: red;")
            return False
    
    def reset_to_original(self):
        """重置为原始数据"""
        json_text = json.dumps(self.original_data, indent=2, ensure_ascii=False)
        self.json_edit.setPlainText(json_text)
        self.status_label.setText("已重置为原始数据")
        self.status_label.setStyleSheet("color: blue;")
    
    def get_updated_data(self):
        """获取更新后的数据"""
        try:
            json_text = self.json_edit.toPlainText()
            return json.loads(json_text)
        except json.JSONDecodeError:
            return None


class GraphicsDemoWindow(QMainWindow):
    """图形演示窗口"""
    
    def __init__(self):
        super().__init__()
        
        self.setWindowTitle("图形基础类演示 - DiagnosticAssistant")
        self.setGeometry(100, 100, 1200, 800)
        
        # 创建中心部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 创建布局
        main_layout = QVBoxLayout(central_widget)
        
        # 创建工具栏
        toolbar_layout = QHBoxLayout()
        
        # 添加按钮
        self.add_node_btn = QPushButton("添加节点")
        self.add_node_btn.clicked.connect(self.add_sample_node)
        
        self.add_connection_btn = QPushButton("添加连接")
        self.add_connection_btn.clicked.connect(self.add_sample_connection)
        
        self.clear_btn = QPushButton("清空场景")
        self.clear_btn.clicked.connect(self.clear_scene)
        
        self.zoom_fit_btn = QPushButton("适应视图")
        self.zoom_fit_btn.clicked.connect(self.zoom_to_fit)
        
        self.delete_selected_btn = QPushButton("删除选中")
        self.delete_selected_btn.clicked.connect(self.delete_selected_items)
        self.delete_selected_btn.setToolTip("删除选中的节点和连接 (Delete键)")
        
        # 添加导出/导入按钮
        self.export_btn = QPushButton("导出场景")
        self.export_btn.clicked.connect(self.export_scene)
        self.export_btn.setToolTip("导出整个场景为JSON文件")
        
        self.import_btn = QPushButton("导入场景")
        self.import_btn.clicked.connect(self.import_scene)
        self.import_btn.setToolTip("从JSON文件导入场景")
        
        toolbar_layout.addWidget(self.add_node_btn)
        toolbar_layout.addWidget(self.add_connection_btn)
        toolbar_layout.addWidget(self.delete_selected_btn)
        toolbar_layout.addWidget(self.clear_btn)
        toolbar_layout.addWidget(self.zoom_fit_btn)
        toolbar_layout.addWidget(self.export_btn)
        toolbar_layout.addWidget(self.import_btn)
        toolbar_layout.addStretch()
        
        main_layout.addLayout(toolbar_layout)
        
        # 创建场景和视图
        self.scene = HardwareScene()
        self.view = HardwareView(self.scene)
        
        # 连接信号
        self.scene.node_added.connect(self.on_node_added)
        self.scene.connection_added.connect(self.on_connection_added)
        self.scene.selection_changed.connect(self.on_selection_changed)
        self.scene.scene_modified.connect(self.on_scene_modified)
        
        self.view.view_zoomed.connect(self.on_view_zoomed)
        self.view.mouse_position_changed.connect(self.on_mouse_position_changed)
        
        # 添加视图到布局
        main_layout.addWidget(self.view)
        
        # 状态栏
        self.statusBar().showMessage("就绪")
        
        # 添加示例节点
        self.add_initial_nodes()
        
        # 连接节点配置编辑信号
        self._connect_node_signals()
    
    def _connect_node_signals(self):
        """连接节点信号"""
        # 监听所有节点的配置编辑请求
        for node in self.scene.nodes.values():
            node.config_edit_requested.connect(self.on_node_config_edit_requested)
        
        # 监听新添加的节点
        self.scene.node_added.connect(self._on_new_node_added)
    
    def _on_new_node_added(self, node):
        """处理新节点添加"""
        node.config_edit_requested.connect(self.on_node_config_edit_requested)
    
    def on_node_config_edit_requested(self, node_id):
        """处理节点配置编辑请求"""
        node = self.scene.nodes.get(node_id)
        if not node:
            return
        
        # 获取节点数据
        node_data = node.to_dict()
        
        # 创建并显示JSON编辑器对话框
        dialog = JsonEditorDialog(node_data, self)
        
        if dialog.exec() == QDialog.Accepted:
            updated_data = dialog.get_updated_data()
            if updated_data:
                self._update_node_from_dict(node, updated_data)
                self.statusBar().showMessage(f"已更新节点配置: {node.name}")
    
    def _update_node_from_dict(self, node, data):
        """从字典更新节点属性"""
        # 更新基本属性
        if 'name' in data:
            node.name = data['name']
        
        if 'type' in data:
            node.type = data['type']
        
        if 'properties' in data:
            node.properties = data['properties'].copy()
        
        # 更新位置
        if 'position' in data:
            pos = data['position']
            node.setPos(pos.get('x', 0), pos.get('y', 0))
        
        # 更新大小
        if 'size' in data:
            size = data['size']
            node.setRect(0, 0, size.get('width', 120), size.get('height', 60))
        
        # 更新外观
        if 'appearance' in data:
            appearance = data['appearance']
            if 'fill_color' in appearance:
                node.fill_color = QColor(appearance['fill_color'])
            if 'border_color' in appearance:
                node.border_color = QColor(appearance['border_color'])
            if 'text_color' in appearance:
                node.text_color = QColor(appearance['text_color'])
            
            # 重新设置样式
            node._setup_style()
        
        # 更新场景中的连接线
        self.scene.update_connections_for_node(node)
        
        # 强制重绘
        node.update()
    
    def export_scene(self):
        """导出整个场景为JSON文件"""
        # 获取场景数据
        scene_data = self.scene.to_dict()
        
        # 添加导出元数据
        scene_data['export_metadata'] = {
            'exported_at': datetime.now().isoformat(),
            'application': 'DiagnosticAssistant Graphics Demo',
            'version': '1.0'
        }
        
        # 选择保存文件
        file_path, _ = QFileDialog.getSaveFileName(
            self, 
            "导出场景", 
            "", 
            "JSON文件 (*.json);;所有文件 (*)"
        )
        
        if not file_path:
            return
        
        # 确保文件扩展名
        if not file_path.endswith('.json'):
            file_path += '.json'
        
        try:
            # 写入JSON文件（带缩进）
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(scene_data, f, indent=2, ensure_ascii=False)
            
            self.statusBar().showMessage(f"场景已导出到: {file_path}")
            QMessageBox.information(self, "导出成功", f"场景已成功导出到:\n{file_path}")
            
        except Exception as e:
            self.statusBar().showMessage(f"导出失败: {str(e)}")
            QMessageBox.critical(self, "导出失败", f"导出场景时出错:\n{str(e)}")
    
    def import_scene(self):
        """从JSON文件导入场景"""
        # 选择文件
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "导入场景",
            "",
            "JSON文件 (*.json);;所有文件 (*)"
        )
        
        if not file_path:
            return
        
        try:
            # 读取JSON文件
            with open(file_path, 'r', encoding='utf-8') as f:
                scene_data = json.load(f)
            
            # 从字典加载场景
            self.scene.from_dict(scene_data)
            
            # 重新连接节点信号
            self._connect_node_signals()
            
            self.statusBar().showMessage(f"场景已从文件导入: {file_path}")
            QMessageBox.information(self, "导入成功", f"场景已成功从文件导入:\n{file_path}")
            
        except json.JSONDecodeError as e:
            self.statusBar().showMessage(f"JSON解析失败: {str(e)}")
            QMessageBox.critical(self, "导入失败", f"JSON文件格式错误:\n{str(e)}")
        except Exception as e:
            self.statusBar().showMessage(f"导入失败: {str(e)}")
            QMessageBox.critical(self, "导入失败", f"导入场景时出错:\n{str(e)}")
    
    def add_initial_nodes(self):
        """添加初始示例节点"""
        # 添加示例节点（基于实际案例）
        nodes = [
            ("5G WiFi路由器", "wireless_communication", 100, 100),
            ("Debug BOX", "debug_tool", 300, 100),
            ("车辆控制器", "controller", 500, 100),
            ("车辆天线", "antenna", 700, 100),
            ("T1 Ethernet转换器", "converter", 300, 300)
        ]
        
        for name, hw_type, x, y in nodes:
            self.scene.add_node(name, hw_type, x, y)
        
        # 添加示例连接
        connections = [
            ("5G WiFi路由器", "Debug BOX", "ethernet_cable", "网络接入"),
            ("Debug BOX", "车辆控制器", "ethernet_cable", "数据传输"),
            ("车辆控制器", "车辆天线", "can_bus", "控制信号"),
            ("Debug BOX", "T1 Ethernet转换器", "ethernet_cable", "冗余路径"),
            ("T1 Ethernet转换器", "车辆天线", "can_bus", "备用连接")
        ]
        
        # 查找节点并创建连接
        node_map = {node.name: node for node in self.scene.nodes.values()}
        
        for from_name, to_name, conn_type, label in connections:
            from_node = node_map.get(from_name)
            to_node = node_map.get(to_name)
            
            if from_node and to_node:
                self.scene.create_connection(from_node, to_node, conn_type, label)
    
    def add_sample_node(self):
        """添加示例节点"""
        import random
        import sys
        sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
        # 随机选择硬件类型 - 直接从HardwareNodeItem类引用
        from gui.src.graphics.hardware_node import HardwareNodeItem
        hw_types = list(HardwareNodeItem.HARDWARE_TYPES.keys())
        hw_type = random.choice(hw_types)

        # 随机位置
        x = random.randint(50, 700)
        y = random.randint(50, 500)

        # 生成名称
        type_name = HardwareNodeItem.HARDWARE_TYPES[hw_type]["name"]
        node_name = f"示例{type_name}{len(self.scene.nodes) + 1}"

        # 添加节点
        node = self.scene.add_node(node_name, hw_type, x, y)
        
        self.statusBar().showMessage(f"已添加节点: {node_name} ({type_name})")
    
    def add_sample_connection(self):
        """添加示例连接 - 启动交互式连接模式
        
        用户需要：
        1. 点击此按钮进入连接创建模式
        2. 点击源节点（连接起点）
        3. 拖拽到目标节点（连接终点）
        4. 松开鼠标完成连接
        
        也可以通过 Ctrl+左键点击节点直接开始创建连接
        """
        nodes = list(self.scene.nodes.values())
        
        if len(nodes) < 2:
            self.statusBar().showMessage("需要至少2个节点才能创建连接")
            return
        
        # 进入连接创建模式
        self._enter_connection_mode()
    
    def _enter_connection_mode(self):
        """进入连接创建模式"""
        # 设置标志表示等待用户选择源节点
        self._waiting_for_source_node = True
        self._connection_source_node = None
        
        # 更新状态栏提示用户
        self.statusBar().showMessage("请点击源节点开始创建连接，按 Esc 取消")
        
        # 修改光标样式提示用户当前处于连接模式
        self.view.setCursor(Qt.CrossCursor)
        
        # 安装事件过滤器来捕获用户点击
        self.view.viewport().installEventFilter(self)
    
    def eventFilter(self, obj, event):
        """事件过滤器，用于处理连接创建模式下的用户交互"""
        from PySide6.QtCore import QEvent
        from PySide6.QtGui import QMouseEvent
        
        # 处理键盘事件 - Esc取消连接模式
        if event.type() == QEvent.KeyPress:
            if event.key() == Qt.Key_Escape:
                self._cancel_connection_mode()
                return True
        
        # 处理鼠标点击事件
        if event.type() == QEvent.MouseButtonPress and isinstance(event, QMouseEvent):
            if event.button() == Qt.LeftButton:
                # 获取点击位置的场景坐标
                scene_pos = self.view.mapToScene(event.pos())
                
                # 查找点击位置下的节点
                items = self.scene.items(scene_pos)
                clicked_node = None
                for item in items:
                    if hasattr(item, 'hardware_id'):  # 是HardwareNodeItem
                        clicked_node = item
                        break
                
                if self._waiting_for_source_node:
                    # 等待选择源节点
                    if clicked_node:
                        self._connection_source_node = clicked_node
                        self._waiting_for_source_node = False
                        
                        # 启动场景的连接模式（显示临时连接线）
                        self.scene.start_connection_mode(clicked_node)
                        
                        self.statusBar().showMessage(
                            f"已选择源节点: {clicked_node.name}，请拖拽到目标节点，按 Esc 取消"
                        )
                        return True
                    else:
                        self.statusBar().showMessage("请点击一个节点作为连接起点")
                        return True
        
        # 处理鼠标释放事件 - 完成连接
        if event.type() == QEvent.MouseButtonRelease and isinstance(event, QMouseEvent):
            if event.button() == Qt.LeftButton and not self._waiting_for_source_node:
                # 获取释放位置的场景坐标
                scene_pos = self.view.mapToScene(event.pos())
                
                # 查找释放位置下的节点
                items = self.scene.items(scene_pos)
                target_node = None
                for item in items:
                    if hasattr(item, 'hardware_id') and item != self._connection_source_node:
                        target_node = item
                        break
                
                if target_node:
                    # 创建连接（使用默认连接类型，后续可以通过右键菜单修改）
                    from gui.src.graphics.connection_line import ConnectionLineItem
                    conn_type = "ethernet_cable"  # 默认连接类型
                    
                    connection = self.scene.create_connection(
                        self._connection_source_node, 
                        target_node, 
                        conn_type
                    )
                    
                    type_name = ConnectionLineItem.CONNECTION_TYPES[conn_type]["name"]
                    self.statusBar().showMessage(
                        f"已创建连接: {self._connection_source_node.name} -> {target_node.name} ({type_name})"
                    )
                else:
                    self.statusBar().showMessage("未选择有效的目标节点，连接已取消")
                
                # 退出连接模式
                self._exit_connection_mode()
                return True
        
        return super().eventFilter(obj, event)
    
    def _cancel_connection_mode(self):
        """取消连接创建模式"""
        self.scene.cancel_connection_mode()
        self._exit_connection_mode()
        self.statusBar().showMessage("连接创建已取消")
    
    def _exit_connection_mode(self):
        """退出连接创建模式"""
        self._waiting_for_source_node = False
        self._connection_source_node = None
        
        # 恢复光标
        self.view.setCursor(Qt.ArrowCursor)
        
        # 移除事件过滤器
        self.view.viewport().removeEventFilter(self)
    
    def delete_selected_items(self):
        """删除选中的节点和连接
        
        删除逻辑：
        1. 先删除选中的连接
        2. 再删除选中的节点（删除节点时会自动删除相关连接）
        """
        # 获取选中的节点和连接
        selected_nodes = self.scene.get_selected_nodes()
        selected_connections = self.scene.get_selected_connections()
        
        if not selected_nodes and not selected_connections:
            self.statusBar().showMessage("没有选中任何项目")
            return
        
        deleted_nodes = 0
        deleted_connections = 0
        
        # 先删除选中的连接
        for connection in selected_connections:
            self.scene.remove_connection(connection.connection_id)
            deleted_connections += 1
        
        # 再删除选中的节点（删除节点会自动删除相关连接）
        for node in selected_nodes:
            self.scene.remove_node(node.hardware_id)
            deleted_nodes += 1
        
        # 更新状态栏
        message_parts = []
        if deleted_nodes > 0:
            message_parts.append(f"{deleted_nodes}个节点")
        if deleted_connections > 0:
            message_parts.append(f"{deleted_connections}个连接")
        
        self.statusBar().showMessage(f"已删除: {', '.join(message_parts)}")
    
    def delete_selected_nodes(self):
        """仅删除选中的节点（及其相关连接）"""
        selected_nodes = self.scene.get_selected_nodes()
        
        if not selected_nodes:
            self.statusBar().showMessage("没有选中任何节点")
            return
        
        deleted_count = 0
        for node in selected_nodes:
            self.scene.remove_node(node.hardware_id)
            deleted_count += 1
        
        self.statusBar().showMessage(f"已删除 {deleted_count} 个节点")
    
    def delete_selected_connections(self):
        """仅删除选中的连接"""
        selected_connections = self.scene.get_selected_connections()
        
        if not selected_connections:
            self.statusBar().showMessage("没有选中任何连接")
            return
        
        deleted_count = 0
        for connection in selected_connections:
            self.scene.remove_connection(connection.connection_id)
            deleted_count += 1
        
        self.statusBar().showMessage(f"已删除 {deleted_count} 个连接")
    
    def keyPressEvent(self, event):
        """处理键盘按键事件"""
        # Delete 或 Backspace 键删除选中项
        if event.key() in (Qt.Key_Delete, Qt.Key_Backspace):
            self.delete_selected_items()
            event.accept()
            return
        
        super().keyPressEvent(event)
    
    def clear_scene(self):
        """清空场景"""
        self.scene.clear_scene()
        self.statusBar().showMessage("场景已清空")
    
    def zoom_to_fit(self):
        """缩放以适应视图"""
        self.view.zoom_to_fit()
        self.statusBar().showMessage("已缩放以适应视图")
    
    # 信号处理函数
    def on_node_added(self, node):
        """处理节点添加"""
        print(f"节点已添加: {node}")
    
    def on_connection_added(self, connection):
        """处理连接添加"""
        print(f"连接已添加: {connection}")
    
    def on_selection_changed(self, selected_nodes, selected_connections):
        """处理选择变化"""
        node_count = len(selected_nodes)
        conn_count = len(selected_connections)
        
        if node_count > 0 or conn_count > 0:
            self.statusBar().showMessage(
                f"已选择: {node_count}个节点, {conn_count}个连接"
            )
    
    def on_scene_modified(self):
        """处理场景修改"""
        node_count = len(self.scene.nodes)
        conn_count = len(self.scene.connections)
        
        self.setWindowTitle(
            f"图形基础类演示 - DiagnosticAssistant (节点: {node_count}, 连接: {conn_count})"
        )
    
    def on_view_zoomed(self, zoom_level):
        """处理视图缩放"""
        self.statusBar().showMessage(f"缩放比例: {zoom_level:.2f}x")
    
    def on_mouse_position_changed(self, scene_pos):
        """处理鼠标位置变化"""
        # 在状态栏显示鼠标位置
        pos_text = f"鼠标位置: ({scene_pos.x():.1f}, {scene_pos.y():.1f})"
        
        # 检查是否在节点上
        items = self.scene.items(scene_pos)
        for item in items:
            if hasattr(item, 'name'):
                pos_text += f" | 节点: {item.name}"
                break
        
        # 更新状态栏（每10次更新一次以避免闪烁）
        if hasattr(self, '_mouse_update_count'):
            self._mouse_update_count += 1
            if self._mouse_update_count >= 10:
                self.statusBar().showMessage(pos_text)
                self._mouse_update_count = 0
        else:
            self._mouse_update_count = 0
            self.statusBar().showMessage(pos_text)


def main():
    """主函数"""
    app = QApplication(sys.argv)
    
    # 设置应用程序样式
    app.setStyle('Fusion')
    
    # 创建并显示窗口
    window = GraphicsDemoWindow()
    window.show()
    
    # 运行应用程序
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
