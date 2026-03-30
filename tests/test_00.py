import sys
from PySide6.QtWidgets import QApplication, QMainWindow
# 导入由 pyside6-uic 生成的 UI 类
sys.path.append('./')  # 替换为你的UI文件所在目录
from gui.src.test_00 import Ui_Dialog

class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        # 创建一个UI类的实例
        self.ui = Ui_Dialog()
        # 调用 setupUi 方法，将UI设置到当前窗口上
        self.ui.setupUi(self)

        # 现在，你可以通过 self.ui 来访问UI中的任何控件了
        # 例如，如果Designer里有个按钮叫 pushButton
        # self.ui.pushButton.setText("点击我")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())