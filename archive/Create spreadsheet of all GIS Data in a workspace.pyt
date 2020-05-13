import os, arcpy, time, csv
arcpy.env.overwriteOutput = True

class Toolbox(object):
	def __init__(self):
		"""Define the toolbox (the name of the toolbox is the name of the
		.pyt file)."""
		self.label = "Toolbox"
		self.alias = ""

		# List of tool classes associated with this toolbox
		self.tools = [InventoryData]


class InventoryData(object):
	def __init__(self):
		"""Define the InventoryData (name is the name of the class)."""
		self.label = "InventoryData"
		self.description = ""
		self.canRunInBackground = False

	def getParameterInfo(self):
		"""Define parameter definitions"""
		param0 = arcpy.Parameter(
		displayName="Root folder full of GIS data",
		name="inFolder",
		datatype="GPString",
		parameterType="Required",
		direction="Input")

		param1 = arcpy.Parameter(
		displayName="Output csv file (optional. Will put xls in root folder if empty)",
		name="outCSV",
		datatype="GPString",
		parameterType="Optional",
		direction="Input")

		# params = [param0, param1, param2, param3, param4, param5]
		params = [param0, param1]
		return params

	def isLicensed(self):
		"""Set whether tool is licensed to execute."""
		return True

	def updateParameters(self, parameters):
		"""Modify the values and properties of parameters before internal
		validation is performed.  This method is called whenever a parameter
		has been changed."""
		if parameters[1].valueAsText is not None:
			if not parameters[1].valueAsText.endswith('csv'):
				parameters[1].value=parameters[1].valueAsText+'.csv'
		else:
			name = parameters[0].valueAsText.split("\\")[-1]
			parameters[1].value=parameters[0].valueAsText + os.sep + name + '_Inventory_Output.csv'
		return

	def updateMessages(self, parameters):
		"""Modify the messages created by internal validation for each tool
		parameter.  This method is called after internal validation."""
		return

	def execute(self, parameters, messages):
		"""The source code of the tool."""
		def inventory_data(workspace, datatypes):
			"""
			Generates full path names under a catalog tree for all requested
			datatype(s).

			Parameters:
			workspace: string
				The top-level workspace that will be used.
			datatypes: string | list | tuple
				Keyword(s) representing the desired datatypes. A single
				datatype can be expressed as a string, otherwise use
				a list or tuple. See arcpy.da.Walk documentation 
				for a full list.
			"""
			for path, path_names, data_names in arcpy.da.Walk(workspace, datatype=datatypes):
				for data_name in data_names:
					yield os.path.join(path, data_name)


		def hasSR(raster):
			try:
				desc = arcpy.Describe(raster)
				SR = desc.spatialReference
				srName = SR.name
				if hasattr(SR, "name"):
					return srName
				else:
					return "No Spatial Reference"
			except:
				return "Spatial Reference Error"

		def dateMod(raster):
			try:
				modTime = time.ctime(os.path.getmtime(raster))
				return modTime
			except WindowsError:
				return "Time Error"

		def getKB(raster):
			try:
				size = os.path.getsize(raster)
				return str(size/1024)
			except:
				return "Size Error"

		def getCellWH(raster):
			try:
				desc = arcpy.Describe(raster)
				cellH = str(desc.meanCellHeight)
				cellW = str(desc.meanCellWidth)
				return cellH + "x" + cellW
			except:
				return "Cell size error"

		def getPixelType(raster):
			try:
				desc = arcpy.Describe(raster)
				pixelType = desc.pixelType
				return pixelType
			except:
				return "Pixel type error"

		def getMin(raster):
			try:
				rast = arcpy.Raster(raster)
				return str(rast.minimum)
			except:
				return "Min value error"

		def getMax(raster):
			try:
				rast = arcpy.Raster(raster)				
				return str(rast.maximum)
			except:
				return "Max value error"

		def getFieldNames(fc):
			'''
			Get names and aliases for all fields, returns a string joined by ;
			'''
			try:
				flds_alias = [f.aliasName for f in arcpy.ListFields(fc)]
				flds_names = [f.name for f in arcpy.ListFields(fc)]
				joined = [' -- '.join(map(str, i)) for i in zip(flds_names, flds_alias)]
				fieldsString = ' ; '.join(str(e) for e in joined)
				return fieldsString
			except:
				return "Could not get field names"

		def getDataType(fc):
			try:
				desc = arcpy.Describe(fc)
				fcDataType = desc.dataType
				return fcDataType
			except:
				return "Data type error"

		def getShapeType(fc):
			try:
				desc = arcpy.Describe(fc)
				fcShapeType = desc.shapeType
				return fcShapeType
			except:
				return "Shape type error"


		inFolder = parameters[0].valueAsText
		outCSV = parameters[1].valueAsText

		def run():
			w = csv.writer(f)
			w.writerow([
				'File Name',
				'File Path',
				'Projection',
				'Data Type',
				'Shape Type',
				'CellHW',
				'Pixel Type',
				'Min Value',
				'Max Value',
			 	'SizeKB',
				'Date Modified',
				'Field Names'
				])

			for data in inventory_data(inFolder, ["Any"]):
				try:
					desc = arcpy.Describe(data)
					fileName = desc.name
					filePath = desc.path

					arcpy.AddMessage("Writing " + data + " to file.")
					output = [
						fileName, 
						filePath,
						hasSR(data),
						getDataType(data),
						getShapeType(data),
						getCellWH(data),
						getPixelType(data),
						getMin(data),
						getMax(data),
						getKB(data),
						dateMod(data),
						getFieldNames(data)
						]
					w.writerow(output) 
				except:
					arcpy.AddMessage("Error")
					w.writerow(["Error: " + data])


			# For some reason this doesn't work at all. No idea why.  Works fine inside arcmap window. 
			arcpy.AddMessage("Converting csv to xls")
			outXLS = outCSV.replace(".csv", ".xls")
			arcpy.TableToExcel_conversion(Input_Table=outCSV, 
				Output_Excel_File=outXLS)


		if sys.version_info[0] < 3:
			with open(outCSV, 'wb') as f:
				run()
		else:			
			with open(outCSV, 'w', newline = '') as f:
				run()
	
		return
