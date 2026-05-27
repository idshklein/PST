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
    AngularBetweennessAnalysis,
    AttractionBetweennessAnalysis,
    AttractionDistanceAnalysis,
    AttractionReachAnalysis,
    SegmentGroupingAnalysis,
    SegmentGroupIntegrationAnalysis,
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


# ---------------------------------------------------------------------------
# Angular Betweenness
# ---------------------------------------------------------------------------

class AngularBetweennessAlgorithm(PstProcessingAlgorithmBase):
    NETWORK = 'NETWORK'
    WEIGHT_NONE = 'WEIGHT_NONE'
    WEIGHT_LENGTH = 'WEIGHT_LENGTH'
    NORM_NONE = 'NORM_NONE'
    NORM_NORMALIZATION = 'NORM_NORMALIZATION'
    NORM_STANDARD = 'NORM_STANDARD'
    NORM_SYNTAX = 'NORM_SYNTAX'
    RADIUS_WALKING = 'RADIUS_WALKING'
    OUTPUT_N = 'OUTPUT_N'
    OUTPUT_TD = 'OUTPUT_TD'
    OUTPUT_MD = 'OUTPUT_MD'

    def initAlgorithm(self, config):
        self.addParameter(QgsProcessingParameterVectorLayer(
            self.NETWORK, self.tr('Segment network'),
            types=[QgsProcessing.TypeVectorLine]))
        self.addParameter(QgsProcessingParameterBoolean(
            self.WEIGHT_NONE, self.tr('No weight'), defaultValue=True))
        self.addParameter(QgsProcessingParameterBoolean(
            self.WEIGHT_LENGTH, self.tr('Weigh by segment length'), defaultValue=False))
        self.addParameter(QgsProcessingParameterBoolean(
            self.NORM_NONE, self.tr('No normalization'), defaultValue=True))
        self.addParameter(QgsProcessingParameterBoolean(
            self.NORM_NORMALIZATION, self.tr('Normalization (Turner 2007)'), defaultValue=False))
        self.addParameter(QgsProcessingParameterBoolean(
            self.NORM_STANDARD, self.tr('Standard normalization (0-1)'), defaultValue=False))
        self.addParameter(QgsProcessingParameterBoolean(
            self.NORM_SYNTAX, self.tr('Syntax normalization (NACH)'), defaultValue=False))
        self.addParameter(QgsProcessingParameterNumber(
            self.RADIUS_WALKING, self.tr('Walking radius (meters)'),
            optional=True, type=QgsProcessingParameterNumber.Double))
        self.addParameter(QgsProcessingParameterBoolean(
            self.OUTPUT_N, self.tr('Output node count (N)'), defaultValue=False))
        self.addParameter(QgsProcessingParameterBoolean(
            self.OUTPUT_TD, self.tr('Output total depth (TD)'), defaultValue=False))
        self.addParameter(QgsProcessingParameterBoolean(
            self.OUTPUT_MD, self.tr('Output mean depth (MD)'), defaultValue=False))

    def _collectProperties(self, parameters, context):
        props = {}
        props['in_network'] = self.NETWORK
        props['weight_none'] = self.parameterAsBool(parameters, self.WEIGHT_NONE, context)
        props['weight_length'] = self.parameterAsBool(parameters, self.WEIGHT_LENGTH, context)
        props['norm_none'] = self.parameterAsBool(parameters, self.NORM_NONE, context)
        props['norm_normalization'] = self.parameterAsBool(parameters, self.NORM_NORMALIZATION, context)
        props['norm_standard'] = self.parameterAsBool(parameters, self.NORM_STANDARD, context)
        props['norm_syntax'] = self.parameterAsBool(parameters, self.NORM_SYNTAX, context)
        props['rad_walking'] = self.parameterAsDouble(parameters, self.RADIUS_WALKING, context)
        props['rad_walking_enabled'] = bool(props['rad_walking'])
        props['rad_straight'] = 0
        props['rad_straight_enabled'] = False
        props['rad_steps'] = 0
        props['rad_steps_enabled'] = False
        props['rad_angular'] = 0
        props['rad_angular_enabled'] = False
        props['rad_axmeter'] = 0
        props['rad_axmeter_enabled'] = False
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
        if not self.parameterAsDouble(parameters, self.RADIUS_WALKING, context):
            return (False, 'Please specify a walking radius.')
        return (True, None)

    def processAlgorithm(self, parameters, context, feedback):
        return self._run_analysis(AngularBetweennessAnalysis, parameters, context, feedback)

    def name(self):
        return 'angularbetweenness'

    def displayName(self):
        return self.tr('Angular Betweenness')

    def createInstance(self):
        return AngularBetweennessAlgorithm()


