# QGIS PLUGIN DEVELOPMENT 

-----------------------------------------------
# Project Overview

This project involves the development of a QGIS plugin called "Save Attributes". Updates on the project; on point, polyline and polygon shape files.

-- The data used in the project consists of [GMT456-GitHub Page](https://github.com/banbar/GMT-456-GIS-Programming) page and newly created files to be used in the project.

### Plugin Goals:

* Providing the interface design of the GUI where the extension is used.
* Drawing and determining distances between the nearest/farthest points in a point shapefile.
* Displaying attributes for length and shortest distance in a polyline shapefile.
* Determining attributes indicating the area in a polygon shapefile.

# Plugin Video:

* Below is a video where you can examine the capabilities of the plugin.

https://github.com/GMT-456-GIS-Programming/midterm-project-eslemsahin/assets/120361919/580f1e7e-d9ff-4276-aff8-baf09ba7ae30

# Plugin Capabilities

## Providing the interface design of the GUI where the extension is used.

New project-specific buttons have been added to the GUI design completed using Qt Designer.
* "Input File", "Select Input Layer" and "Select Output Shapfile Location" push and combobox buttons allow the user to specify input and output files.
* "Draw The Lines" push button is used to draw the nearest and farthest points in the point file.
* "Area Size" button is designed to filter points in the polygon file according to a certain area size.
*  Updated color and arrangement offers the user a more understandable and interactive interface.

# ![ui](https://github.com/GMT-456-GIS-Programming/midterm-project-eslemsahin/assets/120361919/b9a58016-38ff-4cae-b514-daa0fdbb6953) 

## Drawing and determining distances between the nearest/farthest points in a point shapefile.

* When the user selects a point shapefile, the system defines a new shapefile using the selected points and input lines, adding these lines to the created shapefile. Subsequently, it determines the distances between two points in the line layer, creating a new vector layer, and visualizes the distances between the shortest and longest two points as lines. It also displays the distance length between the start and end points in the attribute table.

# ![point](https://github.com/GMT-456-GIS-Programming/midterm-project-eslemsahin/assets/120361919/16c4153a-0173-4c01-a531-e6508ddc4126)

## Displaying attributes for length and shortest distance in a polyline shapefile.

* When the user selects a polyline shapefile, the system determines the start and end points of the polyline and saves the shortest distance between these two points, providing the true length of the polyline.
* Unfortunately, due to an error in this project that I couldn't comprehend, I was unable to achieve the correct output in the attribute table.

# ![polyline](https://github.com/GMT-456-GIS-Programming/midterm-project-eslemsahin/assets/120361919/ae7508a2-d5ab-4171-bda3-db9696da7b9f)

## Determining attributes indicating the area in a polygon shapefile.

* When the user selects a shapefile, they have the option to color polygons based on a specific area size. For example, the user can input a desired area value (e.g., 7500) in the GUI interface. 
* Based on this value, polygons with an area larger than 7500 will be colored blue, while those with smaller areas will be colored pink. The plugin provides the user with visual results reflecting this colorization process. Additionally, this colorization process is displayed in the attribute table, allowing the user to examine area details more thoroughly.

# ![polygon](https://github.com/GMT-456-GIS-Programming/midterm-project-eslemsahin/assets/120361919/5dded18f-446a-48dd-a79e-654353b86eb6)

# Conclusion 

* With these updates, new features have been added to the SaveAttributes plugin and improvements have been made to the GUI layout, enabling the plugin to offer different features to the user with calculations in point, polyline, and polygon shape files.
