# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'pytalic2_preferences.ui'
#
# Created by: PyQt4 UI code generator 4.11.4
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

try:
    _encoding = QtGui.QApplication.UnicodeUTF8
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig)

class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName(_fromUtf8("Dialog"))
        Dialog.setWindowModality(QtCore.Qt.ApplicationModal)
        Dialog.resize(379, 346)
        self.buttonBox = QtGui.QDialogButtonBox(Dialog)
        self.buttonBox.setGeometry(QtCore.QRect(80, 310, 291, 32))
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.metrics_group_box = QtGui.QGroupBox(Dialog)
        self.metrics_group_box.setGeometry(QtCore.QRect(190, 10, 181, 271))
        self.metrics_group_box.setObjectName(_fromUtf8("metrics_group_box"))
        self.verticalLayout = QtGui.QVBoxLayout(self.metrics_group_box)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.label = QtGui.QLabel(self.metrics_group_box)
        self.label.setObjectName(_fromUtf8("label"))
        self.verticalLayout.addWidget(self.label)
        self.horizontalLayout_18 = QtGui.QHBoxLayout()
        self.horizontalLayout_18.setObjectName(_fromUtf8("horizontalLayout_18"))
        self.label_3 = QtGui.QLabel(self.metrics_group_box)
        self.label_3.setObjectName(_fromUtf8("label_3"))
        self.horizontalLayout_18.addWidget(self.label_3)
        self.base_height_spin_2 = QtGui.QDoubleSpinBox(self.metrics_group_box)
        self.base_height_spin_2.setWrapping(True)
        self.base_height_spin_2.setFrame(True)
        self.base_height_spin_2.setButtonSymbols(QtGui.QAbstractSpinBox.UpDownArrows)
        self.base_height_spin_2.setDecimals(1)
        self.base_height_spin_2.setMinimum(1.0)
        self.base_height_spin_2.setMaximum(10.0)
        self.base_height_spin_2.setSingleStep(0.5)
        self.base_height_spin_2.setObjectName(_fromUtf8("base_height_spin_2"))
        self.horizontalLayout_18.addWidget(self.base_height_spin_2)
        self.verticalLayout.addLayout(self.horizontalLayout_18)
        self.horizontalLayout_19 = QtGui.QHBoxLayout()
        self.horizontalLayout_19.setObjectName(_fromUtf8("horizontalLayout_19"))
        self.label_4 = QtGui.QLabel(self.metrics_group_box)
        self.label_4.setObjectName(_fromUtf8("label_4"))
        self.horizontalLayout_19.addWidget(self.label_4)
        self.cap_height_spin = QtGui.QDoubleSpinBox(self.metrics_group_box)
        self.cap_height_spin.setWrapping(True)
        self.cap_height_spin.setDecimals(1)
        self.cap_height_spin.setMinimum(0.5)
        self.cap_height_spin.setMaximum(10.0)
        self.cap_height_spin.setSingleStep(0.5)
        self.cap_height_spin.setProperty("value", 2.0)
        self.cap_height_spin.setObjectName(_fromUtf8("cap_height_spin"))
        self.horizontalLayout_19.addWidget(self.cap_height_spin)
        self.verticalLayout.addLayout(self.horizontalLayout_19)
        self.horizontalLayout_20 = QtGui.QHBoxLayout()
        self.horizontalLayout_20.setObjectName(_fromUtf8("horizontalLayout_20"))
        self.label_5 = QtGui.QLabel(self.metrics_group_box)
        self.label_5.setObjectName(_fromUtf8("label_5"))
        self.horizontalLayout_20.addWidget(self.label_5)
        self.ascent_height_spin = QtGui.QDoubleSpinBox(self.metrics_group_box)
        self.ascent_height_spin.setWrapping(True)
        self.ascent_height_spin.setDecimals(1)
        self.ascent_height_spin.setMinimum(1.0)
        self.ascent_height_spin.setMaximum(10.0)
        self.ascent_height_spin.setSingleStep(0.5)
        self.ascent_height_spin.setObjectName(_fromUtf8("ascent_height_spin"))
        self.horizontalLayout_20.addWidget(self.ascent_height_spin)
        self.verticalLayout.addLayout(self.horizontalLayout_20)
        self.horizontalLayout_21 = QtGui.QHBoxLayout()
        self.horizontalLayout_21.setObjectName(_fromUtf8("horizontalLayout_21"))
        self.label_6 = QtGui.QLabel(self.metrics_group_box)
        self.label_6.setObjectName(_fromUtf8("label_6"))
        self.horizontalLayout_21.addWidget(self.label_6)
        self.descent_height_spin = QtGui.QDoubleSpinBox(self.metrics_group_box)
        self.descent_height_spin.setWrapping(True)
        self.descent_height_spin.setDecimals(1)
        self.descent_height_spin.setMinimum(1.0)
        self.descent_height_spin.setMaximum(10.0)
        self.descent_height_spin.setSingleStep(0.5)
        self.descent_height_spin.setObjectName(_fromUtf8("descent_height_spin"))
        self.horizontalLayout_21.addWidget(self.descent_height_spin)
        self.verticalLayout.addLayout(self.horizontalLayout_21)
        self.horizontalLayout_22 = QtGui.QHBoxLayout()
        self.horizontalLayout_22.setObjectName(_fromUtf8("horizontalLayout_22"))
        self.label_7 = QtGui.QLabel(self.metrics_group_box)
        self.label_7.setObjectName(_fromUtf8("label_7"))
        self.horizontalLayout_22.addWidget(self.label_7)
        self.angle_spin = QtGui.QSpinBox(self.metrics_group_box)
        self.angle_spin.setWrapping(True)
        self.angle_spin.setMaximum(45)
        self.angle_spin.setObjectName(_fromUtf8("angle_spin"))
        self.horizontalLayout_22.addWidget(self.angle_spin)
        self.verticalLayout.addLayout(self.horizontalLayout_22)
        self.horizontalLayout_23 = QtGui.QHBoxLayout()
        self.horizontalLayout_23.setObjectName(_fromUtf8("horizontalLayout_23"))
        self.label_8 = QtGui.QLabel(self.metrics_group_box)
        self.label_8.setObjectName(_fromUtf8("label_8"))
        self.horizontalLayout_23.addWidget(self.label_8)
        self.gap_height_spin = QtGui.QDoubleSpinBox(self.metrics_group_box)
        self.gap_height_spin.setWrapping(True)
        self.gap_height_spin.setDecimals(1)
        self.gap_height_spin.setMinimum(0.5)
        self.gap_height_spin.setMaximum(4.0)
        self.gap_height_spin.setSingleStep(0.5)
        self.gap_height_spin.setProperty("value", 1.0)
        self.gap_height_spin.setObjectName(_fromUtf8("gap_height_spin"))
        self.horizontalLayout_23.addWidget(self.gap_height_spin)
        self.verticalLayout.addLayout(self.horizontalLayout_23)
        self.horizontalLayout_24 = QtGui.QHBoxLayout()
        self.horizontalLayout_24.setObjectName(_fromUtf8("horizontalLayout_24"))
        self.label_9 = QtGui.QLabel(self.metrics_group_box)
        self.label_9.setObjectName(_fromUtf8("label_9"))
        self.horizontalLayout_24.addWidget(self.label_9)
        self.nominal_width_spin = QtGui.QDoubleSpinBox(self.metrics_group_box)
        self.nominal_width_spin.setWrapping(True)
        self.nominal_width_spin.setDecimals(1)
        self.nominal_width_spin.setMinimum(1.0)
        self.nominal_width_spin.setMaximum(10.0)
        self.nominal_width_spin.setSingleStep(0.5)
        self.nominal_width_spin.setProperty("value", 4.0)
        self.nominal_width_spin.setObjectName(_fromUtf8("nominal_width_spin"))
        self.horizontalLayout_24.addWidget(self.nominal_width_spin)
        self.verticalLayout.addLayout(self.horizontalLayout_24)
        self.horizontalLayout_25 = QtGui.QHBoxLayout()
        self.horizontalLayout_25.setObjectName(_fromUtf8("horizontalLayout_25"))
        self.label_10 = QtGui.QLabel(self.metrics_group_box)
        self.label_10.setObjectName(_fromUtf8("label_10"))
        self.horizontalLayout_25.addWidget(self.label_10)
        self.char_set_left_space_spin = QtGui.QDoubleSpinBox(self.metrics_group_box)
        self.char_set_left_space_spin.setDecimals(1)
        self.char_set_left_space_spin.setMaximum(3.0)
        self.char_set_left_space_spin.setSingleStep(0.1)
        self.char_set_left_space_spin.setProperty("value", 1.0)
        self.char_set_left_space_spin.setObjectName(_fromUtf8("char_set_left_space_spin"))
        self.horizontalLayout_25.addWidget(self.char_set_left_space_spin)
        self.verticalLayout.addLayout(self.horizontalLayout_25)
        self.horizontalLayout_26 = QtGui.QHBoxLayout()
        self.horizontalLayout_26.setObjectName(_fromUtf8("horizontalLayout_26"))
        self.label_11 = QtGui.QLabel(self.metrics_group_box)
        self.label_11.setObjectName(_fromUtf8("label_11"))
        self.horizontalLayout_26.addWidget(self.label_11)
        self.char_set_right_space_spin = QtGui.QDoubleSpinBox(self.metrics_group_box)
        self.char_set_right_space_spin.setDecimals(1)
        self.char_set_right_space_spin.setMaximum(3.0)
        self.char_set_right_space_spin.setSingleStep(0.1)
        self.char_set_right_space_spin.setProperty("value", 1.0)
        self.char_set_right_space_spin.setObjectName(_fromUtf8("char_set_right_space_spin"))
        self.horizontalLayout_26.addWidget(self.char_set_right_space_spin)
        self.verticalLayout.addLayout(self.horizontalLayout_26)
        self.color_group_box = QtGui.QGroupBox(Dialog)
        self.color_group_box.setGeometry(QtCore.QRect(5, 10, 181, 158))
        self.color_group_box.setObjectName(_fromUtf8("color_group_box"))
        self.verticalLayout_2 = QtGui.QVBoxLayout(self.color_group_box)
        self.verticalLayout_2.setObjectName(_fromUtf8("verticalLayout_2"))
        self.horizontalLayout_28 = QtGui.QHBoxLayout()
        self.horizontalLayout_28.setObjectName(_fromUtf8("horizontalLayout_28"))
        self.label_13 = QtGui.QLabel(self.color_group_box)
        self.label_13.setObjectName(_fromUtf8("label_13"))
        self.horizontalLayout_28.addWidget(self.label_13)
        self.guides_color_button = SelectColorButton(self.color_group_box)
        self.guides_color_button.setAutoFillBackground(False)
        self.guides_color_button.setText(_fromUtf8(""))
        self.guides_color_button.setObjectName(_fromUtf8("guides_color_button"))
        self.horizontalLayout_28.addWidget(self.guides_color_button)
        self.verticalLayout_2.addLayout(self.horizontalLayout_28)
        self.horizontalLayout_29 = QtGui.QHBoxLayout()
        self.horizontalLayout_29.setObjectName(_fromUtf8("horizontalLayout_29"))
        self.label_14 = QtGui.QLabel(self.color_group_box)
        self.label_14.setObjectName(_fromUtf8("label_14"))
        self.horizontalLayout_29.addWidget(self.label_14)
        self.stroke_color_button = SelectColorButton(self.color_group_box)
        self.stroke_color_button.setAutoFillBackground(False)
        self.stroke_color_button.setText(_fromUtf8(""))
        self.stroke_color_button.setObjectName(_fromUtf8("stroke_color_button"))
        self.horizontalLayout_29.addWidget(self.stroke_color_button)
        self.verticalLayout_2.addLayout(self.horizontalLayout_29)
        self.horizontalLayout_30 = QtGui.QHBoxLayout()
        self.horizontalLayout_30.setObjectName(_fromUtf8("horizontalLayout_30"))
        self.label_15 = QtGui.QLabel(self.color_group_box)
        self.label_15.setObjectName(_fromUtf8("label_15"))
        self.horizontalLayout_30.addWidget(self.label_15)
        self.special_color_stroke_button = SelectColorButton(self.color_group_box)
        self.special_color_stroke_button.setAutoFillBackground(False)
        self.special_color_stroke_button.setText(_fromUtf8(""))
        self.special_color_stroke_button.setObjectName(_fromUtf8("special_color_stroke_button"))
        self.horizontalLayout_30.addWidget(self.special_color_stroke_button)
        self.verticalLayout_2.addLayout(self.horizontalLayout_30)
        self.horizontalLayout_27 = QtGui.QHBoxLayout()
        self.horizontalLayout_27.setObjectName(_fromUtf8("horizontalLayout_27"))
        self.label_12 = QtGui.QLabel(self.color_group_box)
        self.label_12.setObjectName(_fromUtf8("label_12"))
        self.horizontalLayout_27.addWidget(self.label_12)
        self.glyph_color_button = SelectColorButton(self.color_group_box)
        self.glyph_color_button.setAutoFillBackground(False)
        self.glyph_color_button.setText(_fromUtf8(""))
        self.glyph_color_button.setObjectName(_fromUtf8("glyph_color_button"))
        self.horizontalLayout_27.addWidget(self.glyph_color_button)
        self.verticalLayout_2.addLayout(self.horizontalLayout_27)

        self.retranslateUi(Dialog)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), Dialog.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), Dialog.reject)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        Dialog.setWindowTitle(_translate("Dialog", "Preferences", None))
        self.metrics_group_box.setTitle(_translate("Dialog", "Metrics", None))
        self.label.setText(_translate("Dialog", "Note: All units are nib-widths.", None))
        self.label_3.setText(_translate("Dialog", "X-height", None))
        self.label_4.setText(_translate("Dialog", "Capital height", None))
        self.label_5.setText(_translate("Dialog", "Ascent height", None))
        self.label_6.setText(_translate("Dialog", "Descent height", None))
        self.label_7.setText(_translate("Dialog", "Guide angle", None))
        self.label_8.setText(_translate("Dialog", "Gap distance", None))
        self.label_9.setText(_translate("Dialog", "Nominal width", None))
        self.label_10.setText(_translate("Dialog", "Left spacing", None))
        self.label_11.setText(_translate("Dialog", "Right spacing", None))
        self.color_group_box.setTitle(_translate("Dialog", "Colors", None))
        self.label_13.setText(_translate("Dialog", "Guidelines", None))
        self.label_14.setText(_translate("Dialog", "Main stroke", None))
        self.label_15.setText(_translate("Dialog", "Drawing stroke", None))
        self.label_12.setText(_translate("Dialog", "Glyph", None))

from view.widgets_qt import SelectColorButton