# ---------------------------------------------------------------------------
# Segment Grouping
# ---------------------------------------------------------------------------

class SegmentGroupingAlgorithm(PstProcessingAlgorithmBase):
    NETWORK = 'NETWORK'
    ANGLE_THRESHOLD = 'ANGLE_THRESHOLD'
    SPLIT_AT_JUNCTIONS = 'SPLIT_AT_JUNCTIONS'
    GENERATE_COLORS = 'GENERATE_COLORS'

    def initAlgorithm(self, config):
        self.addParameter(QgsProcessingParameterVectorLayer(
            self.NETWORK, self.tr('Segment network'),
            types=[QgsProcessing.TypeVectorLine]))
        self.addParameter(QgsProcessingParameterNumber(
            self.ANGLE_THRESHOLD, self.tr('Angle threshold (degrees)'),
            type=QgsProcessingParameterNumber.Double,
            defaultValue=1, minValue=0))
        self.addParameter(QgsProcessingParameterBoolean(
            self.SPLIT_AT_JUNCTIONS, self.tr('Split at junctions'), defaultValue=False))
        self.addParameter(QgsProcessingParameterBoolean(
            self.GENERATE_COLORS, self.tr('Generate minimal disjunct colors'), defaultValue=False))

    def _collectProperties(self, parameters, context):
        props = {}
        props['in_network'] = self.NETWORK
        props['angle_threshold'] = self.parameterAsDouble(parameters, self.ANGLE_THRESHOLD, context)
        props['split_at_junctions'] = self.parameterAsBool(parameters, self.SPLIT_AT_JUNCTIONS, context)
        props['generate_colors'] = self.parameterAsBool(parameters, self.GENERATE_COLORS, context)
        # apply_colors requires a live map canvas – not available in batch Processing
        props['apply_colors'] = False
        return props

    def processAlgorithm(self, parameters, context, feedback):
        return self._run_analysis(SegmentGroupingAnalysis, parameters, context, feedback)

    def name(self):
        return 'segmentgrouping'

    def displayName(self):
        return self.tr('Segment Grouping')

    def createInstance(self):
        return SegmentGroupingAlgorithm()


# ---------------------------------------------------------------------------
# Segment Group Integration
# ---------------------------------------------------------------------------

