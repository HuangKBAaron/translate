#!/usr/bin/python
# -*- coding: utf8 -*-
#
# WordForge Translation Editor
# Copyright 2006 WordForge Foundation
#
# Version 0.1 (31 August 2006)
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#
# Developed by:
#       Hok Kakada (hokkakada@khmeros.info)
#       Keo Sophon (keosophon@khmeros.info)
#       Seth Chanratha (sethchanratha@khmeros.info)
#       San Titvirak (titvirak@khmeros.info)
#
# This module is working on any comments of current TU.

from PyQt4 import QtCore, QtGui
import sys
from ui.Ui_Comment import Ui_frmComment
import modules.World as World
from translate.storage import po
from translate.storage import xliff

class CommentDock(QtGui.QDockWidget):
    """
    Code for Comment View
    
    @signal commentChanged(): emitted when Comment view's document is modified.
    @signal readyForSave(True): emitted when Comment view's text is changed.
    @signal copyAvailable(bool): emitted when text is selected or de-selected in the Comment view.
    """
    
    def __init__(self, parent):
        QtGui.QDockWidget.__init__(self, parent)
        self.setObjectName("commentDock")
        self.setWindowTitle(self.tr("Comment"))
        self.form = QtGui.QWidget(self)
        self.ui = Ui_frmComment()
        self.ui.setupUi(self.form)
        self.setWidget(self.form)
        self.layout = QtGui.QTextLayout()
        self.ui.txtLocationComment.hide()
        self.ui.txtTranslatorComment.setWhatsThis("Translator Comment\n\nThis is where translator can leave comments for other translators or for reviewers.")
        self.ui.txtLocationComment.setWhatsThis("Location Comment\n\nThis noneditable comment contains information about where the message is found in the souce code. It will be appeared once there is comments only. You can hide the comment editor by deactivating Views - Show Comment.")
        self.applySettings()

        self.connect(self.ui.txtTranslatorComment, QtCore.SIGNAL("textChanged()"), self.emitReadyForSave)
        
        # create highlight font
        self.highlightFormat = QtGui.QTextCharFormat()
        self.highlightFormat.setFontWeight(QtGui.QFont.Bold)
        self.highlightFormat.setForeground(QtCore.Qt.white)
        self.highlightFormat.setBackground(QtCore.Qt.darkMagenta)
        self.highlightRange = QtGui.QTextLayout.FormatRange()
        self.highlightRange.format = self.highlightFormat

    def closeEvent(self, event):
        """
        set text of action object to 'show Comment' before closing Comment View
        @param QCloseEvent Object: received close event when closing widget
        """        
        QtGui.QDockWidget.closeEvent(self, event)
        self.toggleViewAction().setChecked(False)

    def updateView(self, currentUnit):
        """ update comments 
        @param currentUnit: new unit that just emit"""
        self.ui.txtTranslatorComment.setEnabled(bool(currentUnit))
        if (not currentUnit):
            self.ui.txtLocationComment.hide()
            self.ui.txtTranslatorComment.setPlainText("")
            return
        translatorComment = ""
        locationComment = ""
        if isinstance(currentUnit, po.pounit):
            translatorComment = currentUnit.getnotes("translator")
            locationComment = comments = "".join([comment[3:] for comment in currentUnit.sourcecomments])
            if (locationComment == ""):
                self.ui.txtLocationComment.hide()
            else:
                self.ui.txtLocationComment.show()
                self.ui.txtLocationComment.setPlainText(unicode(locationComment))
        elif isinstance(currentUnit, xliff.xliffunit):
            translatorComment = currentUnit.getnotes()
            self.ui.txtLocationComment.hide()
        else:
            translatorComment = ""
            self.ui.txtLocationComment.hide()
        self.ui.txtTranslatorComment.setPlainText(unicode(translatorComment))

    def checkModified(self):
        if self.ui.txtTranslatorComment.document().isModified():
            self.emit(QtCore.SIGNAL("commentChanged"), self.ui.txtTranslatorComment.toPlainText())

    def highlightSearch(self, textField, position, length = 0):
        """Highlight the text at specified position, length, and textField.
        @param textField: source or target text box.
        @param position: highlight start point.
        @param length: highlight length."""
        if (textField != World.comment or position == None):
            if (not getattr(self, "highlightBlock", None)):
                return
            self.highlightRange.length = 0
        else:
            textField = self.ui.txtTranslatorComment
            self.highlightBlock = textField.document().findBlock(position)
            self.highlightRange.start = position - self.highlightBlock.position()
            self.highlightRange.length = length
        self.highlightBlock.layout().setAdditionalFormats([self.highlightRange])
        self.highlightBlock.document().markContentsDirty(self.highlightBlock.position(), self.highlightBlock.length())

    def emitReadyForSave(self):
        self.emit(QtCore.SIGNAL("readyForSave"), True)

    def applySettings(self):
        """ set color and font to txtTranslatorComment"""
        commentColor = World.settings.value("commentColor")
        if (commentColor.isValid()):
            colorObj = QtGui.QColor(commentColor.toString())
            palette = self.ui.txtTranslatorComment.palette()
            palette.setColor(QtGui.QPalette.Active,QtGui.QPalette.ColorRole(QtGui.QPalette.Text), colorObj)
            self.ui.txtTranslatorComment.setPalette(palette)
            
        font = World.settings.value("commentFont")
        if (font.isValid()):
            fontObj = QtGui.QFont()
            if (fontObj.fromString(font.toString())):
                self.ui.txtTranslatorComment.setFont(fontObj)
                
    def replaceText(self, textField, position, length, replacedText):
        """replace the string (at position and length) with replacedText in txtTarget.
        @param textField: source or target text box.
        @param position: old string's start point.
        @param length: old string's length.
        @param replacedText: string to replace."""
        if (textField != World.comment):
            return
        text = self.ui.txtTranslatorComment.toPlainText()
        text.replace(position, length, replacedText);
        self.ui.txtTranslatorComment.setPlainText(text)
        self.ui.txtTranslatorComment.document().setModified()
        self.checkModified()
    
if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    comment = CommentDock(None)
    comment.show()
    sys.exit(app.exec_())
