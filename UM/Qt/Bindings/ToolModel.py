# Copyright (c) 2017 Ultimaker B.V.
# Uranium is released under the terms of the LGPLv3 or higher.

from PyQt5.QtCore import Qt

from UM.Application import Application

from UM.Qt.ListModel import ListModel
from UM.PluginRegistry import PluginRegistry


class ToolModel(ListModel):
    IdRole = Qt.UserRole + 1
    NameRole = Qt.UserRole + 2
    IconRole = Qt.UserRole + 3
    ToolActiveRole = Qt.UserRole + 4
    ToolEnabledRole = Qt.UserRole + 5
    DescriptionRole = Qt.UserRole + 6
    LocationRole = Qt.UserRole + 7

    def __init__(self, parent = None):
        super().__init__(parent)

        self._controller = Application.getInstance().getController()
        self._controller.toolsChanged.connect(self._onToolsChanged)
        self._controller.toolEnabledChanged.connect(self._onToolEnabledChanged)
        self._controller.activeToolChanged.connect(self._onActiveToolChanged)
        self._onToolsChanged()

        self.addRoleName(self.IdRole, "id")
        self.addRoleName(self.NameRole, "name")
        self.addRoleName(self.IconRole, "icon")
        self.addRoleName(self.ToolActiveRole, "active")
        self.addRoleName(self.ToolEnabledRole, "enabled")
        self.addRoleName(self.DescriptionRole, "description")
        self.addRoleName(self.LocationRole, "location")

    def _onToolsChanged(self):
        items = []

        tools = self._controller.getAllTools()
        for name in tools:
            tool_meta_data = PluginRegistry.getInstance().getMetaData(name).get("tool", {})
            location = PluginRegistry.getInstance().getMetaData(name).get("location", "")

            # Skip tools that are marked as not visible
            if "visible" in tool_meta_data and not tool_meta_data["visible"]:
                continue

            # Optional metadata elements
            description = tool_meta_data.get("description", "")
            icon_name = tool_meta_data.get("icon", "default.png")

            weight = tool_meta_data.get("weight", 0)

            enabled = self._controller.getTool(name).getEnabled()

            items.append({
                "id": name,
                "name": tool_meta_data.get("name", name),
                "icon": icon_name,
                "location": location,
                "active": False,
                "enabled": enabled,
                "description": description,
                "weight": weight
            })

        items.sort(key = lambda t: t["weight"])
        self.setItems(items)

    def _onActiveToolChanged(self):
        active_tool = self._controller.getActiveTool()

        for index, value in enumerate(self.items):
            if self._controller.getTool(value["id"]) == active_tool:
                self.setProperty(index, "active", True)
            else:
                self.setProperty(index, "active", False)

    def _onToolEnabledChanged(self, tool_id, enabled):
        index = self.find("id", tool_id)
        if index >= 0:
            self.setProperty(index, "enabled", enabled)