class SegmentGroupIntegrationAlgorithm(PstProcessingAlgorithmBase):
    NETWORK = 'NETWORK'
    ANGLE_THRESHOLD = 'ANGLE_THRESHOLD'
    SPLIT_AT_JUNCTIONS = 'SPLIT_AT_JUNCTIONS'
    RADIUS_WALKING = 'RADIUS_WALKING'
    RADIUS_STEPS = 'RADIUS_STEPS'
    OUTPUT_N = 'OUTPUT_N'
    OUTPUT_TD = 'OUTPUT_TD'
    OUTPUT_MD = 'OUTPUT_MD'

    def initAlgorithm(self, config):
        self.addParameter(QgsProcessingParameterVectorLayer(
            self.NETWORK, self.tr('Segment network'),
            types=[QgsProcessing.TypeVectorLine]))
        self.addParameter(QgsProcessingParameterNumber(
            self.ANGLE_THRESHOLD, self.tr('Angle threshold (degrees)'),
            type=QgsProcessingParameterNumber.Double,
            defaultValue=1, minValue=0))
        self.addParameter(QgsProcessingParameterBoolean(
            self.SPLIT_AT_JUNCTIONS, self.tr('Split at junctions'), defaultValue=False))
        self.addParameter(QgsProcessingParameterNumber(
            self.RADIUS_WALKING, self.tr('Walking radius (meters)'),
            optional=True, type=QgsProcessingParameterNumber.Double))
        self.addParameter(QgsProcessingParameterNumber(
            self.RADIUS_STEPS, self.tr('Steps radius'),
            optional=True, type=QgsProcessingParameterNumber.Integer))
        self.addParameter(QgsProcessingParameterBoolean(
            self.OUTPUT_N, self.tr('Output node count (N)'), defaultValue=True))
        self.addParameter(QgsProcessingParameterBoolean(
            self.OUTPUT_TD, self.tr('Output total depth (TD)'), defaultValue=True))
        self.addParameter(QgsProcessingParameterBoolean(
            self.OUTPUT_MD, self.tr('Output mean depth (MD)'), defaultValue=True))

    def _collectProperties(self, parameters, context):
        props = {}
        props['in_network'] = self.NETWORK
        props['angle_threshold'] = self.parameterAsDouble(parameters, self.ANGLE_THRESHOLD, context)
        props['split_at_junctions'] = self.parameterAsBool(parameters, self.SPLIT_AT_JUNCTIONS, context)
        props['rad_walking'] = self.parameterAsDouble(parameters, self.RADIUS_WALKING, context)
        props['rad_walking_enabled'] = bool(props['rad_walking'])
        props['rad_steps'] = self.parameterAsInt(parameters, self.RADIUS_STEPS, context)
        props['rad_steps_enabled'] = bool(props['rad_steps'])
        props['rad_straight'] = 0
        props['rad_straight_enabled'] = False
        props['rad_angular'] = 0
        props['rad_angular_enabled'] = False
        props['rad_axmeter'] = 0
        props['rad_axmeter_enabled'] = False
        props['output_N'] = self.parameterAsBool(parameters, self.OUTPUT_N, context)
        props['output_TD'] = self.parameterAsBool(parameters, self.OUTPUT_TD, context)
        props['output_MD'] = self.parameterAsBool(parameters, self.OUTPUT_MD, context)
        return props

    def checkParameterValues(self, parameters, context):
        props = self._collectProperties(parameters, context)
        if not props['rad_walking_enabled'] and not props['rad_steps_enabled']:
            return (False, 'Please specify at least one radius (walking or steps).')
        return (True, None)

    def processAlgorithm(self, parameters, context, feedback):
        return self._run_analysis(SegmentGroupIntegrationAnalysis, parameters, context, feedback)

    def name(self):
        return 'segmentgroupintegration'

    def displayName(self):
        return self.tr('Segment Group Integration')

    def createInstance(self):
        return SegmentGroupIntegrationAlgorithm()


# ---------------------------------------------------------------------------
# Shared helpers for Attraction analyses
# ---------------------------------------------------------------------------

def _collect_attraction_base_props(alg, parameters, context,
                                   network_param, unlinks_param,
                                   destinations_param):
    """Collect the common props shared by all three Attraction analyses."""
    props = {}
    props['in_network'] = network_param
    props['in_unlinks'] = unlinks_param
    props['in_unlinks_enabled'] = (
        alg.parameterAsVectorLayer(parameters, unlinks_param, context) is not None)
    # Origin type is always 'lines' in the simplified Processing wrapper.
    # Results are written back to the network layer.
    props['in_origin_type'] = 'lines'
    props['in_origin_points'] = ''
    props['origin_is_regions'] = False
    props['origin_poly_edge_point_interval_enabled'] = False
    props['origin_poly_edge_point_interval'] = 0
    props['in_destinations'] = destinations_param
    props['dest_is_regions'] = False
    props['dest_poly_edge_point_interval_enabled'] = False
    props['dest_poly_edge_point_interval'] = 0
    # Disable attribute-copy feature
    props['dst_attr_to_org_enabled'] = False
    props['dst_attr_to_org_in_column'] = ''
    props['dst_attr_to_org_out_column_suffix'] = ''
    return props


