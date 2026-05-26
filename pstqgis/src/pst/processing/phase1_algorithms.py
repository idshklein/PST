"""
Copyright 2019 Meta Berghauser Pont

This file is part of PST.

PST is free software: you can redistribute it and/or modify
it under the terms of the GNU Lesser General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version. The GNU Lesser General Public License
is intended to guarantee your freedom to share and change all versions
of a program--to make sure it remains free software for all its users.

PST is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU Lesser General Public License for more details.

You should have received a copy of the GNU Lesser General Public License
along with PST. If not, see <http://www.gnu.org/licenses/>.
"""

from qgis.PyQt.QtCore import QCoreApplication
from qgis.core import (
    QgsProcessing,
    QgsProcessingAlgorithm,
    QgsProcessingParameterBoolean,
    QgsProcessingParameterEnum,
    QgsProcessingParameterFeatureSource,
    QgsProcessingParameterField,
    QgsProcessingParameterNumber,
    QgsProcessingParameterString,
    QgsProcessingParameterVectorLayer,
)

from ..analyses import (
    AnalysisDelegateFilter,
    AngularChoiceAnalysis,
    AngularIntegrationAnalysis,
    CreateSegmentMapAnalysis,
    NetworkBetweennessAnalysis,
    NetworkIntegrationAnalysis,
    ReachAnalysis,
)
from .processing_analysis_delegate import ProcessingAnalysisDelegate
from .processing_qgis_model import ProcessingQgisModel


class PstProcessingAlgorithmBase(QgsProcessingAlgorithm):

    def tr(self, string):
        return QCoreApplication.translate('Processing', string)

    def _run_analysis(self, analysisClass, parameters, context, feedback):
        props = self._collectProperties(parameters, context)
        model = ProcessingQgisModel(self, parameters, context)
        analysis = analysisClass(model, props)
        delegate = AnalysisDelegateFilter(ProcessingAnalysisDelegate(feedback))
        analysis.run(delegate)
        return {}

    def group(self):
        return self.tr('PST analyses')

    def groupId(self):
        return 'pst_analyses'


