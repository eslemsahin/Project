# -*- coding: utf-8 -*-
"""
/***************************************************************************
 SaveAttributes
                                 A QGIS plugin
 This plugin saves the attribute of the selected vector layer as a csv file. 
 Generated by Plugin Builder: http://g-sherman.github.io/Qgis-Plugin-Builder/
                              -------------------
        begin                : 2020-10-30
        git sha              : $Format:%H$
        copyright            : (C) 2020 by Berk Anbaroğlu
        email                : banbar@hacettepe.edu.tr
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""
from qgis.PyQt.QtCore import QSettings, QTranslator, QCoreApplication
from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtWidgets import QAction, QFileDialog, QMessageBox
from qgis.core import *
from osgeo import ogr, osr, gdal
import os
from PyQt5.QtCore import QVariant
from qgis.utils import iface

from qgis.core.additions.edit import edit
from qgis.PyQt.QtGui import QColor
# Initialize Qt resources from file resources.py
#from .resources import *
# Import the code for the dialog
from .save_attributes_dialog import SaveAttributesDialog
import os.path


class SaveAttributes:
    """QGIS Plugin Implementation."""

    def __init__(self, iface):
        """Constructor.

        :param iface: An interface instance that will be passed to this class
            which provides the hook by which you can manipulate the QGIS
            application at run time.
        :type iface: QgsInterface
        """
        # Save reference to the QGIS interface
        self.iface = iface
        # initialize plugin directory
        self.plugin_dir = os.path.dirname(__file__)
        # initialize locale
        locale = QSettings().value('locale/userLocale')[0:2]
        locale_path = os.path.join(
            self.plugin_dir,
            'i18n',
            'SaveAttributes_{}.qm'.format(locale))

        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)
            QCoreApplication.installTranslator(self.translator)

        # Declare instance attributes
        self.actions = []
        self.menu = self.tr(u'&Save Attributes')

        # Check if plugin was started the first time in current QGIS session
        # Must be set in initGui() to survive plugin reloads
        self.first_start = None

    # noinspection PyMethodMayBeStatic
    def tr(self, message):
        """Get the translation for a string using Qt translation API.

        We implement this ourselves since we do not inherit QObject.

        :param message: String for translation.
        :type message: str, QString

        :returns: Translated version of message.
        :rtype: QString
        """
        # noinspection PyTypeChecker,PyArgumentList,PyCallByClass
        return QCoreApplication.translate('SaveAttributes', message)


    def add_action(
        self,
        icon_path,
        text,
        callback,
        enabled_flag=True,
        add_to_menu=True,
        add_to_toolbar=True,
        status_tip=None,
        whats_this=None,
        parent=None):
        """Add a toolbar icon to the toolbar.

        :param icon_path: Path to the icon for this action. Can be a resource
            path (e.g. ':/plugins/foo/bar.png') or a normal file system path.
        :type icon_path: str

        :param text: Text that should be shown in menu items for this action.
        :type text: str

        :param callback: Function to be called when the action is triggered.
        :type callback: function

        :param enabled_flag: A flag indicating if the action should be enabled
            by default. Defaults to True.
        :type enabled_flag: bool

        :param add_to_menu: Flag indicating whether the action should also
            be added to the menu. Defaults to True.
        :type add_to_menu: bool

        :param add_to_toolbar: Flag indicating whether the action should also
            be added to the toolbar. Defaults to True.
        :type add_to_toolbar: bool

        :param status_tip: Optional text to show in a popup when mouse pointer
            hovers over the action.
        :type status_tip: str

        :param parent: Parent widget for the new action. Defaults None.
        :type parent: QWidget

        :param whats_this: Optional text to show in the status bar when the
            mouse pointer hovers over the action.

        :returns: The action that was created. Note that the action is also
            added to self.actions list.
        :rtype: QAction
        """

        icon = QIcon(icon_path)
        action = QAction(icon, text, parent)
        action.triggered.connect(callback)
        action.setEnabled(enabled_flag)

        if status_tip is not None:
            action.setStatusTip(status_tip)

        if whats_this is not None:
            action.setWhatsThis(whats_this)

        if add_to_toolbar:
            # Adds plugin icon to Plugins toolbar
            self.iface.addToolBarIcon(action)

        if add_to_menu:
            self.iface.addPluginToVectorMenu(
                self.menu,
                action)

        self.actions.append(action)

        return action

    def initGui(self):
        """Create the menu entries and toolbar icons inside the QGIS GUI."""

        icon_path = 'C:/Users/Ata/AppData/Roaming/QGIS/QGIS3/profiles/ata/python/plugins/save_attributes2/icon.ico'
        self.add_action(
            icon_path,
            text=self.tr(u''),
            callback=self.run,
            parent=self.iface.mainWindow())

        # will be set False in run()
        self.first_start = True


    def unload(self):
        """Removes the plugin menu item and icon from QGIS GUI."""
        for action in self.actions:
            self.iface.removePluginVectorMenu(
                self.tr(u'&Save Attributes'),
                action)
            self.iface.removeToolBarIcon(action)

    def select_output_file(self):
        filename, _filter = QFileDialog.getSaveFileName(
            self.dlg, 
            "Select output file ",
            "", 
            '*.csv')
        self.dlg.lineEdit.setText(filename)
    
    def input_shp_file(self):
        self.dlg.lineEdit_input_shp.setText("")
        self.dlg.comboBox_id.clear()
        self.shpPath, self._filter = QFileDialog.getOpenFileName(self.dlg, "Select input shp file","", 'ESRI Shapefiles(*.shp *.SHP);; GeoJSON (*.GEOJSON *.geojson);; Geography Markup Language(*.GML)')
        try:
            self.shp = ogr.Open(self.shpPath)
            self.layer = self.shp.GetLayer(0)
            self.name = self.layer.GetName()
#            self.sr = self.layer.GetSpatialRef().ExportToProj4()
            # If POINT, display . otherwise a LINE
            #self.dlg.m2_lbl_status.setText('<html><head/><body><p><span style=" color:#00ff00;"> ✔ </span></p></body></html>')
            self.dlg.lineEdit_input_shp.setText(self.shpPath)
            
            self.dlg.comboBox_id.clear()
            self.layerDef = self.layer.GetLayerDefn()            
            self.fieldNames = [self.layerDef.GetFieldDefn(i).name for i in range(self.layerDef.GetFieldCount())] 
            self.dlg.comboBox_id.addItems(self.fieldNames)

            self.v_layer = QgsVectorLayer(self.shpPath, self.name, "ogr")
            QgsProject.instance().addMapLayer(self.v_layer)
            self.oznitelikler = self.v_layer.fields().names()
            layers, self.shpPath, fieldNamesLayer = self.loadLayerList()
        except:
            self.dlg.label_wrong_input.setText('Wrong Input')
    
    # createShp is supposed to create a new shapefile.

    def createShp(self, input_line, costs, out_shp, sr):
        driver = ogr.GetDriverByName('Esri Shapefile')
        ds = driver.CreateDataSource(out_shp)
        srs = osr.SpatialReference()
        srs.ImportFromProj4(sr)
        layer = ds.CreateLayer('mst', srs, ogr.wkbLineString)
        layer.CreateField(ogr.FieldDefn('id', ogr.OFTInteger))
        layer.CreateField(ogr.FieldDefn('cost', ogr.OFTReal))
        defn = layer.GetLayerDefn()
        
        for e,i in enumerate(zip(input_line, costs)):
            feat = ogr.Feature(defn)
            feat.SetField('id', e)
            feat.SetField('cost', i[1])
        
            # Geometry
            feat.SetGeometry(i[0])    
            layer.CreateFeature(feat)
        
        ds = layer = defn = feat = None

    def load_comboBox(self):
        layers_shp = []
        layers = [layer for layer in QgsProject.instance().mapLayers().values()]
        
        if layers:
            for layer in layers:
                if hasattr(layer, "dataProvider"):
                    myfilepath = layer.dataProvider().dataSourceUri()
                    myDirectory, nameFile = os.path.split(myfilepath)
                    try:
                        geometry_type = ["Point", "Line", "Polygon", "Unknown"][layer.geometryType()]
                        self.dlg.comboBox.addItem(f"{layer.name()} - {geometry_type}")
                    except:
                        continue

        self.selectedLayerIndex = self.dlg.comboBox.currentIndex()
        
        if not (0 <= self.selectedLayerIndex < len(layers_shp)):
            return
        try:
            self.selectedLayer = layers_shp[self.selectedLayerIndex]
        except:
            return
        print(self.selectedLayer.name())

    def loadLayerList(self):

        layersList = []
        layersList_shp = []
        # Show the shapefiles in the ComboBox
        layers = [layer for layer in QgsProject.instance().mapLayers().values()]
        if len(layers) != 0:  # checklayers exist in the project
            for layer in layers:
                if hasattr(layer, "dataProvider"):  # to not consider Openlayers basemaps in the layer list
                    myfilepath = layer.dataProvider().dataSourceUri()  # directory including filename
                    (myDirectory, nameFile) = os.path.split(myfilepath)  # splitting into directory and filename
                    # if (".shp" in nameFile):
                    try:
                        if layer.geometryType() == 0:
                            # Exception for OSM base map (Raster)
                            layersList.append(layer.name())
                            layersList_shp.append(layer)

                            print("LAYER LIST:", layersList)


                    except:
                        continue

            # Layer lists
            # Point and Polygon layer indexes
            self.dlg.comboBox.clear()
            self.dlg.comboBox.addItems(layersList)
            self.selectedLayerIndex = self.dlg.comboBox.currentIndex()

            if self.selectedLayerIndex < 0 or self.selectedLayerIndex > len(layersList_shp):
                return

            # Selected layers
            self.selectedLayer = layersList_shp[self.selectedLayerIndex]

            fieldNamesLayer = [field.name() for field in self.selectedLayer.fields()]
            return [layers, layersList_shp, fieldNamesLayer]
        else:
            return [layers, False]

    def runAlgorithm(self):

        points = [feat for feat in self.selectedLayer.getFeatures()]

        minDistance = 99999999
        maxDistance = 0
        for x, point in enumerate(points):
            point_geom = point.geometry()  # Input geometry
            for y, pointSearched in enumerate(points):
                pointSearched_geom = pointSearched.geometry()
                if not x == y:  # Could be done by feature id's (do not know which one gives the best performance)
                    distance = point_geom.distance(pointSearched_geom)
                    if distance > maxDistance:
                        maxDistance = distance
                        maxDistFeatures = [point, pointSearched]
                    if distance < minDistance and not distance < 0:
                        minDistance = distance
                        minDistFeatures = [point, pointSearched]

        if len(maxDistFeatures) > 1 and len(minDistFeatures) > 1:

            self.v_layer = QgsVectorLayer("MultiLineString", "lines", "memory",crs=self.v_layer.sourceCrs())
            pr = self.v_layer.dataProvider()
            attr = pr.addAttributes(
                [QgsField('startPoint_ID', QVariant.String), QgsField('endPoint_ID', QVariant.String),
                 QgsField('segment_length', QVariant.Double)])  # int to string for positive id
            self.v_layer.updateFields()
            fields = self.v_layer.fields()

            for i in range(len(maxDistFeatures) - 1):
                lineStart = maxDistFeatures[i].geometry().get()
                lineEnd = maxDistFeatures[i + 1].geometry().get()
                segMax = QgsFeature()
                segMax.setFields(fields, True)
                segMax.setGeometry(QgsGeometry.fromPolyline([lineStart, lineEnd]))
                segMax.setAttributes([maxDistFeatures[i]["id"], maxDistFeatures[i + 1]["id"], maxDistance])

            for i in range(len(minDistFeatures) - 1):
                lineStart = minDistFeatures[i].geometry().get()
                lineEnd = minDistFeatures[i + 1].geometry().get()
                segMin = QgsFeature()
                segMin.setFields(fields, True)
                segMin.setGeometry(QgsGeometry.fromPolyline([lineStart, lineEnd]))
                segMin.setAttributes([minDistFeatures[i]["id"], minDistFeatures[i + 1]["id"], minDistance])

            pr.addFeatures([segMax])
            pr.addFeatures([segMin])

            self.v_layer.updateExtents()
            QgsProject.instance().addMapLayers([self.v_layer])
            # add the line to
            # QgsProject.instance().addMapLayers([self.v_layer]) to add it on iface

    def apply_graduated_symbology(self, area_size):
        myRangeList = []
        
        symbol1 = QgsSymbol.defaultSymbol(self.new2.geometryType())
        symbol1.setColor(QColor("#FF00FF"))
        myRangeList.append(QgsRendererRange(0, area_size, symbol1, f"Areas smaller than {area_size}"))
        
        symbol2 = QgsSymbol.defaultSymbol(self.new2.geometryType())
        symbol2.setColor(QColor("#ADD8E6"))
        myRangeList.append(QgsRendererRange(area_size, float('inf'), symbol2, f"Areas greater than {area_size}"))
        
        renderer = QgsGraduatedSymbolRenderer('Area', myRangeList)
        renderer.setMode(QgsGraduatedSymbolRenderer.Custom)
        
        self.new2.setRenderer(renderer)
        
        print("Graduated color scheme applied")

    def error_msg(self, warning):
        QMessageBox.warning(self.dlg.show(), self.tr("Warning!!!"), self.tr(str(warning)), QMessageBox.Ok)

    def run(self):
        """Run method that performs all the real work"""
        
        # Create the dialog with elements (after translation) and keep reference
        # Only create GUI ONCE in callback, so that it will only load when the plugin is started
        if self.first_start == True:
            self.first_start = False
            self.dlg = SaveAttributesDialog()
            #self.dlg.pushButton.clicked.connect(self.select_output_file)
            self.dlg.pb_select_layer.clicked.connect(self.input_shp_file)
            self.dlg.comboBox.currentIndexChanged.connect(lambda: self.load_comboBox())
            self.dlg.toolButton.clicked.connect(self.select_output_file)
            self.dlg.pushButton.clicked.connect(self.runAlgorithm)

        # show the dialog
        self.dlg.show()
        # Run the dialog event loop
        result = self.dlg.exec_()
        # See if OK was pressed
        if result:

            # Do something useful here - delete the line containing pass and
            # substitute with your code.

            file_path = self.dlg.lineEdit_input_shp.text()
            # Open the shp file
            # Second argument tell whether to read (0, default), or to update (1)
            ds = ogr.Open(file_path,0)

            if ds is None:
                sys.exit('Could not open {0}.'.format(file_path))

            # Obtain the layer
            lyr = ds.GetLayer()

            # Runs, but does not create a new field-------------
            # lyr.CreateField(ogr.FieldDefn('x', ogr.OFTReal))
            # lyr.CreateField(ogr.FieldDefn('y', ogr.OFTReal))
            # # Runs, but does not create a new field-------------

            if (lyr.GetGeomType() == ogr.wkbPoint): #wkb: wll known binary
                type_of_layer = "point"
            elif(lyr.GetGeomType() == ogr.wkbLineString):
                type_of_layer = "line"
            elif(lyr.GetGeomType() == ogr.wkbPolygon):
                type_of_layer = "polygon"


            vlayer = QgsVectorLayer(self.dlg.lineEdit_input_shp.text(),
                                    type_of_layer,
                                    "ogr")

            # Obtain the chosen ID field - it is supposed to be ID.
            # Note: If the "No ID" checkbox is checked, we should not include ID's in the newly created shp file.
            idFieldName = self.dlg.comboBox_id.currentText()


            # Number of features/records
            num_features = lyr.GetFeatureCount()
            print("Number of features: ", num_features)

            if(type_of_layer == "point"):
                layer = iface.activeLayer()
                fields = layer.fields().names()
                field2Add = ["x", "y"]

                layer.startEditing()
                dp = layer.dataProvider()

                for name in field2Add:
                    if not name in fields:
                        dp.addAttributes([QgsField(name, QVariant.Double)])

                layer.updateFields()

                all_features = layer.getFeatures()

                for feat in all_features:
                    geom = feat.geometry()
                    x = geom.asPoint().x()
                    y = geom.asPoint().y()


                    #layer.updateFeature(feat.id())
            # Commit changes
                layer.commitChanges()
            if type_of_layer =="line":
                QgsProject.instance().addMapLayer(self.v_layer)

                attributes = self.v_layer.fields().names()

                print(attributes)

                attributes_to_add = ["minDistance", "realDistance"]
                self.v_layer.startEditing()
                dp = self.v_layer.dataProvider()

                for attribute_name in attributes_to_add:
                    if not attribute_name in attributes:
                        dp.addAttributes([QgsField(attribute_name, QVariant.Double)])

                self.v_layer.updateFields()

                lines = [feat for feat in self.v_layer.getFeatures()]

                if len(lines) > 0:
                    sCrs = self.v_layer.sourceCrs()
                    print("crs: ", sCrs)
                    d = QgsDistanceArea()
                    d.setEllipsoid(sCrs.ellipsoidAcronym())

                    for line in lines:
                        geom = line.geometry()
                        realDistance = d.measureLine(geom.asMultiPolyline()[0])

                        print(realDistance)

                        start_point = geom.constGet()[0][0]
                        end_point = geom.constGet()[0][-1]

                        print("start point: ", start_point)
                        print("end point: ", end_point)

                        min_line = QgsFeature()
                        min_line.setGeometry(QgsGeometry.fromPolyline([start_point, end_point]))

                        min_distance = d.measureLine(min_line.geometry().asPolyline())

                        print("minimum distance : ", min_distance)

                        line["minDistance"] = min_distance
                        line["realDistance"] = realDistance
                        self.v_layer.updateFeature(line)

                    self.v_layer.updateFields()
                    self.v_layer.commitChanges()

            elif (type_of_layer == "polygon"):
                #self.newayer = QgsVectorLayer(self.shpPath, self.name, "ogr")
                self.new2= QgsVectorLayer("Polygon","Area_calc","memory",crs=self.v_layer.sourceCrs())
                pr = self.new2.dataProvider()
                pr.addAttributes([QgsField("id", QVariant.Int),QgsField("featNum", QVariant.Int),QgsField("Area",QVariant.String)])
                self.new2.updateFields()
                features = self.v_layer.getFeatures()
                for x in features:
                    geom = x.geometry()
                    f = QgsFeature()
                    f.setGeometry(geom)
                    f.setAttributes([x['id'],x.id(),geom.area()])
                    pr.addFeature(f)
                    self.new2.updateExtents()
                QgsProject.instance().addMapLayer(self.new2)

                area_size = int(self.dlg.lineEdit_2.text())
                self.apply_graduated_symbology(area_size)

                caps = self.v_layer.dataProvider().capabilities()
                fields_name = [f.name() for f in self.v_layer.fields()]

                if caps & QgsVectorDataProvider.AddAttributes:
                    # We check if the attribute field is not exist
                    if "Area" not in fields_name:
                        # We add the field name Area and with the double type (it can be integer or text
                        self.new2.dataProvider().addAttributes([QgsField("Area", QVariant.Double)])
                        # We update layer's field otherwise we'll not have the field
                        self.new2.updateFields()
                        # Recreate the list field by the name to have index of the field
                        fields_name = [f.name() for f in self.new2.fields()]
                        # we get the index of the Area field
                        fareaidx = fields_name.index('Area')
                    else:
                        # We are here because there is a field name Area
                        print("The Area field is already added")
                        # Recreate the list field by the name to have index of the field
                        fields_name = [f.name() for f in self.new2.fields()]
                        # we get the index of the Area field
                        fareaidx = fields_name.index('Area')

                # Here we check if we can change attribute of the layer
                if caps & QgsVectorDataProvider.ChangeAttributeValues:
                    # we loop^on every feature
                    for feature in self.new2.getFeatures():
                        # For each feature :
                        # We calculate the area and put the index of the field Area
                        # We round the area value by 2 digit
                        attrs = {fareaidx: round(feature.geometry().area(), 2)}
                        # We change the the value of Area Field for this feature.
                        self.new2.dataProvider().changeAttributeValues({feature.id(): attrs})
            else:
                self.error_msj("Please check the shapefile you selected!")