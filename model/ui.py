import os
from math import sqrt, ceil
from functools import partial
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QFont, QMovie, QColor
from PyQt5.QtWidgets import (QApplication, QHBoxLayout, QGridLayout, QSlider,
                             QLabel, QMainWindow, QSizePolicy, QPushButton,
                             QVBoxLayout, QWidget)
from PIL import Image


COLORS = {
    "WIN_BG":   "#222222",
    "INFO_BG":  "#252526",
    "WATCH_BG": "#000000",
    "COMBO_BG": "#3c3c3c",
    "BORDER":   "#757575",
    "TEXT":     "#cccccc",
    "TAG":      "#888888",
    "SELECT":   "#ADFF2F",
}
FONT = "Roboto"


class UI:

    def setup(self, Picker: QMainWindow, num_subscreen: int = 16) -> None:
        Picker.setWindowTitle("Thumbnail Picker")
        Picker.setGeometry(100, 100, 1200, 800)

        self.createMenuBar(Picker)
        self.createContentLayout(Picker, num_subscreen)
        self.createProgressBarLayout(Picker)

        self.centralLayout = QVBoxLayout()
        self.centralLayout.addWidget(self.contentBlock)
        self.centralLayout.addWidget(self.progressBarWidget)

        self.centralWidget = QWidget()
        self.centralWidget.setLayout(self.centralLayout)
        self.centralWidget.setStyleSheet(
            f"color: {COLORS['TEXT']};"
            "border-width: 0px;"
            "border-style: solid;"
            f"border-color: {COLORS['BORDER']};"
            f"background-color: {COLORS['WIN_BG']};"
        )
        Picker.setCentralWidget(self.centralWidget)

    def createMenuBar(self, Picker: QMainWindow) -> None:
        menuBar = Picker.menuBar()
        fileMenu = menuBar.addMenu("&File")
        fileMenu.setObjectName("FileMenu")
        self.openAction = fileMenu.addAction("&Open...")
        self.openAction.setObjectName("OpenAction")
        self.openAction.triggered.connect(Picker.setProject)

    def createContentLayout(self, Picker: QMainWindow, num_subscreen: int) -> None:
        self.contentBlock = ScreenUI(num_subscreen)

    def createProgressBarLayout(self, Picker: QMainWindow) -> None:
        self.progressBar = QSlider(Qt.Horizontal)
        self.progressBar.setRange(0, 0)
        self.progressBar.setFixedHeight(30)
        self.progressBar.setStyleSheet(
            """
            .QSlider {
                border-radius: 10px;
            }
            .QSlider::groove:horizontal {
                border: 1px solid #262626;
                height: 10px;
                background: #393939;
                margin: 0 12px;
            }
            .QSlider::handle:horizontal {
                background: #3281FF;
                width: 0px;
                height: 0px;
                margin: -6px 0px;
                border-radius:8px;
            }
            .QSlider::sub-page:horizontal{
                background:#52b1ee;
            }
            """
        )

        self.percentageLabel = QLabel("0.00%")
        self.percentageLabel.setFixedSize(45, 30)

        self.nextPageButton = QPushButton("Next")

        self.progressBarLayout = QHBoxLayout()
        self.progressBarLayout.addWidget(self.progressBar)
        self.progressBarLayout.addWidget(self.percentageLabel)
        self.progressBarLayout.addWidget(self.nextPageButton)
        self.progressBarLayout.setSpacing(10)
        self.progressBarWidget = QWidget()
        self.progressBarWidget.setLayout(self.progressBarLayout)
        self.progressBarWidget.setFixedHeight(40)

    def updateContent(self, gifs: list[str]) -> None:
        self.contentBlock.update(gifs)

class ScreenUI(QWidget):

    def __init__(self, num_subscreen: int = 16) -> None:
        super().__init__()
        self.content_layout = QGridLayout()
        self.setLayout(self.content_layout)
        self.num_subscreen = num_subscreen

        H = int(sqrt(num_subscreen))
        W = ceil(num_subscreen / H)
        for i in range(num_subscreen):
            h, w = i // W, i % W
            subscreen = self.getSubScreen(i, "")
            self.content_layout.addWidget(subscreen, h, w)

    def update(self, gif_paths: list[str]) -> None:
        N = len(gif_paths)

        for i in range(self.num_subscreen):
            path = gif_paths[i] if i < N else ""
            widget = self.content_layout.itemAt(i).widget()
            widget.update(path)

        for i in range(self.num_subscreen):
            widget = self.content_layout.itemAt(i).widget()
            widget.start()

    @staticmethod
    def getSubScreen(id: int, name: str) -> QWidget:
        subscreen = SubScreen(id, name)
        # fixed size when loading new frame
        subscreen.setSizePolicy(
            QSizePolicy.Ignored, QSizePolicy.Ignored
        )
        subscreen.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
        return subscreen

    def get_classes(self):
        classes = {}
        for i in range(self.num_subscreen):
            widget = self.content_layout.itemAt(i).widget()
            if os.path.exists(widget.name):
                classes[widget.name] = (widget.get_class())

        return classes


