from PySide6 import QtCore, QtGui, QtWidgets
from PySide6.QtGui import QTextOption, QFont, QTextCursor, QTextDocument

class HTMLDelegate(QtWidgets.QStyledItemDelegate):
    def paint(self, painter, option, index):
        self.initStyleOption(option,index)

        painter.save()

        # See https://stackoverflow.com/questions/23802170/word-wrap-with-html-qtableview-and-delegates
        # and
        # https://stackoverflow.com/questions/35397943/how-to-make-a-fast-qtableview-with-html-formatted-and-clickable-cells
        doc = QtGui.QTextDocument()

        # word wrap
        #textOption = doc.defaultTextOption()
        #textOption.setWrapMode(QTextOption.WordWrap)
        #doc.setDefaultTextOption(textOption)
        #doc.setTextWidth(option.rect.width())

        doc.setHtml(option.text)

        option.text = ""
        option.widget.style().drawControl(QtWidgets.QStyle.CE_ItemViewItem, option, painter)

        painter.translate(option.rect.left(), option.rect.top())

        clip = QtCore.QRectF(0, 0, option.rect.width(), option.rect.height())
        doc.drawContents(painter, clip)

        painter.restore()


    def sizeHint(self, option, index):
        self.initStyleOption(option,index)
        doc = QtGui.QTextDocument()
        doc.setHtml(option.text)
        #doc.setTextWidth(option.rect.width())
        return QtCore.QSize(doc.idealWidth(), doc.size().height())


    def elideRichText(self, richText: str, maxWidth: int, font: QFont):
        doc = QTextDocument()
        doc.setDocumentMargin(0)
        doc.setHtml(richText)
        doc.adjustSize()
    
        if (doc.size().width() > maxWidth):
            # Elide text
            cursor = QTextCursor(doc)
            cursor.movePosition(QTextCursor.End)
    
            elidedPostfix = "..."
            metric = QFontMetrics(font)
            postfixWidth: int = metric.horizontalAdvance(elidedPostfix)
            while (doc.size().width() > maxWidth - postfixWidth):
                   cursor.deletePreviousChar()
                   doc.adjustSize()
    
            cursor.insertText(elidedPostfix)
    
            return doc.toHtml()
    
        return richText