def _collect_radii_props(alg, parameters, context,
                         straight_param=None, walking_param=None,
                         steps_param=None, angular_param=None,
                         axmeter_param=None):
    """Collect radius props from optional radius parameters."""
    props = {}
    props['rad_straight'] = alg.parameterAsDouble(parameters, straight_param, context) if straight_param else 0
    props['rad_straight_enabled'] = bool(props['rad_straight'])
    props['rad_walking'] = alg.parameterAsDouble(parameters, walking_param, context) if walking_param else 0
    props['rad_walking_enabled'] = bool(props['rad_walking'])
    props['rad_steps'] = alg.parameterAsInt(parameters, steps_param, context) if steps_param else 0
    props['rad_steps_enabled'] = bool(props['rad_steps'])
    props['rad_angular'] = alg.parameterAsDouble(parameters, angular_param, context) if angular_param else 0
    props['rad_angular_enabled'] = bool(props['rad_angular'])
    props['rad_axmeter'] = alg.parameterAsDouble(parameters, axmeter_param, context) if axmeter_param else 0
    props['rad_axmeter_enabled'] = bool(props['rad_axmeter'])
    return props


# ---------------------------------------------------------------------------
# Attraction Distance
# ---------------------------------------------------------------------------

class AttractionDistanceAlgorithm(PstProcessingAlgorithmBase):
    NETWORK = 'NETWORK'
    UNLINKS = 'UNLINKS'
    DESTINATIONS = 'DESTINATIONS'
    DEST_NAME = 'DEST_NAME'
    DEST_DATA_ENABLED = 'DEST_DATA_ENABLED'
    DEST_DATA = 'DEST_DATA'
    DIST_WALKING = 'DIST_WALKING'
    DIST_STEPS = 'DIST_STEPS'
    DIST_ANGULAR = 'DIST_ANGULAR'
    DIST_AXMETER = 'DIST_AXMETER'
    RADIUS_STRAIGHT = 'RADIUS_STRAIGHT'
    RADIUS_WALKING = 'RADIUS_WALKING'
    RADIUS_STEPS = 'RADIUS_STEPS'
    RADIUS_ANGULAR = 'RADIUS_ANGULAR'

    def initAlgorithm(self, config):
        self.addParameter(QgsProcessingParameterVectorLayer(
            self.NETWORK, self.tr('Network'),
            types=[QgsProcessing.TypeVectorLine]))
        self.addParameter(QgsProcessingParameterFeatureSource(
            self.UNLINKS, self.tr('Unlinks'),
            types=[QgsProcessing.TypeVectorPoint], optional=True))
        self.addParameter(QgsProcessingParameterVectorLayer(
            self.DESTINATIONS, self.tr('Destinations'),
            types=[QgsProcessing.TypeVectorPoint]))
        self.addParameter(QgsProcessingParameterString(
            self.DEST_NAME,
            self.tr('Destination name for output column (max 2 characters)'),
            optional=True))
        self.addParameter(QgsProcessingParameterBoolean(
            self.DEST_DATA_ENABLED,
            self.tr('Weight destinations by data column'),
            defaultValue=False))
        self.addParameter(QgsProcessingParameterField(
            self.DEST_DATA,
            self.tr('Destination weight column'),
            parentLayerParameterName=self.DESTINATIONS,
            optional=True))
        self.addParameter(QgsProcessingParameterBoolean(
            self.DIST_WALKING, self.tr('Walking distance (meters)'), defaultValue=True))
        self.addParameter(QgsProcessingParameterBoolean(
            self.DIST_STEPS, self.tr('Axial/segment lines (steps)'), defaultValue=False))
        self.addParameter(QgsProcessingParameterBoolean(
            self.DIST_ANGULAR, self.tr('Angle (degrees)'), defaultValue=False))
        self.addParameter(QgsProcessingParameterBoolean(
            self.DIST_AXMETER, self.tr('Axialmeter (steps*meters)'), defaultValue=False))
        self.addParameter(QgsProcessingParameterNumber(
            self.RADIUS_STRAIGHT, self.tr('Straight radius'),
            optional=True, type=QgsProcessingParameterNumber.Double))
        self.addParameter(QgsProcessingParameterNumber(
            self.RADIUS_WALKING, self.tr('Walking radius'),
            optional=True, type=QgsProcessingParameterNumber.Double))
        self.addParameter(QgsProcessingParameterNumber(
            self.RADIUS_STEPS, self.tr('Steps radius'),
            optional=True, type=QgsProcessingParameterNumber.Integer))
        self.addParameter(QgsProcessingParameterNumber(
            self.RADIUS_ANGULAR, self.tr('Angular radius'),
            optional=True, type=QgsProcessingParameterNumber.Double))

    def _collectProperties(self, parameters, context):
        props = _collect_attraction_base_props(
            self, parameters, context,
            self.NETWORK, self.UNLINKS, self.DESTINATIONS)
        dest_data_enabled = self.parameterAsBool(parameters, self.DEST_DATA_ENABLED, context)
        dest_data_field = self.parameterAsString(parameters, self.DEST_DATA, context)
        props['dest_data_enabled'] = dest_data_enabled and bool(dest_data_field)
        props['dest_data'] = [dest_data_field] if props['dest_data_enabled'] else []
        props['dest_name'] = self.parameterAsString(parameters, self.DEST_NAME, context)[:2]
        props['dist_straight'] = False
        props['dist_walking'] = self.parameterAsBool(parameters, self.DIST_WALKING, context)
        props['dist_steps'] = self.parameterAsBool(parameters, self.DIST_STEPS, context)
        props['dist_angular'] = self.parameterAsBool(parameters, self.DIST_ANGULAR, context)
        props['dist_axmeter'] = self.parameterAsBool(parameters, self.DIST_AXMETER, context)
        props['dist_weights'] = False
        props['dw_attribute'] = ''
        props['point_connection_weight'] = 0
        props.update(_collect_radii_props(
            self, parameters, context,
            straight_param=self.RADIUS_STRAIGHT,
            walking_param=self.RADIUS_WALKING,
            steps_param=self.RADIUS_STEPS,
            angular_param=self.RADIUS_ANGULAR))
        return props

    def checkParameterValues(self, parameters, context):
        if (not self.parameterAsBool(parameters, self.DIST_WALKING, context)
                and not self.parameterAsBool(parameters, self.DIST_STEPS, context)
                and not self.parameterAsBool(parameters, self.DIST_ANGULAR, context)
                and not self.parameterAsBool(parameters, self.DIST_AXMETER, context)):
            return (False, 'Please select at least one distance mode.')
        props = self._collectProperties(parameters, context)
        if (not props['rad_straight_enabled'] and not props['rad_walking_enabled']
                and not props['rad_steps_enabled'] and not props['rad_angular_enabled']):
            return (False, 'Please specify at least one radius.')
        if (props['dest_data_enabled']
                and not self.parameterAsString(parameters, self.DEST_DATA, context)):
            return (False, 'Please select a destination weight column, or disable weighting.')
        return (True, None)

    def processAlgorithm(self, parameters, context, feedback):
        return self._run_analysis(AttractionDistanceAnalysis, parameters, context, feedback)

    def name(self):
        return 'attractiondistance'

    def displayName(self):
        return self.tr('Attraction Distance')

    def createInstance(self):
        return AttractionDistanceAlgorithm()