class SubScreen(QWidget):

    def __init__(self, id: int, name: str) -> None:
        super().__init__()
        self.content = QLabel()
        self.content.setStyleSheet(
            f"""
            color: {COLORS['TAG']};
            border-width: 3px;
            """
        )

        self.id = id
        self.name = name
        self.cls = "valid"

        self.button_border = self.get_button("B")
        self.button_sceneCut = self.get_button("C")
        self.button_screenContent = self.get_button("S")

        self.buttons = {
            "border": [self.button_border, "#000000"],
            "sceneCut": [self.button_sceneCut, "#FF0000"],
            "screenContent": [self.button_screenContent, "#00FF00"],
        }

        self.button_border.clicked.connect(partial(self.buttonClick, cls="border"))
        self.button_sceneCut.clicked.connect(partial(self.buttonClick, cls="sceneCut"))
        self.button_screenContent.clicked.connect(partial(self.buttonClick, cls="screenContent"))

        self.button_layout = QHBoxLayout()
        self.button_layout.addWidget(self.button_border)
        self.button_layout.addWidget(self.button_sceneCut)
        self.button_layout.addWidget(self.button_screenContent)

        self.layout = QVBoxLayout()
        self.layout.addWidget(self.content)
        self.layout.addLayout(self.button_layout)
        self.setLayout(self.layout)

    def update(self, name: str) -> None:
        self.name = name
        self.cls = "valid"

        if os.path.exists(name):
            self.movie = QMovie(name)
            self.movie.setSpeed(50) # 50%
            self.movie.setBackgroundColor(QColor(255, 255, 255, 255))
            
            gif_size = Image.open(name)
            self.movie_size = QSize(gif_size.width, gif_size.height)
            self.content.setMovie(self.movie)
            self.adjustSize()
        else:
            self.content.clear()

        for name, (button, color) in self.buttons.items():
            button.setStyleSheet(
                f"""
                border-width: 1px;
                border-color: {COLORS['BORDER']};
                """
            )


    def start(self) -> None:
        if os.path.exists(self.name):
            self.movie.start()

    def buttonClick(self, event, cls: str):
        if not os.path.exists(self.name):
            return

        self.cls = cls if self.cls != cls else "valid"
        for name, (button, color) in self.buttons.items():
            if name != self.cls:
                button.setStyleSheet(
                    f"""
                    border-width: 1px;
                    border-color: {COLORS['BORDER']};
                    """
                )
            else:
                button.setStyleSheet(
                    f"""
                    border-width: 1px;
                    border-color: {COLORS['BORDER']};
                    color: #FFFFFF;
                    background-color: {color};
                    """
                )

    def setAlignment(self, align) -> None:
        self.content.setAlignment(align)

    def setSizePolicy(self, w_policy, h_policy) -> None:
        self.content.setSizePolicy(w_policy, h_policy)

    def resizeEvent(self, event) -> None:
        # size is decided after resizeEvent.
        if os.path.exists(self.name):
            self.adjustSize()

    def adjustSize(self) -> None:
        w, h = self.content.width(), self.content.height()
        mw, mh = self.movie_size.width(), self.movie_size.height()
        factor = min(w / mw, h / mh)

        nw, nh = round(factor * mw), round(factor * mh)
        self.movie.setScaledSize(QSize(nw, nh))

    def get_class(self):
        return self.cls

    @staticmethod
    def get_button(name: str) -> QPushButton:
        button = QPushButton(name)
        button.setFixedSize(35, 35)
        button.setFont(QFont(FONT, 20))
        button.setStyleSheet(
            f"""
            border-width: 1px;
            border-color: {COLORS['BORDER']};
            """
        )

        return button


class FinishMessage(QMainWindow):

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Congratulation !!!")
        self.label = QLabel("You have finished the classification of all the thumbnails !!!")
        self.setCentralWidget(self.label)

    def closeEvent(self, event):
        for window in QApplication.topLevelWidgets():
            window.close()