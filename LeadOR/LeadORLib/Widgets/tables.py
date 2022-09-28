import qt

class ComboDelegate(qt.QItemDelegate):
  def __init__(self, parent, comboItems):
    qt.QItemDelegate.__init__(self, parent)
    self.comboItems = comboItems

  def createEditor(self, parent, option, index):
    combo = qt.QComboBox(parent)
    combo.addItems(self.comboItems)
    return combo

  def setEditorData(self, editor, index):
    editor.blockSignals(True)
    editor.setCurrentText(index.model().data(index))
    editor.blockSignals(False)

  def setModelData(self, editor, model, index):
    name = editor.currentText
    model.setData(index, name, qt.Qt.DisplayRole)


class customStandardItemModel(qt.QStandardItemModel):
  def __init__(self , *args, **kwargs):
    self.columnNames = kwargs["columnNames"]
    self.updateFcn = kwargs["updateFcn"]
    del kwargs["columnNames"]
    del kwargs["updateFcn"]
    super().__init__(*args, **kwargs)

  def flags(self, index):
    baseFlags = qt.Qt.ItemIsEnabled | qt.Qt.ItemIsSelectable
    if index.column() == self.columnNames.index("Visible"):
      return baseFlags | qt.Qt.ItemIsUserCheckable
    elif index.column() == self.columnNames.index("Name"):
      return baseFlags
    else:
      return baseFlags | qt.Qt.ItemIsEditable

  def setData(self , *args, **kwargs):
    qt.QStandardItemModel.setData(self , *args, **kwargs)
    self.updateFcn()

  def headerData(self,section,orientation,role):
    if section == 2:
      if orientation == qt.Qt.Horizontal and role == qt.Qt.DecorationRole:
        return qt.QIcon(':Icons/Small/SlicerVisibleInvisible.png')
    elif orientation == qt.Qt.Horizontal and role == qt.Qt.DisplayRole:
      return self.columnNames[section]
    qt.QStandardItemModel.headerData(self,section,orientation,role)

class FeaturesTable:

  RowHeight = 25

  def __init__(self, view, updateParameterNodeFromGUIFunction):

    self.columnNames = ["Name", "MapTo", "Visible"]
    self.model = customStandardItemModel(0, len(self.columnNames), columnNames=self.columnNames, updateFcn=updateParameterNodeFromGUIFunction)

    self.view = view
    self.view.setVisible(0)
    self.view.verticalHeader().setMaximumSectionSize(self.RowHeight)
    self.view.verticalHeader().setMinimumSectionSize(self.RowHeight)
    self.view.verticalHeader().setDefaultSectionSize(self.RowHeight)
    self.view.setFixedHeight(65)
    self.view.setModel(self.model)
    self.view.selectionModel().selectionChanged.connect(self.onSelectionChanged)

    self.view.setItemDelegateForColumn(self.columnNames.index("MapTo"), ComboDelegate(self.model, ["","TubeRadiusAndColor","TubeRadius","TubeColor"]))

  def onSelectionChanged(self):
    pass

  def getSelectedRow(self):
    selectedRows = self.view.selectionModel().selectedRows()
    for selectedRow in selectedRows:
      return selectedRow.row() # is a single selection view

  def addRowAndSetVisibility(self):
    self.model.insertRow(self.model.rowCount())
    self.view.setFixedHeight(self.view.height+self.RowHeight)
    if self.model.rowCount():
      self.view.setVisible(1)
      self.view.horizontalHeader().setSectionResizeMode(0, qt.QHeaderView.Stretch)
      self.view.horizontalHeader().setSectionResizeMode(1, qt.QHeaderView.Stretch)
      self.view.horizontalHeader().setSectionResizeMode(2, qt.QHeaderView.ResizeToContents)

  def removeLastRowAndSetHeight(self):
    self.model.removeRow(self.model.rowCount()-1)
    self.view.setFixedHeight(self.view.height-self.RowHeight)

  def updateNumberOfRows(self, N):
    if N==0:
      while (self.model.rowCount()):
        self.removeLastRowAndSetHeight()
    elif N>self.model.rowCount():
      while (N>self.model.rowCount()):
        self.addRowAndSetVisibility()
    else:
      while (N<self.model.rowCount()):
        self.removeLastRowAndSetHeight()

  def updateNthRowFromFeature(self, rowNumber, feature):
    for columnNumber,columnName in enumerate(self.columnNames):
      featureKey = self.stringToCammelCase(columnName)
      value = feature[featureKey]
      index = self.model.index(rowNumber, columnNumber)
      if columnNumber == self.columnNames.index("Visible"):
        value = qt.Qt.Checked if value else qt.Qt.Unchecked
        role = qt.Qt.CheckStateRole
      else:
        role = qt.Qt.DisplayRole
      self.model.setData(index, value, role)

  def updateFeatureFromNthRow(self, feature, rowNumber):
    updated = False
    for columnNumber,columnName in enumerate(self.columnNames):
      index = self.model.index(rowNumber, columnNumber)
      if columnNumber == self.columnNames.index("Visible"):
        role = qt.Qt.CheckStateRole
      else:
        role = qt.Qt.DisplayRole
      value = self.model.data(index, role)
      featureKey = self.stringToCammelCase(columnName)
      if feature[featureKey] != value:
        feature[featureKey] = value
        updated = True
    return updated

  def stringToCammelCase(self,str):
    return str[0].lower() + str[1:]