class AngularIntegrationAlgorithm(PstProcessingAlgorithmBase):
    NETWORK = 'NETWORK'
    CALC_NO_WEIGHT = 'CALC_NO_WEIGHT'
    CALC_LENGTH_WEIGHT = 'CALC_LENGTH_WEIGHT'
    NORM_NORMALIZATION = 'NORM_NORMALIZATION'
    NORM_SYNTAX = 'NORM_SYNTAX'
    NORM_HILLIER = 'NORM_HILLIER'
    ANGLE_PRECISION = 'ANGLE_PRECISION'
    ANGLE_THRESHOLD = 'ANGLE_THRESHOLD'
    RADIUS_STRAIGHT = 'RADIUS_STRAIGHT'
    RADIUS_WALKING = 'RADIUS_WALKING'
    RADIUS_STEPS = 'RADIUS_STEPS'
    RADIUS_ANGULAR = 'RADIUS_ANGULAR'
    OUTPUT_N = 'OUTPUT_N'
    OUTPUT_TD = 'OUTPUT_TD'
    OUTPUT_MD = 'OUTPUT_MD'

    def initAlgorithm(self, config):
        self.addParameter(QgsProcessingParameterVectorLayer(self.NETWORK, self.tr('Segment network'), types=[QgsProcessing.TypeVectorLine]))
        self.addParameter(QgsProcessingParameterBoolean(self.CALC_NO_WEIGHT, self.tr('No weights'), defaultValue=True))
        self.addParameter(QgsProcessingParameterBoolean(self.CALC_LENGTH_WEIGHT, self.tr('Weigh by length'), defaultValue=False))
        self.addParameter(QgsProcessingParameterBoolean(self.NORM_NORMALIZATION, self.tr('Normalization (Turner 2007)'), defaultValue=True))
        self.addParameter(QgsProcessingParameterBoolean(self.NORM_SYNTAX, self.tr('Syntax normalization (NAIN)'), defaultValue=False))
        self.addParameter(QgsProcessingParameterBoolean(self.NORM_HILLIER, self.tr('Normalization (Hillier)'), defaultValue=False))
        self.addParameter(QgsProcessingParameterNumber(self.ANGLE_PRECISION, self.tr('Angle precision'), type=QgsProcessingParameterNumber.Integer, defaultValue=1, minValue=0))
        self.addParameter(QgsProcessingParameterNumber(self.ANGLE_THRESHOLD, self.tr('Angle threshold'), type=QgsProcessingParameterNumber.Double, defaultValue=0, minValue=0))
        self.addParameter(QgsProcessingParameterNumber(self.RADIUS_STRAIGHT, self.tr('Straight radius'), optional=True, type=QgsProcessingParameterNumber.Double))
        self.addParameter(QgsProcessingParameterNumber(self.RADIUS_WALKING, self.tr('Walking radius'), optional=True, type=QgsProcessingParameterNumber.Double))
        self.addParameter(QgsProcessingParameterNumber(self.RADIUS_STEPS, self.tr('Steps radius'), optional=True, type=QgsProcessingParameterNumber.Integer))
        self.addParameter(QgsProcessingParameterNumber(self.RADIUS_ANGULAR, self.tr('Angular radius'), optional=True, type=QgsProcessingParameterNumber.Double))
        self.addParameter(QgsProcessingParameterBoolean(self.OUTPUT_N, self.tr('Output node count (N)'), defaultValue=True))
        self.addParameter(QgsProcessingParameterBoolean(self.OUTPUT_TD, self.tr('Output total depth (TD)'), defaultValue=True))
        self.addParameter(QgsProcessingParameterBoolean(self.OUTPUT_MD, self.tr('Output mean depth (MD)'), defaultValue=True))

    def _collectProperties(self, parameters, context):
        props = {}
        props['in_network'] = self.NETWORK
        props['calc_no_weight'] = self.parameterAsBool(parameters, self.CALC_NO_WEIGHT, context)
        props['calc_length_weight'] = self.parameterAsBool(parameters, self.CALC_LENGTH_WEIGHT, context)
        props['norm_normalization'] = self.parameterAsBool(parameters, self.NORM_NORMALIZATION, context)
        props['norm_syntax'] = self.parameterAsBool(parameters, self.NORM_SYNTAX, context)
        props['norm_hillier'] = self.parameterAsBool(parameters, self.NORM_HILLIER, context)
        props['angle_precision'] = self.parameterAsInt(parameters, self.ANGLE_PRECISION, context)
        props['angle_threshold'] = self.parameterAsDouble(parameters, self.ANGLE_THRESHOLD, context)
        props['rad_straight'] = self.parameterAsDouble(parameters, self.RADIUS_STRAIGHT, context)
        props['rad_straight_enabled'] = bool(props['rad_straight'])
        props['rad_walking'] = self.parameterAsDouble(parameters, self.RADIUS_WALKING, context)
        props['rad_walking_enabled'] = bool(props['rad_walking'])
        props['rad_steps'] = self.parameterAsInt(parameters, self.RADIUS_STEPS, context)
        props['rad_steps_enabled'] = bool(props['rad_steps'])
        props['rad_angular'] = self.parameterAsDouble(parameters, self.RADIUS_ANGULAR, context)
        props['rad_angular_enabled'] = bool(props['rad_angular'])
        props['output_N'] = self.parameterAsBool(parameters, self.OUTPUT_N, context)
        props['output_TD'] = self.parameterAsBool(parameters, self.OUTPUT_TD, context)
        props['output_MD'] = self.parameterAsBool(parameters, self.OUTPUT_MD, context)
        return props

    def checkParameterValues(self, parameters, context):
        if (not self.parameterAsBool(parameters, self.CALC_NO_WEIGHT, context)
                and not self.parameterAsBool(parameters, self.CALC_LENGTH_WEIGHT, context)):
            return (False, 'Please select at least one weight mode.')
        if (not self.parameterAsBool(parameters, self.NORM_NORMALIZATION, context)
                and not self.parameterAsBool(parameters, self.NORM_SYNTAX, context)
                and not self.parameterAsBool(parameters, self.NORM_HILLIER, context)):
            return (False, 'Please select at least one normalization mode.')
        props = self._collectProperties(parameters, context)
        if not props['rad_straight_enabled'] and not props['rad_walking_enabled'] and not props['rad_steps_enabled'] and not props['rad_angular_enabled']:
            return (False, 'Please specify at least one radius.')
        return (True, None)

    def processAlgorithm(self, parameters, context, feedback):
        return self._run_analysis(AngularIntegrationAnalysis, parameters, context, feedback)

    def name(self):
        return 'angularintegration'

    def displayName(self):
        return self.tr('Angular Integration')

    def createInstance(self):
        return AngularIntegrationAlgorithm()


