from PySide6.QtCore import QObject, QEvent, Qt
from PySide6.QtWidgets import QLineEdit, QTextEdit, QMenu, QScrollBar, QComboBox

class CustomContextMenuFilter(QObject):
    def eventFilter(self, obj, event):
        is_context_menu = (event.type() == QEvent.Type.ContextMenu) or \
                         (isinstance(obj, QTextEdit) and \
                          event.type() == QEvent.Type.MouseButtonPress and \
                          event.button() == Qt.RightButton)
            
        if is_context_menu and (isinstance(obj, QLineEdit) or isinstance(obj, QTextEdit)):
            menu = QMenu(obj)
            menu.setStyleSheet("""
                QMenu {
                    background-color: white;
                    border: 1px solid #dee2e6;
                    border-radius: 4px;
                    padding: 5px;
                }
                QMenu::item {
                    padding: 8px 20px;
                    color: #495057;
                }
                QMenu::item:selected {
                    background-color: #e9ecef;
                    color: #000;
                }
                QMenu::separator {
                    height: 1px;
                    background: #dee2e6;
                    margin: 5px 0px;
                }
            """)
            if isinstance(obj, QLineEdit):
                is_password = obj.echoMode() == QLineEdit.Password
                has_text = len(obj.text()) > 0
                has_selection = obj.hasSelectedText()
                is_read_only = obj.isReadOnly()
                can_undo = obj.isUndoAvailable()
                can_redo = obj.isRedoAvailable()
            elif isinstance(obj, QTextEdit):  # QTextEdit
                is_password = False
                has_text = len(obj.toPlainText()) > 0
                has_selection = bool(obj.textCursor().selectedText())
                is_read_only = obj.isReadOnly()
                can_undo = obj.document().isUndoAvailable()
                can_redo = obj.document().isRedoAvailable()
            elif isinstance(obj, QScrollBar):
                # 스크롤바 컨텍스트 메뉴 추가
                # menu = QMenu(obj)


                # 스크롤 위치 관련 메뉴
                scroll_to_top = menu.addAction("맨 위로")
                scroll_to_top.triggered.connect(lambda: obj.setValue(obj.minimum()))
                
                scroll_to_bottom = menu.addAction("맨 아래로")
                scroll_to_bottom.triggered.connect(lambda: obj.setValue(obj.maximum()))
                
                menu.addSeparator()
                
                # 페이지 단위 스크롤
                page_up = menu.addAction("페이지 위로")
                page_up.triggered.connect(lambda: obj.setValue(obj.value() - obj.pageStep()))
                
                page_down = menu.addAction("페이지 아래로")
                page_down.triggered.connect(lambda: obj.setValue(obj.value() + obj.pageStep()))
                
                menu.addSeparator()
                
                # 스크롤 업/다운
                scroll_up = menu.addAction("스크롤 위로")
                scroll_up.triggered.connect(lambda: obj.setValue(obj.value() - obj.singleStep()))
                
                scroll_down = menu.addAction("스크롤 아래로")
                scroll_down.triggered.connect(lambda: obj.setValue(obj.value() + obj.singleStep()))
                
                menu.exec_(event.globalPos())
                return True
            else:
                return False
            
            # Undo/Redo
            if can_undo:
                action = menu.addAction("실행 취소\tCtrl+Z")
                action.triggered.connect(obj.undo)
            if can_redo:
                action = menu.addAction("다시 실행\tCtrl+Y")
                action.triggered.connect(obj.redo)
            
            if menu.actions() and (has_selection or not is_read_only):
                menu.addSeparator()
            
            # Cut/Copy/Paste
            if has_selection and not is_password:
                if not is_read_only:
                    action = menu.addAction("잘라내기\tCtrl+X")
                    action.triggered.connect(obj.cut)
                action = menu.addAction("복사\tCtrl+C")
                action.triggered.connect(obj.copy)
            
            if not is_read_only:
                action = menu.addAction("붙여넣기\tCtrl+V")
                action.triggered.connect(obj.paste)
            
            if has_selection and not is_password:
                if not is_read_only:
                    menu.addSeparator()
                    action = menu.addAction("삭제")
                    if isinstance(obj, QLineEdit):
                        action.triggered.connect(lambda: obj.del_())
                    else:
                        action.triggered.connect(lambda: obj.textCursor().removeSelectedText())
            
            if has_text and not is_password:
                if menu.actions():
                    menu.addSeparator()
                action = menu.addAction("전체 선택\tCtrl+A")
                action.triggered.connect(obj.selectAll)
            
            if menu.actions():
                menu.exec_(event.globalPos())
            return True
            
        return super().eventFilter(obj, event) 