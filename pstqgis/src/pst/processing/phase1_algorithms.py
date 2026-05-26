

class CreateSegmentMapAlgorithm(PstProcessingAlgorithmBase):
	NETWORK_TYPE = 'NETWORK_TYPE'
	NETWORK = 'NETWORK'
	UNLINKS = 'UNLINKS'
	TRIM_SNAP = 'TRIM_SNAP'
	TRIM_TAIL = 'TRIM_TAIL'
	TRIM_COLDEV = 'TRIM_COLDEV'
	COPY_COLUMN = 'COPY_COLUMN'
	COPY_COLUMN_OUT = 'COPY_COLUMN_OUT'

	_NETWORK_TYPES = [
		('Axial or segment', 'AXIAL_OR_SEGMENT'),
		('Road center lines', 'ROAD_CENTER_LINES'),
	]

	def initAlgorithm(self, config):
		self.addParameter(QgsProcessingParameterEnum(
			self.NETWORK_TYPE,
			self.tr('Network type'),
			options=[entry[0] for entry in self._NETWORK_TYPES],
			defaultValue=0,
		))
		self.addParameter(QgsProcessingParameterVectorLayer(
			self.NETWORK,
			self.tr('Network table'),
			types=[QgsProcessing.TypeVectorLine],
		))
		self.addParameter(QgsProcessingParameterFeatureSource(
			self.UNLINKS,
			self.tr('Unlinks'),
			types=[QgsProcessing.TypeVectorPoint],
			optional=True,
		))
		self.addParameter(QgsProcessingParameterNumber(
			self.TRIM_SNAP,
			self.tr('Snap points closer than (meters)'),
			type=QgsProcessingParameterNumber.Double,
			defaultValue=1,
			minValue=1,
		))
		self.addParameter(QgsProcessingParameterNumber(
			self.TRIM_TAIL,
			self.tr('Remove tail segments shorter than (meters)'),
			type=QgsProcessingParameterNumber.Double,
			defaultValue=10,
			minValue=1,
		))
		self.addParameter(QgsProcessingParameterNumber(
			self.TRIM_COLDEV,
			self.tr('Merge segment-pairs with colinear deviation below (meters)'),
			type=QgsProcessingParameterNumber.Double,
			defaultValue=1,
			minValue=1,
		))
		self.addParameter(QgsProcessingParameterField(
			self.COPY_COLUMN,
			self.tr('Copy input column'),
			parentLayerParameterName=self.NETWORK,
			optional=True,
		))
		self.addParameter(QgsProcessingParameterString(
			self.COPY_COLUMN_OUT,
			self.tr('Copied output column name'),
			optional=True,
		))

	def _collectProperties(self, parameters, context):
		props = {}
		props['in_network_type'] = self._NETWORK_TYPES[self.parameterAsEnum(parameters, self.NETWORK_TYPE, context)][1]
		props['in_network'] = self.NETWORK
		props['in_unlinks'] = self.UNLINKS
		props['in_unlinks_enabled'] = self.parameterAsVectorLayer(parameters, self.UNLINKS, context) is not None
		props['trim_snap'] = self.parameterAsDouble(parameters, self.TRIM_SNAP, context)
		props['trim_tail'] = self.parameterAsDouble(parameters, self.TRIM_TAIL, context)
		props['trim_coldev'] = self.parameterAsDouble(parameters, self.TRIM_COLDEV, context)
		props['copy_column_in'] = self.parameterAsString(parameters, self.COPY_COLUMN, context)
		props['copy_column_out'] = self.parameterAsString(parameters, self.COPY_COLUMN_OUT, context)
		props['copy_column_enabled'] = bool(props['copy_column_in']) and bool(props['copy_column_out'])
		return props

	def checkParameterValues(self, parameters, context):
		props = self._collectProperties(parameters, context)
		if bool(props['copy_column_in']) != bool(props['copy_column_out']):
			return (False, 'To copy a column, both the input column and output column name must be set.')
		return (True, None)

	def processAlgorithm(self, parameters, context, feedback):
		from ..analyses import CreateSegmentMapAnalysis
		return self._run_analysis(CreateSegmentMapAnalysis, parameters, context, feedback)

	def name(self):
		return 'createsegmentmap'

	def displayName(self):
		return self.tr('Create Segment Map')

	def createInstance(self):
		return CreateSegmentMapAlgorithm()