class AngularChoiceAlgorithm(PstProcessingAlgorithmBase):
    NETWORK = 'NETWORK'
    WEIGHT_NONE = 'WEIGHT_NONE'
    WEIGHT_LENGTH = 'WEIGHT_LENGTH'
    NORM_NONE = 'NORM_NONE'
    NORM_NORMALIZATION = 'NORM_NORMALIZATION'
    NORM_STANDARD = 'NORM_STANDARD'
    NORM_SYNTAX = 'NORM_SYNTAX'
    ANGLE_PRECISION = 'ANGLE_PRECISION'
    ANGLE_THRESHOLD = 'ANGLE_THRESHOLD'
    RADIUS_STRAIGHT = 'RADIUS_STRAIGHT'
    RADIUS_WALKING = 'RADIUS_WALKING'
    RADIUS_STEPS = 'RADIUS_STEPS'
    RADIUS_ANGULAR = 'RADIUS_ANGULAR'
    OUTPUT_N = 'OUTPUT_N'
    OUTPUT_TD = 'OUTPUT_TD'
    OUTPUT_MD = 'OUTPUT_MD'

    def initAlgorithm(self, config):
        self.addParameter(QgsProcessingParameterVectorLayer(self.NETWORK, self.tr('Segment network'), types=[QgsProcessing.TypeVectorLine]))
        self.addParameter(QgsProcessingParameterBoolean(self.WEIGHT_NONE, self.tr('No weight'), defaultValue=True))
        self.addParameter(QgsProcessingParameterBoolean(self.WEIGHT_LENGTH, self.tr('Weigh by segment length'), defaultValue=False))
        self.addParameter(QgsProcessingParameterBoolean(self.NORM_NONE, self.tr('No normalization'), defaultValue=True))
        self.addParameter(QgsProcessingParameterBoolean(self.NORM_NORMALIZATION, self.tr('Normalization (Turner 2007)'), defaultValue=False))
        self.addParameter(QgsProcessingParameterBoolean(self.NORM_STANDARD, self.tr('Standard normalization (0-1)'), defaultValue=False))
        self.addParameter(QgsProcessingParameterBoolean(self.NORM_SYNTAX, self.tr('Syntax normalization (NACH)'), defaultValue=False))
        self.addParameter(QgsProcessingParameterNumber(self.ANGLE_PRECISION, self.tr('Angle precision'), type=QgsProcessingParameterNumber.Integer, defaultValue=1, minValue=0))
        self.addParameter(QgsProcessingParameterNumber(self.ANGLE_THRESHOLD, self.tr('Angle threshold'), type=QgsProcessingParameterNumber.Double, defaultValue=0, minValue=0))
        self.addParameter(QgsProcessingParameterNumber(self.RADIUS_STRAIGHT, self.tr('Straight radius'), optional=True, type=QgsProcessingParameterNumber.Double))
        self.addParameter(QgsProcessingParameterNumber(self.RADIUS_WALKING, self.tr('Walking radius'), optional=True, type=QgsProcessingParameterNumber.Double))
        self.addParameter(QgsProcessingParameterNumber(self.RADIUS_STEPS, self.tr('Steps radius'), optional=True, type=QgsProcessingParameterNumber.Integer))
        self.addParameter(QgsProcessingParameterNumber(self.RADIUS_ANGULAR, self.tr('Angular radius'), optional=True, type=QgsProcessingParameterNumber.Double))
        self.addParameter(QgsProcessingParameterBoolean(self.OUTPUT_N, self.tr('Output node count (N)'), defaultValue=True))
        self.addParameter(QgsProcessingParameterBoolean(self.OUTPUT_TD, self.tr('Output total depth (TD)'), defaultValue=True))
        self.addParameter(QgsProcessingParameterBoolean(self.OUTPUT_MD, self.tr('Output mean depth (MD)'), defaultValue=True))

    def _collectProperties(self, parameters, context):
        props = {}
        props['in_network'] = self.NETWORK
        props['weight_none'] = self.parameterAsBool(parameters, self.WEIGHT_NONE, context)
        props['weight_length'] = self.parameterAsBool(parameters, self.WEIGHT_LENGTH, context)
        props['norm_none'] = self.parameterAsBool(parameters, self.NORM_NONE, context)
        props['norm_normalization'] = self.parameterAsBool(parameters, self.NORM_NORMALIZATION, context)
        props['norm_standard'] = self.parameterAsBool(parameters, self.NORM_STANDARD, context)
        props['norm_syntax'] = self.parameterAsBool(parameters, self.NORM_SYNTAX, context)
        props['angle_precision'] = self.parameterAsInt(parameters, self.ANGLE_PRECISION, context)
        props['angle_threshold'] = self.parameterAsDouble(parameters, self.ANGLE_THRESHOLD, context)
        props['rad_straight'] = self.parameterAsDouble(parameters, self.RADIUS_STRAIGHT, context)
        props['rad_straight_enabled'] = bool(props['rad_straight'])
        props['rad_walking'] = self.parameterAsDouble(parameters, self.RADIUS_WALKING, context)
        props['rad_walking_enabled'] = bool(props['rad_walking'])
        props['rad_steps'] = self.parameterAsInt(parameters, self.RADIUS_STEPS, context)
        props['rad_steps_enabled'] = bool(props['rad_steps'])
        props['rad_angular'] = self.parameterAsDouble(parameters, self.RADIUS_ANGULAR, context)
        props['rad_angular_enabled'] = bool(props['rad_angular'])
        props['output_N'] = self.parameterAsBool(parameters, self.OUTPUT_N, context)
        props['output_TD'] = self.parameterAsBool(parameters, self.OUTPUT_TD, context)
        props['output_MD'] = self.parameterAsBool(parameters, self.OUTPUT_MD, context)
        return props

    def checkParameterValues(self, parameters, context):
        if (not self.parameterAsBool(parameters, self.WEIGHT_NONE, context)
                and not self.parameterAsBool(parameters, self.WEIGHT_LENGTH, context)):
            return (False, 'Please select at least one weight mode.')
        if (not self.parameterAsBool(parameters, self.NORM_NONE, context)
                and not self.parameterAsBool(parameters, self.NORM_NORMALIZATION, context)
                and not self.parameterAsBool(parameters, self.NORM_STANDARD, context)
                and not self.parameterAsBool(parameters, self.NORM_SYNTAX, context)):
            return (False, 'Please select at least one normalization mode.')
        props = self._collectProperties(parameters, context)
        if not props['rad_straight_enabled'] and not props['rad_walking_enabled'] and not props['rad_steps_enabled'] and not props['rad_angular_enabled']:
            return (False, 'Please specify at least one radius.')
        return (True, None)

    def processAlgorithm(self, parameters, context, feedback):
        return self._run_analysis(AngularChoiceAnalysis, parameters, context, feedback)

    def name(self):
        return 'angularchoice'

    def displayName(self):
        return self.tr('Angular Choice')

    def createInstance(self):
        return AngularChoiceAlgorithm()


