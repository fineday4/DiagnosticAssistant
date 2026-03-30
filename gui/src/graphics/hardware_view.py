"""
硬件视图控制类 - 提供图形视图的交互控制

继承自 QGraphicsView，提供：
1. 视图缩放和平移控制
2. 鼠标事件处理
3. 网格和对齐功能
4. 视图状态管理
"""

from PySide6.QtCore import Qt, QPoint, QPointF, QRectF, QTimer
from PySide6.QtCore import Signal as PySide6Signal
from PySide6.QtGui import QWheelEvent, QMouseEvent, QKeyEvent, QPainter, QPen, QBrush, QColor, QCursor
from PySide6.QtWidgets import QGraphicsView, QGraphicsScene, QMenu
# QAction兼容性导入：在PySide6新版本中，QAction从QtWidgets移动到了QtGui
try:
    from PySide6.QtWidgets import QAction
except ImportError:
    from PySide6.QtGui import QAction

from typing import Optional, Tuple

from .hardware_scene import HardwareScene


class HardwareView(QGraphicsView):
    """硬件视图控制类"""
    
    # 信号定义 - 使用重命名的Signal以避免可能的导入冲突
    view_zoomed = PySide6Signal(float)  # 缩放比例
    view_panned = PySide6Signal(QPointF)  # 视图中心点
    mouse_position_changed = PySide6Signal(QPointF)  # 鼠标场景位置
    
    def __init__(self, scene: Optional[HardwareScene] = None, parent=None):
        """初始化硬件视图"""
        super().__init__(parent)
        
        # 视图设置
        self.setRenderHint(QPainter.Antialiasing, True)
        self.setRenderHint(QPainter.TextAntialiasing, True)
        self.setRenderHint(QPainter.SmoothPixmapTransform, True)
        
        # 视图优化
        self.setViewportUpdateMode(QGraphicsView.FullViewportUpdate)
        self.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
        self.setResizeAnchor(QGraphicsView.AnchorViewCenter)
        
        # 交互设置
        self.setDragMode(QGraphicsView.RubberBandDrag)
        self.setInteractive(True)
        
        # 缩放设置
        self.zoom_factor = 1.15
        self.min_zoom = 0.1
        self.max_zoom = 10.0
        self.current_zoom = 1.0
        
        # 网格和对齐设置
        self.grid_enabled = True
        self.snap_to_grid = True
        self.grid_size = 20
        
        # 鼠标状态
        self._pan_mode = False
        self._pan_start_pos = QPoint()
        self._last_mouse_pos = QPoint()
        
        # 定时器用于鼠标位置跟踪
        self._mouse_tracker = QTimer(self)
        self._mouse_tracker.timeout.connect(self._track_mouse_position)
        self._mouse_tracker.start(50)  # 每50ms更新一次
        
        # 设置场景
        if scene:
            self.set_scene(scene)
        
        # 初始化视图
        self._setup_view()
    
    def _setup_view(self):
        """设置视图属性"""
        # 设置背景颜色
        self.setBackgroundBrush(QColor(240, 240, 240))
        
        # 设置视口属性
        self.setOptimizationFlag(QGraphicsView.DontAdjustForAntialiasing, True)
        self.setOptimizationFlag(QGraphicsView.DontSavePainterState, True)
        
        # 设置缓存
        self.setCacheMode(QGraphicsView.CacheBackground)
    
    def set_scene(self, scene: HardwareScene):
        """设置硬件场景"""
        self.setScene(scene)
        
        # 连接场景信号
        if scene:
            scene.scene_modified.connect(self._on_scene_modified)
    
    def wheelEvent(self, event: QWheelEvent):
        """处理鼠标滚轮事件（缩放）"""
        # 计算缩放因子
        delta = event.angleDelta().y()
        
        if delta > 0:
            # 放大
            zoom = self.zoom_factor
        else:
            # 缩小
            zoom = 1.0 / self.zoom_factor
        
        # 应用缩放
        self.zoom(zoom, event.position())
        
        # 接受事件
        event.accept()
    
    def mousePressEvent(self, event: QMouseEvent):
        """处理鼠标按下事件"""
        scene_pos = self.mapToScene(event.pos())
        
        if event.button() == Qt.MiddleButton or (
            event.button() == Qt.LeftButton and event.modifiers() & Qt.AltModifier
        ):
            # 进入平移模式
            self._pan_mode = True
            self._pan_start_pos = event.pos()
            self.setCursor(Qt.ClosedHandCursor)
            event.accept()
            return
        
        elif event.button() == Qt.RightButton:
            # 检查是否点击了场景中的项目
            item = self.itemAt(event.pos())
            if item:
                # 如果点击了项目，让项目处理右键事件
                super().mousePressEvent(event)
                return
            else:
                # 如果点击了空白区域，显示视图的右键菜单
                self._show_context_menu(event)
                event.accept()
                return
        
        super().mousePressEvent(event)
        
        # 更新鼠标位置
        self._last_mouse_pos = event.pos()
    
    def mouseMoveEvent(self, event: QMouseEvent):
        """处理鼠标移动事件"""
        # 处理平移
        if self._pan_mode:
            delta = event.pos() - self._pan_start_pos
            self.horizontalScrollBar().setValue(
                self.horizontalScrollBar().value() - delta.x()
            )
            self.verticalScrollBar().setValue(
                self.verticalScrollBar().value() - delta.y()
            )
            self._pan_start_pos = event.pos()
            event.accept()
            return
        
        super().mouseMoveEvent(event)
        
        # 更新鼠标位置
        self._last_mouse_pos = event.pos()
    
    def mouseReleaseEvent(self, event: QMouseEvent):
        """处理鼠标释放事件"""
        if self._pan_mode and (
            event.button() == Qt.MiddleButton or
            (event.button() == Qt.LeftButton and event.modifiers() & Qt.AltModifier)
        ):
            # 退出平移模式
            self._pan_mode = False
            self.setCursor(Qt.ArrowCursor)
            event.accept()
            return
        
        super().mouseReleaseEvent(event)
    
    def keyPressEvent(self, event: QKeyEvent):
        """处理键盘按下事件"""
        # 缩放快捷键
        if event.key() == Qt.Key_Plus and event.modifiers() & Qt.ControlModifier:
            self.zoom(self.zoom_factor, self.mapFromGlobal(QCursor.pos()))
            event.accept()
            return
        elif event.key() == Qt.Key_Minus and event.modifiers() & Qt.ControlModifier:
            self.zoom(1.0 / self.zoom_factor, self.mapFromGlobal(QCursor.pos()))
            event.accept()
            return
        elif event.key() == Qt.Key_0 and event.modifiers() & Qt.ControlModifier:
            self.reset_zoom()
            event.accept()
            return
        
        # 网格对齐快捷键
        elif event.key() == Qt.Key_G and event.modifiers() & Qt.ControlModifier:
            self.toggle_grid()
            event.accept()
            return
        elif event.key() == Qt.Key_S and event.modifiers() & Qt.ControlModifier:
            self.toggle_snap_to_grid()
            event.accept()
            return
        
        # 视图居中快捷键
        elif event.key() == Qt.Key_C and event.modifiers() & Qt.ControlModifier:
            self.center_on_scene()
            event.accept()
            return
        
        super().keyPressEvent(event)
    
    def zoom(self, factor: float, viewport_pos: Optional[QPointF] = None):
        """缩放视图"""
        # 计算新缩放比例
        new_zoom = self.current_zoom * factor
        
        # 检查缩放限制
        if new_zoom < self.min_zoom or new_zoom > self.max_zoom:
            return
        
        # 应用缩放
        self.scale(factor, factor)
        self.current_zoom = new_zoom
        
        # 发出缩放信号
        self.view_zoomed.emit(self.current_zoom)
    
    def reset_zoom(self):
        """重置缩放比例"""
        self.resetTransform()
        self.current_zoom = 1.0
        self.view_zoomed.emit(self.current_zoom)
    
    def zoom_to_fit(self):
        """缩放以适应所有内容"""
        if not self.scene():
            return
        
        # 获取场景边界
        scene_rect = self.scene().sceneRect()
        if scene_rect.isNull():
            return
        
        # 计算适合的缩放比例
        view_rect = self.viewport().rect()
        x_ratio = view_rect.width() / scene_rect.width()
        y_ratio = view_rect.height() / scene_rect.height()
        fit_ratio = min(x_ratio, y_ratio) * 0.9  # 留10%边距
        
        # 应用缩放
        self.resetTransform()
        self.scale(fit_ratio, fit_ratio)
        self.current_zoom = fit_ratio
        
        # 居中显示
        self.centerOn(scene_rect.center())
        
        # 发出信号
        self.view_zoomed.emit(self.current_zoom)
        self.view_panned.emit(self.mapToScene(self.viewport().rect().center()))
    
    def center_on_scene(self):
        """居中显示场景"""
        if not self.scene():
            return
        
        scene_rect = self.scene().sceneRect()
        if not scene_rect.isNull():
            self.centerOn(scene_rect.center())
            self.view_panned.emit(scene_rect.center())
    
    def toggle_grid(self):
        """切换网格显示"""
        self.grid_enabled = not self.grid_enabled
        
        # 更新场景网格设置
        scene = self.scene()
        if isinstance(scene, HardwareScene):
            scene.grid_enabled = self.grid_enabled
        
        # 强制重绘
        self.viewport().update()
    
    def toggle_snap_to_grid(self):
        """切换网格对齐"""
        self.snap_to_grid = not self.snap_to_grid
    
    def snap_to_grid_point(self, scene_point: QPointF) -> QPointF:
        """将场景点对齐到网格"""
        if not self.snap_to_grid or not self.grid_enabled:
            return scene_point
        
        grid_size = self.grid_size / self.current_zoom  # 考虑缩放
        
        x = round(scene_point.x() / grid_size) * grid_size
        y = round(scene_point.y() / grid_size) * grid_size
        
        return QPointF(x, y)
    
    def get_view_center(self) -> QPointF:
        """获取视图中心点的场景坐标"""
        view_center = self.viewport().rect().center()
        return self.mapToScene(view_center)
    
    def get_visible_rect(self) -> QRectF:
        """获取可见区域的场景矩形"""
        top_left = self.mapToScene(self.viewport().rect().topLeft())
        bottom_right = self.mapToScene(self.viewport().rect().bottomRight())
        return QRectF(top_left, bottom_right)
    
    def _track_mouse_position(self):
        """跟踪鼠标位置"""
        if not self.underMouse():
            return
        
        # 获取鼠标位置
        mouse_pos = self.mapFromGlobal(QCursor.pos())
        scene_pos = self.mapToScene(mouse_pos)
        
        # 发出鼠标位置信号
        self.mouse_position_changed.emit(scene_pos)
    
    def _show_context_menu(self, event: QMouseEvent):
        """显示右键上下文菜单"""
        menu = QMenu(self)
        
        # 添加视图操作
        zoom_fit_action = menu.addAction("缩放以适应")
        reset_zoom_action = menu.addAction("重置缩放")
        menu.addSeparator()
        
        # 添加网格操作
        grid_action = menu.addAction("显示网格")
        grid_action.setCheckable(True)
        grid_action.setChecked(self.grid_enabled)
        
        snap_action = menu.addAction("对齐到网格")
        snap_action.setCheckable(True)
        snap_action.setChecked(self.snap_to_grid)
        
        menu.addSeparator()
        
        # 添加视图操作
        center_action = menu.addAction("居中显示")
        
        # 显示菜单并获取选择
        action = menu.exec_(event.globalPos())
        
        # 处理菜单选择
        if action == zoom_fit_action:
            self.zoom_to_fit()
        elif action == reset_zoom_action:
            self.reset_zoom()
        elif action == grid_action:
            self.toggle_grid()
        elif action == snap_action:
            self.toggle_snap_to_grid()
        elif action == center_action:
            self.center_on_scene()
    
    def _on_scene_modified(self):
        """处理场景修改事件"""
        # 更新视图
        self.viewport().update()
    
    def drawForeground(self, painter: QPainter, rect: QRectF):
        """绘制前景（覆盖层）"""
        super().drawForeground(painter, rect)
        
        # 绘制缩放比例指示器
        if self.current_zoom != 1.0:
            painter.save()
            
            # 设置字体
            font = painter.font()
            font.setPointSize(8)
            painter.setFont(font)
            
            # 设置颜色
            painter.setPen(QPen(QColor(0, 0, 0, 180)))
            painter.setBrush(QBrush(QColor(255, 255, 255, 200)))
            
            # 绘制背景矩形
            text = f"缩放: {self.current_zoom:.2f}x"
            text_rect = painter.boundingRect(QRectF(), Qt.AlignLeft, text)
            text_rect.adjust(-5, -2, 5, 2)
            text_rect.moveTopLeft(rect.topLeft() + QPointF(10, 10))
            
            painter.drawRoundedRect(text_rect, 3, 3)
            
            # 绘制文本
            painter.drawText(text_rect, Qt.AlignCenter, text)
            
            painter.restore()
    
    def __repr__(self):
        return (f"HardwareView(zoom={self.current_zoom:.2f}x, "
                f"grid={'on' if self.grid_enabled else 'off'}, "
                f"snap={'on' if self.snap_to_grid else 'off'})")