# ---------------------------------------------------------------------------
# Attraction Reach
# ---------------------------------------------------------------------------

class AttractionReachAlgorithm(PstProcessingAlgorithmBase):
    NETWORK = 'NETWORK'
    UNLINKS = 'UNLINKS'
    DESTINATIONS = 'DESTINATIONS'
    DEST_NAME = 'DEST_NAME'
    DEST_DATA_ENABLED = 'DEST_DATA_ENABLED'
    DEST_DATA = 'DEST_DATA'
    DISTRIBUTION_FUNC = 'DISTRIBUTION_FUNC'
    COLLECTION_FUNC = 'COLLECTION_FUNC'
    RADIUS_STRAIGHT = 'RADIUS_STRAIGHT'
    RADIUS_WALKING = 'RADIUS_WALKING'
    RADIUS_STEPS = 'RADIUS_STEPS'
    RADIUS_ANGULAR = 'RADIUS_ANGULAR'
    RADIUS_AXMETER = 'RADIUS_AXMETER'

    _DIST_FUNCS = [('Copy', 'copy'), ('Divide', 'divide')]
    _COLL_FUNCS = [('Average', 'avarage'), ('Sum', 'sum'), ('Min', 'min'), ('Max', 'max')]

    def initAlgorithm(self, config):
        self.addParameter(QgsProcessingParameterVectorLayer(
            self.NETWORK, self.tr('Network'),
            types=[QgsProcessing.TypeVectorLine]))
        self.addParameter(QgsProcessingParameterFeatureSource(
            self.UNLINKS, self.tr('Unlinks'),
            types=[QgsProcessing.TypeVectorPoint], optional=True))
        self.addParameter(QgsProcessingParameterVectorLayer(
            self.DESTINATIONS, self.tr('Destinations'),
            types=[QgsProcessing.TypeVectorPoint]))
        self.addParameter(QgsProcessingParameterString(
            self.DEST_NAME,
            self.tr('Destination name for output column (max 2 characters)'),
            optional=True))
        self.addParameter(QgsProcessingParameterBoolean(
            self.DEST_DATA_ENABLED,
            self.tr('Weight destinations by data column'),
            defaultValue=False))
        self.addParameter(QgsProcessingParameterField(
            self.DEST_DATA,
            self.tr('Destination weight column'),
            parentLayerParameterName=self.DESTINATIONS,
            optional=True))
        self.addParameter(QgsProcessingParameterEnum(
            self.DISTRIBUTION_FUNC,
            self.tr('Attraction distribution function'),
            options=[e[0] for e in self._DIST_FUNCS],
            defaultValue=0))
        self.addParameter(QgsProcessingParameterEnum(
            self.COLLECTION_FUNC,
            self.tr('Attraction collection function'),
            options=[e[0] for e in self._COLL_FUNCS],
            defaultValue=0))
        self.addParameter(QgsProcessingParameterNumber(
            self.RADIUS_STRAIGHT, self.tr('Straight radius'),
            optional=True, type=QgsProcessingParameterNumber.Double))
        self.addParameter(QgsProcessingParameterNumber(
            self.RADIUS_WALKING, self.tr('Walking radius'),
            optional=True, type=QgsProcessingParameterNumber.Double))
        self.addParameter(QgsProcessingParameterNumber(
            self.RADIUS_STEPS, self.tr('Steps radius'),
            optional=True, type=QgsProcessingParameterNumber.Integer))
        self.addParameter(QgsProcessingParameterNumber(
            self.RADIUS_ANGULAR, self.tr('Angular radius'),
            optional=True, type=QgsProcessingParameterNumber.Double))
        self.addParameter(QgsProcessingParameterNumber(
            self.RADIUS_AXMETER, self.tr('Axialmeter radius'),
            optional=True, type=QgsProcessingParameterNumber.Double))

    def _collectProperties(self, parameters, context):
        props = _collect_attraction_base_props(
            self, parameters, context,
            self.NETWORK, self.UNLINKS, self.DESTINATIONS)
        dest_data_enabled = self.parameterAsBool(parameters, self.DEST_DATA_ENABLED, context)
        dest_data_field = self.parameterAsString(parameters, self.DEST_DATA, context)
        props['dest_data_enabled'] = dest_data_enabled and bool(dest_data_field)
        props['dest_data'] = [dest_data_field] if props['dest_data_enabled'] else []
        props['dest_name'] = self.parameterAsString(parameters, self.DEST_NAME, context)[:2]
        props['dest_distribution_function'] = self._DIST_FUNCS[
            self.parameterAsEnum(parameters, self.DISTRIBUTION_FUNC, context)][1]
        props['origin_collection_function'] = self._COLL_FUNCS[
            self.parameterAsEnum(parameters, self.COLLECTION_FUNC, context)][1]
        # Use non-weight mode (DistanceType.UNDEFINED with standard radii)
        props['weight_enabled'] = False
        props['weight_func'] = 'pow'
        props['weight_func_constant'] = 1
        # distance_modes not used when weight_enabled=False; disable all
        for key in ('dist_straight_enabled', 'dist_walking_enabled', 'dist_steps_enabled',
                    'dist_angular_enabled', 'dist_axmeter_enabled'):
            props[key] = False
        props.update(_collect_radii_props(
            self, parameters, context,
            straight_param=self.RADIUS_STRAIGHT,
            walking_param=self.RADIUS_WALKING,
            steps_param=self.RADIUS_STEPS,
            angular_param=self.RADIUS_ANGULAR,
            axmeter_param=self.RADIUS_AXMETER))
        return props

    def checkParameterValues(self, parameters, context):
        props = self._collectProperties(parameters, context)
        if (not props['rad_straight_enabled'] and not props['rad_walking_enabled']
                and not props['rad_steps_enabled'] and not props['rad_angular_enabled']
                and not props['rad_axmeter_enabled']):
            return (False, 'Please specify at least one radius.')
        if (props['dest_data_enabled']
                and not self.parameterAsString(parameters, self.DEST_DATA, context)):
            return (False, 'Please select a destination weight column, or disable weighting.')
        return (True, None)

    def processAlgorithm(self, parameters, context, feedback):
        return self._run_analysis(AttractionReachAnalysis, parameters, context, feedback)

    def name(self):
        return 'attractionreach'

    def displayName(self):
        return self.tr('Attraction Reach')

    def createInstance(self):
        return AttractionReachAlgorithm()