class ReachAlgorithm(PstProcessingAlgorithmBase):
    NETWORK = 'NETWORK'
    UNLINKS = 'UNLINKS'
    ORIGINS = 'ORIGINS'
    CALC_COUNT = 'CALC_COUNT'
    CALC_LENGTH = 'CALC_LENGTH'
    CALC_AREA = 'CALC_AREA'
    AREA_UNIT = 'AREA_UNIT'
    RADIUS_STRAIGHT = 'RADIUS_STRAIGHT'
    RADIUS_WALKING = 'RADIUS_WALKING'
    RADIUS_STEPS = 'RADIUS_STEPS'
    RADIUS_ANGULAR = 'RADIUS_ANGULAR'
    _AREA_UNITS = [
        ('square meter', 'm2'),
        ('square kilometer', 'km2'),
        ('hectare', 'ha'),
    ]

    def initAlgorithm(self, config):
        self.addParameter(QgsProcessingParameterVectorLayer(self.NETWORK, self.tr('Network'), types=[QgsProcessing.TypeVectorLine]))
        self.addParameter(QgsProcessingParameterFeatureSource(self.UNLINKS, self.tr('Unlinks'), types=[QgsProcessing.TypeVectorPoint], optional=True))
        self.addParameter(QgsProcessingParameterFeatureSource(self.ORIGINS, self.tr('Origins'), types=[QgsProcessing.TypeVectorPoint], optional=True))
        self.addParameter(QgsProcessingParameterBoolean(self.CALC_COUNT, self.tr('Calculate number of reached lines'), defaultValue=True))
        self.addParameter(QgsProcessingParameterBoolean(self.CALC_LENGTH, self.tr('Calculate total length of reached lines'), defaultValue=True))
        self.addParameter(QgsProcessingParameterBoolean(self.CALC_AREA, self.tr('Calculate reached area'), defaultValue=True))
        self.addParameter(QgsProcessingParameterEnum(self.AREA_UNIT, self.tr('Area unit'), options=[entry[0] for entry in self._AREA_UNITS], defaultValue=0))
        self.addParameter(QgsProcessingParameterNumber(self.RADIUS_STRAIGHT, self.tr('Straight radius'), optional=True, type=QgsProcessingParameterNumber.Double))
        self.addParameter(QgsProcessingParameterNumber(self.RADIUS_WALKING, self.tr('Walking radius'), optional=True, type=QgsProcessingParameterNumber.Double))
        self.addParameter(QgsProcessingParameterNumber(self.RADIUS_STEPS, self.tr('Steps radius'), optional=True, type=QgsProcessingParameterNumber.Integer))
        self.addParameter(QgsProcessingParameterNumber(self.RADIUS_ANGULAR, self.tr('Angular radius'), optional=True, type=QgsProcessingParameterNumber.Double))

    def _collectProperties(self, parameters, context):
        props = {}
        props['in_network'] = self.NETWORK
        props['in_unlinks'] = self.UNLINKS
        props['in_unlinks_enabled'] = self.parameterAsVectorLayer(parameters, self.UNLINKS, context) is not None
        props['in_origins'] = self.ORIGINS
        props['in_origins_enabled'] = self.parameterAsVectorLayer(parameters, self.ORIGINS, context) is not None
        props['calc_count'] = self.parameterAsBool(parameters, self.CALC_COUNT, context)
        props['calc_length'] = self.parameterAsBool(parameters, self.CALC_LENGTH, context)
        props['calc_area'] = self.parameterAsBool(parameters, self.CALC_AREA, context)
        props['area_unit'] = self._AREA_UNITS[self.parameterAsEnum(parameters, self.AREA_UNIT, context)][1]
        props['rad_straight'] = self.parameterAsDouble(parameters, self.RADIUS_STRAIGHT, context)
        props['rad_straight_enabled'] = bool(props['rad_straight'])
        props['rad_walking'] = self.parameterAsDouble(parameters, self.RADIUS_WALKING, context)
        props['rad_walking_enabled'] = bool(props['rad_walking'])
        props['rad_steps'] = self.parameterAsInt(parameters, self.RADIUS_STEPS, context)
        props['rad_steps_enabled'] = bool(props['rad_steps'])
        props['rad_angular'] = self.parameterAsDouble(parameters, self.RADIUS_ANGULAR, context)
        props['rad_angular_enabled'] = bool(props['rad_angular'])
        return props

    def checkParameterValues(self, parameters, context):
        props = self._collectProperties(parameters, context)
        if not props['calc_count'] and not props['calc_length'] and not props['calc_area']:
            return (False, 'Please select at least one reach output.')
        if not props['rad_straight_enabled'] and not props['rad_walking_enabled'] and not props['rad_steps_enabled'] and not props['rad_angular_enabled']:
            return (False, 'Please specify at least one radius.')
        return (True, None)

    def processAlgorithm(self, parameters, context, feedback):
        return self._run_analysis(ReachAnalysis, parameters, context, feedback)

    def name(self):
        return 'reach'

    def displayName(self):
        return self.tr('Reach')

    def createInstance(self):
        return ReachAlgorithm()


