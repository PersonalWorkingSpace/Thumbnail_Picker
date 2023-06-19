import os
import sys
from glob import glob
from PyQt5.QtWidgets import QApplication, QFileDialog, QMainWindow
from model.ui import UI, FinishMessage


NUM_SUBSCREEN = 16


class Picker(QMainWindow):

    def __init__(self) -> None:
        super().__init__()
        self.ui = UI()
        self.ui.setup(self, NUM_SUBSCREEN)
        self.message = FinishMessage()
        self.expName = ""
        self.connectEvent()

    def connectEvent(self):
        self.ui.nextPageButton.clicked.connect(self.nextPage)

    def setProject(self) -> None:
        self.expName = self.fileDialog()
        if os.path.exists(self.expName):
            self.gifs = glob(os.path.join(self.expName, "*.gif"))
            self.gifs.sort()
            self.num_gifs = len(self.gifs)

            if self.num_gifs == 0:
                self.expName = ""
                return

            start = os.path.basename(self.gifs[0]).split('.')[0]
            end = os.path.basename(self.gifs[-1]).split('.')[0]
            self.picker_folder = os.path.join(self.expName, f"picker_{start}-{end}")
            os.makedirs(self.picker_folder, exist_ok=True)

            self.setWindowTitle(f"Thumbnail Picker: {self.expName}")
            self.config = os.path.join(self.picker_folder, "progress.cfg")
            if os.path.exists(self.config):
                with open(self.config, "r") as f:
                    try:
                        self.curr_idx = int(f.read())
                    except:
                        self.curr_idx = 0
                        with open(self.config, "w") as f:
                            f.write(str(self.curr_idx))
            else:
                self.curr_idx = 0
                with open(self.config, "w") as f:
                    f.write(str(self.curr_idx))

            self.updateProgressRange()
            self.updateProgress()
            self.updateContentBlock()

    def fileDialog(self) -> str:  # pragma: no cover
        options = QFileDialog.Options()
        options |= QFileDialog.ShowDirsOnly
        options |= QFileDialog.DontResolveSymlinks
        fileName = QFileDialog.getExistingDirectory(
            self, "Open Directory", "",
            options=options
        )
        return fileName

    def updateProgressRange(self):
        self.ui.progressBar.setRange(0, self.num_gifs)
        self.ui.progressBar.setValue(1)

    def updateProgress(self):
        self.ui.progressBar.setValue(1 + self.curr_idx)
        percentage = min(100, self.curr_idx / self.num_gifs * 100)
        self.ui.percentageLabel.setText(f"{percentage:.2f}%")
        if percentage == 100:
            self.showFinishMessage()

    def updateContentBlock(self) -> None:
        self.ui.updateContent(self.gifs[self.curr_idx:self.curr_idx+NUM_SUBSCREEN])
        self.curr_idx += NUM_SUBSCREEN

    def nextPage(self) -> None:
        if not os.path.exists(self.expName):
            return

        with open(self.config, "w") as f:
            f.write(str(self.curr_idx))

        classes = self.ui.contentBlock.get_classes()

        valid = open(os.path.join(self.picker_folder, "valid.out"), "a")
        border = open(os.path.join(self.picker_folder, "border.out"), "a")
        sceneCut = open(os.path.join(self.picker_folder, "sceneCut.out"), "a")
        screenContent = open(os.path.join(self.picker_folder, "screenContent.out"), "a")

        for name, c in classes.items():
            name = os.path.basename(name + "\n")
            if c == "border":
                border.write(name)
            elif c == "sceneCut":
                sceneCut.write(name)
            elif c == "screenContent":
                screenContent.write(name)
            else:
                valid.write(name)

        valid.close()
        border.close()
        sceneCut.close()
        screenContent.close()

        self.updateProgress()

        if self.curr_idx >= self.num_gifs:
            self.showFinishMessage()
        else:
            self.updateContentBlock()

    def showFinishMessage(self):
        self.hide()
        self.message.show()


if __name__ == "__main__":  # pragma: no cover
    app = QApplication(sys.argv)
    win = Picker()
    win.show()
    sys.exit(app.exec())