# ---------------------------------------------------------------------------
# Attraction Betweenness
# ---------------------------------------------------------------------------

class AttractionBetweennessAlgorithm(PstProcessingAlgorithmBase):
    NETWORK = 'NETWORK'
    UNLINKS = 'UNLINKS'
    DESTINATIONS = 'DESTINATIONS'
    DEST_NAME = 'DEST_NAME'
    DEST_DATA_ENABLED = 'DEST_DATA_ENABLED'
    DEST_DATA = 'DEST_DATA'
    DIST_WALKING = 'DIST_WALKING'
    DIST_STEPS = 'DIST_STEPS'
    DIST_ANGULAR = 'DIST_ANGULAR'
    DIST_AXMETER = 'DIST_AXMETER'
    NORM_NONE = 'NORM_NONE'
    NORM_STANDARD = 'NORM_STANDARD'
    RADIUS_STRAIGHT = 'RADIUS_STRAIGHT'
    RADIUS_WALKING = 'RADIUS_WALKING'
    RADIUS_STEPS = 'RADIUS_STEPS'
    RADIUS_ANGULAR = 'RADIUS_ANGULAR'

    def initAlgorithm(self, config):
        self.addParameter(QgsProcessingParameterVectorLayer(
            self.NETWORK, self.tr('Network'),
            types=[QgsProcessing.TypeVectorLine]))
        self.addParameter(QgsProcessingParameterFeatureSource(
            self.UNLINKS, self.tr('Unlinks'),
            types=[QgsProcessing.TypeVectorPoint], optional=True))
        self.addParameter(QgsProcessingParameterVectorLayer(
            self.DESTINATIONS, self.tr('Destinations'),
            types=[QgsProcessing.TypeVectorPoint]))
        self.addParameter(QgsProcessingParameterString(
            self.DEST_NAME,
            self.tr('Destination name for output column (max 2 characters)'),
            optional=True))
        self.addParameter(QgsProcessingParameterBoolean(
            self.DEST_DATA_ENABLED,
            self.tr('Weight destinations by data column'),
            defaultValue=False))
        self.addParameter(QgsProcessingParameterField(
            self.DEST_DATA,
            self.tr('Destination weight column'),
            parentLayerParameterName=self.DESTINATIONS,
            optional=True))
        self.addParameter(QgsProcessingParameterBoolean(
            self.DIST_WALKING, self.tr('Walking distance (meters)'), defaultValue=True))
        self.addParameter(QgsProcessingParameterBoolean(
            self.DIST_STEPS, self.tr('Axial/segment lines (steps)'), defaultValue=False))
        self.addParameter(QgsProcessingParameterBoolean(
            self.DIST_ANGULAR, self.tr('Angle (degrees)'), defaultValue=False))
        self.addParameter(QgsProcessingParameterBoolean(
            self.DIST_AXMETER, self.tr('Axialmeter (steps*meters)'), defaultValue=False))
        self.addParameter(QgsProcessingParameterBoolean(
            self.NORM_NONE, self.tr('No normalization'), defaultValue=True))
        self.addParameter(QgsProcessingParameterBoolean(
            self.NORM_STANDARD, self.tr('Standard normalization (0-1)'), defaultValue=False))
        self.addParameter(QgsProcessingParameterNumber(
            self.RADIUS_STRAIGHT, self.tr('Straight radius'),
            optional=True, type=QgsProcessingParameterNumber.Double))
        self.addParameter(QgsProcessingParameterNumber(
            self.RADIUS_WALKING, self.tr('Walking radius'),
            optional=True, type=QgsProcessingParameterNumber.Double))
        self.addParameter(QgsProcessingParameterNumber(
            self.RADIUS_STEPS, self.tr('Steps radius'),
            optional=True, type=QgsProcessingParameterNumber.Integer))
        self.addParameter(QgsProcessingParameterNumber(
            self.RADIUS_ANGULAR, self.tr('Angular radius'),
            optional=True, type=QgsProcessingParameterNumber.Double))

    def _collectProperties(self, parameters, context):
        props = _collect_attraction_base_props(
            self, parameters, context,
            self.NETWORK, self.UNLINKS, self.DESTINATIONS)
        dest_data_enabled = self.parameterAsBool(parameters, self.DEST_DATA_ENABLED, context)
        dest_data_field = self.parameterAsString(parameters, self.DEST_DATA, context)
        props['dest_data_enabled'] = dest_data_enabled and bool(dest_data_field)
        props['dest_data'] = [dest_data_field] if props['dest_data_enabled'] else []
        props['dest_name'] = self.parameterAsString(parameters, self.DEST_NAME, context)[:2]
        props['dist_walking'] = self.parameterAsBool(parameters, self.DIST_WALKING, context)
        props['dist_steps'] = self.parameterAsBool(parameters, self.DIST_STEPS, context)
        props['dist_angular'] = self.parameterAsBool(parameters, self.DIST_ANGULAR, context)
        props['dist_axmeter'] = self.parameterAsBool(parameters, self.DIST_AXMETER, context)
        props['dist_straight'] = False
        props['norm_none'] = self.parameterAsBool(parameters, self.NORM_NONE, context)
        props['norm_standard'] = self.parameterAsBool(parameters, self.NORM_STANDARD, context)
        props.update(_collect_radii_props(
            self, parameters, context,
            straight_param=self.RADIUS_STRAIGHT,
            walking_param=self.RADIUS_WALKING,
            steps_param=self.RADIUS_STEPS,
            angular_param=self.RADIUS_ANGULAR))
        return props

    def checkParameterValues(self, parameters, context):
        if (not self.parameterAsBool(parameters, self.DIST_WALKING, context)
                and not self.parameterAsBool(parameters, self.DIST_STEPS, context)
                and not self.parameterAsBool(parameters, self.DIST_ANGULAR, context)
                and not self.parameterAsBool(parameters, self.DIST_AXMETER, context)):
            return (False, 'Please select at least one distance mode.')
        if (not self.parameterAsBool(parameters, self.NORM_NONE, context)
                and not self.parameterAsBool(parameters, self.NORM_STANDARD, context)):
            return (False, 'Please select at least one normalization mode.')
        props = self._collectProperties(parameters, context)
        if (not props['rad_straight_enabled'] and not props['rad_walking_enabled']
                and not props['rad_steps_enabled'] and not props['rad_angular_enabled']):
            return (False, 'Please specify at least one radius.')
        if (props['dest_data_enabled']
                and not self.parameterAsString(parameters, self.DEST_DATA, context)):
            return (False, 'Please select a destination weight column, or disable weighting.')
        return (True, None)

    def processAlgorithm(self, parameters, context, feedback):
        return self._run_analysis(AttractionBetweennessAnalysis, parameters, context, feedback)

    def name(self):
        return 'attractionbetweenness'

    def displayName(self):
        return self.tr('Attraction Betweenness')

    def createInstance(self):
        return AttractionBetweennessAlgorithm()