class NetworkIntegrationAlgorithm(PstProcessingAlgorithmBase):
    NETWORK = 'NETWORK'
    UNLINKS = 'UNLINKS'
    RADIUS_STEPS = 'RADIUS_STEPS'
    OUTPUT_N = 'OUTPUT_N'
    OUTPUT_TD = 'OUTPUT_TD'
    OUTPUT_MD = 'OUTPUT_MD'
    OUTPUT_AT_JUNCTIONS = 'OUTPUT_AT_JUNCTIONS'

    def initAlgorithm(self, config):
        self.addParameter(QgsProcessingParameterVectorLayer(self.NETWORK, self.tr('Axial network'), types=[QgsProcessing.TypeVectorLine]))
        self.addParameter(QgsProcessingParameterFeatureSource(self.UNLINKS, self.tr('Unlinks'), types=[QgsProcessing.TypeVectorPoint], optional=True))
        self.addParameter(QgsProcessingParameterNumber(self.RADIUS_STEPS, self.tr('Steps radius'), optional=True, type=QgsProcessingParameterNumber.Integer))
        self.addParameter(QgsProcessingParameterBoolean(self.OUTPUT_N, self.tr('Output node count (N)'), defaultValue=True))
        self.addParameter(QgsProcessingParameterBoolean(self.OUTPUT_TD, self.tr('Output total depth (TD)'), defaultValue=True))
        self.addParameter(QgsProcessingParameterBoolean(self.OUTPUT_MD, self.tr('Output mean depth (MD)'), defaultValue=True))
        self.addParameter(QgsProcessingParameterBoolean(self.OUTPUT_AT_JUNCTIONS, self.tr('Store average score at junctions'), defaultValue=False))

    def _collectProperties(self, parameters, context):
        props = {}
        props['in_network'] = self.NETWORK
        props['in_unlinks'] = self.UNLINKS
        props['in_unlinks_enabled'] = self.parameterAsVectorLayer(parameters, self.UNLINKS, context) is not None
        props['rad_steps'] = self.parameterAsInt(parameters, self.RADIUS_STEPS, context)
        props['rad_steps_enabled'] = bool(props['rad_steps'])
        props['output_N'] = self.parameterAsBool(parameters, self.OUTPUT_N, context)
        props['output_TD'] = self.parameterAsBool(parameters, self.OUTPUT_TD, context)
        props['output_MD'] = self.parameterAsBool(parameters, self.OUTPUT_MD, context)
        props['output_at_junctions'] = self.parameterAsBool(parameters, self.OUTPUT_AT_JUNCTIONS, context)
        return props

    def checkParameterValues(self, parameters, context):
        props = self._collectProperties(parameters, context)
        if not props['rad_steps_enabled']:
            return (False, 'Please specify a steps radius.')
        return (True, None)

    def processAlgorithm(self, parameters, context, feedback):
        return self._run_analysis(NetworkIntegrationAnalysis, parameters, context, feedback)

    def name(self):
        return 'networkintegration'

    def displayName(self):
        return self.tr('Network Integration')

    def createInstance(self):
        return NetworkIntegrationAlgorithm()


