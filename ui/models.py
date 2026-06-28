from PySide6.QtCore import Qt, QAbstractTableModel, QModelIndex
from utils.helpers import format_size, format_date

class NodeModulesModel(QAbstractTableModel):
    def __init__(self, data=None):
        super().__init__()
        self._data = data or []
        self._headers = ["Select", "Project Name", "Framework", "Package Manager", "Size", "Last Modified", "Status", "Full Path"]

    def data(self, index, role):
        if not index.isValid():
            return None
        
        row = index.row()
        col = index.column()
        item = self._data[row]

        if role == Qt.DisplayRole:
            if col == 1:
                return item["project_name"]
            elif col == 2:
                return item["framework"]
            elif col == 3:
                return item["package_manager"]
            elif col == 4:
                return format_size(item["size"])
            elif col == 5:
                return format_date(item["last_modified"])
            elif col == 6:
                return item["status"]
            elif col == 7:
                return item["path"]

        elif role == Qt.CheckStateRole and col == 0:
            # Using PySide6 Qt.CheckState enums
            return Qt.CheckState.Checked if item.get("selected", False) else Qt.CheckState.Unchecked
            
        elif role == Qt.UserRole:
            return item
            
        return None

    def setData(self, index, value, role):
        if not index.isValid():
            return False

        if role == Qt.CheckStateRole and index.column() == 0:
            # handle PySide6 check state value
            self._data[index.row()]["selected"] = (value == Qt.CheckState.Checked.value or value == Qt.CheckState.Checked)
            self.dataChanged.emit(index, index, [role])
            return True

        return False

    def rowCount(self, index=QModelIndex()):
        return len(self._data)

    def columnCount(self, index=QModelIndex()):
        return len(self._headers)

    def headerData(self, section, orientation, role):
        if role == Qt.DisplayRole and orientation == Qt.Orientation.Horizontal:
            return self._headers[section]
        return None

    def flags(self, index):
        flags = super().flags(index)
        if index.column() == 0:
            flags |= Qt.ItemFlag.ItemIsUserCheckable
        return flags

    def append_item(self, item: dict):
        self.beginInsertRows(QModelIndex(), self.rowCount(), self.rowCount())
        item["selected"] = False
        self._data.append(item)
        self.endInsertRows()

    def get_all_data(self):
        return self._data
        
    def get_selected_items(self):
        return [item for item in self._data if item.get("selected", False)]
        
    def set_all_selected(self, selected: bool):
        if not self._data:
            return
        for item in self._data:
            item["selected"] = selected
        self.dataChanged.emit(self.index(0, 0), self.index(self.rowCount() - 1, 0), [Qt.CheckStateRole])
        
    def clear(self):
        self.beginResetModel()
        self._data.clear()
        self.endResetModel()

    def remove_items(self, paths_to_remove: set):
        """Remove items matching paths and notify views"""
        # Iterate backwards to safely remove items
        for i in range(len(self._data) - 1, -1, -1):
            if self._data[i]["path"] in paths_to_remove:
                self.beginRemoveRows(QModelIndex(), i, i)
                del self._data[i]
                self.endRemoveRows()
