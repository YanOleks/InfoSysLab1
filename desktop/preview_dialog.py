from PySide6.QtWidgets import QDialog, QVBoxLayout, QPlainTextEdit, QLabel
from PySide6.QtGui import QPixmap, QImage, QFont
from PySide6.QtCore import Qt

class PreviewDialog(QDialog):
    def __init__(self, filename, file_type, content, parent=None):
        super().__init__(parent)
        self.setWindowTitle(filename)
        self.setMinimumSize(600, 400)
        
        layout = QVBoxLayout()
        
        if file_type == "code":
            editor = QPlainTextEdit()
            editor.setReadOnly(True)
            font = QFont("Courier New")
            font.setStyleHint(QFont.Monospace)
            editor.setFont(font)
            # content is string for code
            if isinstance(content, bytes):
                content = content.decode("utf-8")
            editor.setPlainText(content)
            layout.addWidget(editor)
            
        elif file_type == "image":
            label = QLabel()
            label.setAlignment(Qt.AlignCenter)
            # content is bytes for image
            image = QImage.fromData(content)
            pixmap = QPixmap.fromImage(image)
            pixmap_scaled = pixmap.scaled(580, 380, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            label.setPixmap(pixmap_scaled)
            layout.addWidget(label)
            
        self.setLayout(layout)