class NetworkBetweennessAlgorithm(PstProcessingAlgorithmBase):
    NETWORK = 'NETWORK'
    UNLINKS = 'UNLINKS'
    DIST_WALKING = 'DIST_WALKING'
    DIST_STEPS = 'DIST_STEPS'
    DIST_AXMETER = 'DIST_AXMETER'
    WEIGHT_NONE = 'WEIGHT_NONE'
    WEIGHT_LENGTH = 'WEIGHT_LENGTH'
    WEIGHT_DATA = 'WEIGHT_DATA'
    WEIGHT_DATA_COLS = 'WEIGHT_DATA_COLS'
    WEIGHT_DATA_NAME = 'WEIGHT_DATA_NAME'
    NORM_NONE = 'NORM_NONE'
    NORM_STANDARD = 'NORM_STANDARD'
    RADIUS_STRAIGHT = 'RADIUS_STRAIGHT'
    RADIUS_WALKING = 'RADIUS_WALKING'
    RADIUS_STEPS = 'RADIUS_STEPS'
    RADIUS_ANGULAR = 'RADIUS_ANGULAR'
    OUTPUT_N = 'OUTPUT_N'
    OUTPUT_TD = 'OUTPUT_TD'
    OUTPUT_MD = 'OUTPUT_MD'

    def initAlgorithm(self, config):
        self.addParameter(QgsProcessingParameterVectorLayer(self.NETWORK, self.tr('Network'), types=[QgsProcessing.TypeVectorLine]))
        self.addParameter(QgsProcessingParameterFeatureSource(self.UNLINKS, self.tr('Unlinks'), types=[QgsProcessing.TypeVectorPoint], optional=True))
        self.addParameter(QgsProcessingParameterBoolean(self.DIST_WALKING, self.tr('Walking distance (meters)'), defaultValue=True))
        self.addParameter(QgsProcessingParameterBoolean(self.DIST_STEPS, self.tr('Axial/segment lines (steps)'), defaultValue=False))
        self.addParameter(QgsProcessingParameterBoolean(self.DIST_AXMETER, self.tr('Axialmeter (steps*meters)'), defaultValue=False))
        self.addParameter(QgsProcessingParameterBoolean(self.WEIGHT_NONE, self.tr('No weight'), defaultValue=True))
        self.addParameter(QgsProcessingParameterBoolean(self.WEIGHT_LENGTH, self.tr('Weigh by segment length'), defaultValue=False))
        self.addParameter(QgsProcessingParameterBoolean(self.WEIGHT_DATA, self.tr('Weigh by segment data'), defaultValue=False))
        self.addParameter(QgsProcessingParameterField(self.WEIGHT_DATA_COLS, self.tr('Weight data columns'), parentLayerParameterName=self.NETWORK, allowMultiple=True, optional=True))
        self.addParameter(QgsProcessingParameterString(self.WEIGHT_DATA_NAME, self.tr('Data name (used in output column)'), optional=True))
        self.addParameter(QgsProcessingParameterBoolean(self.NORM_NONE, self.tr('No normalization'), defaultValue=True))
        self.addParameter(QgsProcessingParameterBoolean(self.NORM_STANDARD, self.tr('Standard normalization (0-1)'), defaultValue=False))
        self.addParameter(QgsProcessingParameterNumber(self.RADIUS_STRAIGHT, self.tr('Straight radius'), optional=True, type=QgsProcessingParameterNumber.Double))
        self.addParameter(QgsProcessingParameterNumber(self.RADIUS_WALKING, self.tr('Walking radius'), optional=True, type=QgsProcessingParameterNumber.Double))
        self.addParameter(QgsProcessingParameterNumber(self.RADIUS_STEPS, self.tr('Steps radius'), optional=True, type=QgsProcessingParameterNumber.Integer))
        self.addParameter(QgsProcessingParameterNumber(self.RADIUS_ANGULAR, self.tr('Angular radius'), optional=True, type=QgsProcessingParameterNumber.Double))
        self.addParameter(QgsProcessingParameterBoolean(self.OUTPUT_N, self.tr('Output node count (N)'), defaultValue=True))
        self.addParameter(QgsProcessingParameterBoolean(self.OUTPUT_TD, self.tr('Output total depth (TD)'), defaultValue=True))
        self.addParameter(QgsProcessingParameterBoolean(self.OUTPUT_MD, self.tr('Output mean depth (MD)'), defaultValue=True))

    def _collectProperties(self, parameters, context):
        props = {}
        props['in_network'] = self.NETWORK
        props['in_unlinks'] = self.UNLINKS
        props['in_unlinks_enabled'] = self.parameterAsVectorLayer(parameters, self.UNLINKS, context) is not None
        props['dist_walking'] = self.parameterAsBool(parameters, self.DIST_WALKING, context)
        props['dist_steps'] = self.parameterAsBool(parameters, self.DIST_STEPS, context)
        props['dist_axmeter'] = self.parameterAsBool(parameters, self.DIST_AXMETER, context)
        props['weight_none'] = self.parameterAsBool(parameters, self.WEIGHT_NONE, context)
        props['weight_length'] = self.parameterAsBool(parameters, self.WEIGHT_LENGTH, context)
        props['weight_data'] = self.parameterAsBool(parameters, self.WEIGHT_DATA, context)
        props['weight_data_cols'] = self.parameterAsFields(parameters, self.WEIGHT_DATA_COLS, context)
        props['weight_data_name'] = self.parameterAsString(parameters, self.WEIGHT_DATA_NAME, context)
        props['norm_none'] = self.parameterAsBool(parameters, self.NORM_NONE, context)
        props['norm_standard'] = self.parameterAsBool(parameters, self.NORM_STANDARD, context)
        props['rad_straight'] = self.parameterAsDouble(parameters, self.RADIUS_STRAIGHT, context)
        props['rad_straight_enabled'] = bool(props['rad_straight'])
        props['rad_walking'] = self.parameterAsDouble(parameters, self.RADIUS_WALKING, context)
        props['rad_walking_enabled'] = bool(props['rad_walking'])
        props['rad_steps'] = self.parameterAsInt(parameters, self.RADIUS_STEPS, context)
        props['rad_steps_enabled'] = bool(props['rad_steps'])
        props['rad_angular'] = self.parameterAsDouble(parameters, self.RADIUS_ANGULAR, context)
        props['rad_angular_enabled'] = bool(props['rad_angular'])
        props['output_N'] = self.parameterAsBool(parameters, self.OUTPUT_N, context)
        props['output_TD'] = self.parameterAsBool(parameters, self.OUTPUT_TD, context)
        props['output_MD'] = self.parameterAsBool(parameters, self.OUTPUT_MD, context)
        return props

    def checkParameterValues(self, parameters, context):
        props = self._collectProperties(parameters, context)
        if not props['dist_walking'] and not props['dist_steps'] and not props['dist_axmeter']:
            return (False, 'Please select at least one distance mode.')
        if not props['norm_none'] and not props['norm_standard']:
            return (False, 'Please select at least one normalization mode.')
        if not props['weight_none'] and not props['weight_length'] and not props['weight_data']:
            return (False, 'Please select at least one weight mode.')
        if props['weight_data'] and not props['weight_data_cols']:
            return (False, 'Please select at least one weight data column.')
        if props['weight_data'] and not props['weight_data_name']:
            return (False, 'Please enter a data name for the weighted output columns.')
        if not props['rad_straight_enabled'] and not props['rad_walking_enabled'] and not props['rad_steps_enabled'] and not props['rad_angular_enabled']:
            return (False, 'Please specify at least one radius.')
        return (True, None)

    def processAlgorithm(self, parameters, context, feedback):
        return self._run_analysis(NetworkBetweennessAnalysis, parameters, context, feedback)

    def name(self):
        return 'networkbetweenness'

    def displayName(self):
        return self.tr('Network Betweenness')

    def createInstance(self):
        return NetworkBetweennessAlgorithm()


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
        return self._run_analysis(CreateSegmentMapAnalysis, parameters, context, feedback)

    def name(self):
        return 'createsegmentmap'

    def displayName(self):
        return self.tr('Create Segment Map')

    def createInstance(self):
        return CreateSegmentMapAlgorithm()
