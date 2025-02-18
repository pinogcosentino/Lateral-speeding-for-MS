# -*- coding: utf-8 -*-

"""
/***************************************************************************
 SeismicMicrozonation
                                 A QGIS plugin
 Lateral spreading for seismic microzonation
 Generated by Plugin Builder: http://g-sherman.github.io/Qgis-Plugin-Builder/
                              -------------------
        begin                : 2025-01-08
        copyright            : (C) 2025 by Giuseppe Cosentino
        email                : giuseppe.cosentino@cnr.it
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

__author__ = 'Giuseppe Cosentino'
__date__ = '2025-01-08'
__copyright__ = '(C) 2025 by Giuseppe Cosentino'

# This will get replaced with a git SHA1 when you do a git archive

__revision__ = '$Format:%H$'

from qgis.core import QgsProcessing
from qgis.core import QgsProcessingAlgorithm
from qgis.core import QgsProcessingMultiStepFeedback
from qgis.core import QgsProcessingParameterRasterLayer
from qgis.core import QgsProcessingParameterVectorLayer
from qgis.core import QgsProcessingParameterField
from qgis.core import QgsProcessingParameterFeatureSink
import processing


class SeismicMicrozonationAlgorithm(QgsProcessingAlgorithm):

    def initAlgorithm(self, config=None):
        self.addParameter(QgsProcessingParameterRasterLayer('digital_terrain_model_dtm', 'Digital Terrain Model (DTM)', defaultValue=None))
        self.addParameter(QgsProcessingParameterVectorLayer('layer_with_il_index', 'Layer with IL index', types=[QgsProcessing.TypeVectorPolygon], defaultValue=None))
        self.addParameter(QgsProcessingParameterField('il_index', 'IL index', type=QgsProcessingParameterField.Numeric, parentLayerParameterName='layer_with_il_index', allowMultiple=False, defaultValue=None))
        self.addParameter(QgsProcessingParameterFeatureSink('LowLateralSpreadingZ0', 'Low lateral spreading (Z0)', type=QgsProcessing.TypeVectorAnyGeometry, createByDefault=True, supportsAppend=True, defaultValue='TEMPORARY_OUTPUT'))
        self.addParameter(QgsProcessingParameterFeatureSink('RespectZonesRs', 'Respect zones (RS)', type=QgsProcessing.TypeVectorAnyGeometry, createByDefault=True, supportsAppend=True, defaultValue='TEMPORARY_OUTPUT'))
        self.addParameter(QgsProcessingParameterFeatureSink('SusceptibilityZonesSz', 'Susceptibility Zones (SZ)', type=QgsProcessing.TypeVectorAnyGeometry, createByDefault=True, supportsAppend=True, defaultValue='TEMPORARY_OUTPUT'))

    def processAlgorithm(self, parameters, context, model_feedback):
        # Use a multi-step feedback, so that individual child algorithm progress reports are adjusted for the
        # overall progress through the model
        feedback = QgsProcessingMultiStepFeedback(24, model_feedback)
        results = {}
        outputs = {}

        # Ritaglia raster con maschera
        alg_params = {
            'ALPHA_BAND': False,
            'CROP_TO_CUTLINE': True,
            'DATA_TYPE': 0,  # Usa Il Tipo Dati del Layer in Ingresso
            'EXTRA': '',
            'INPUT': parameters['digital_terrain_model_dtm'],
            'KEEP_RESOLUTION': False,
            'MASK': parameters['layer_with_il_index'],
            'MULTITHREADING': False,
            'NODATA': None,
            'OPTIONS': '',
            'SET_RESOLUTION': False,
            'SOURCE_CRS': 'ProjectCrs',
            'TARGET_CRS': 'ProjectCrs',
            'TARGET_EXTENT': parameters['layer_with_il_index'],
            'X_RESOLUTION': None,
            'Y_RESOLUTION': None,
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['RitagliaRasterConMaschera'] = processing.run('gdal:cliprasterbymasklayer', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(1)
        if feedback.isCanceled():
            return {}

        # Pendenza
        alg_params = {
            'AS_PERCENT': True,
            'BAND': 1,
            'COMPUTE_EDGES': False,
            'EXTRA': '',
            'INPUT': outputs['RitagliaRasterConMaschera']['OUTPUT'],
            'OPTIONS': '',
            'SCALE': 1,
            'ZEVENBERGEN': False,
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['Pendenza'] = processing.run('gdal:slope', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(2)
        if feedback.isCanceled():
            return {}

        # Poligonizzazione (da raster a vettore)
        alg_params = {
            'BAND': 1,
            'EIGHT_CONNECTEDNESS': False,
            'EXTRA': '',
            'FIELD': 'DN',
            'INPUT': outputs['Pendenza']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['PoligonizzazioneDaRasterAVettore'] = processing.run('gdal:polygonize', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(3)
        if feedback.isCanceled():
            return {}

        # Intersezione_01
        # prende gli attributi sia del raster che del vettore 
        alg_params = {
            'GRID_SIZE': None,
            'INPUT': outputs['PoligonizzazioneDaRasterAVettore']['OUTPUT'],
            'INPUT_FIELDS': [''],
            'OVERLAY': parameters['layer_with_il_index'],
            'OVERLAY_FIELDS': [''],
            'OVERLAY_FIELDS_PREFIX': '',
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['Intersezione_01'] = processing.run('native:intersection', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(4)
        if feedback.isCanceled():
            return {}

        # Rinomina campo Indice di liquefazione
        # Rinominato il campo ha i volore del Indice di liquefazione per poter fare l'estrazione degli oggetti (poichè salvando il modello in python le funzionalità di qgis delle espressioni non funzionano quando si deve fare l'intersezione )
        alg_params = {
            'FIELD': parameters['il_index'],
            'INPUT': outputs['Intersezione_01']['OUTPUT'],
            'NEW_NAME': 'Index',
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['RinominaCampoIndiceDiLiquefazione'] = processing.run('native:renametablefield', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(5)
        if feedback.isCanceled():
            return {}

        # SZ (0< IL<=2) and (5< slope <=15)
        alg_params = {
            'EXPRESSION': '("INDEX" > 0 AND "INDEX"<=2) and ("DN" > 5 AND "DN" <=15)',
            'INPUT': outputs['RinominaCampoIndiceDiLiquefazione']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['Sz0Il2And5Slope15'] = processing.run('native:extractbyexpression', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(6)
        if feedback.isCanceled():
            return {}

        # SZ (2< IL<=5) and (2< slope<=5)
        alg_params = {
            'EXPRESSION': '("INDEX" > 2 AND "INDEX"<=5) AND ("DN" > 2 AND "DN" <=5)',
            'INPUT': outputs['RinominaCampoIndiceDiLiquefazione']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['Sz2Il5And2Slope5'] = processing.run('native:extractbyexpression', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(7)
        if feedback.isCanceled():
            return {}

        # RZ (0< IL<=2) and (slope >15)
        alg_params = {
            'EXPRESSION': '("INDEX" > 0 AND "INDEX"<=2) \r\nAND ("DN" >15)',
            'INPUT': outputs['RinominaCampoIndiceDiLiquefazione']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['Rz0Il2AndSlope15'] = processing.run('native:extractbyexpression', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(8)
        if feedback.isCanceled():
            return {}

        # SZ (5< IL< =15) AND (2< slope <=5)
        alg_params = {
            'EXPRESSION': '("INDEX"> 5 AND "INDEX"<= 15) AND (2< "DN" <=5)',
            'INPUT': outputs['RinominaCampoIndiceDiLiquefazione']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['Sz5Il15And2Slope5'] = processing.run('native:extractbyexpression', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(9)
        if feedback.isCanceled():
            return {}

        # SZ0 (0<IL<=2) and (2< slope <=5)
        alg_params = {
            'EXPRESSION': '("INDEX" > 0 AND "INDEX"<=2) and ("DN" > 2 AND "DN" <=5)',
            'INPUT': outputs['RinominaCampoIndiceDiLiquefazione']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['Sz00il2And2Slope5'] = processing.run('native:extractbyexpression', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(10)
        if feedback.isCanceled():
            return {}

        # zs_merge
        alg_params = {
            'CRS': 'ProjectCrs',
            'LAYERS': [outputs['Sz5Il15And2Slope5']['OUTPUT'],outputs['Sz2Il5And2Slope5']['OUTPUT'],outputs['Sz0Il2And5Slope15']['OUTPUT']],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['Zs_merge'] = processing.run('native:mergevectorlayers', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(11)
        if feedback.isCanceled():
            return {}

        # RZ ("IL" >15) AND ("slope" > 2)
        # Estrazione tramite espressione 
        # I campi 'DN' = slope% 
        # 'Index'= Indice di liquefazione
        alg_params = {
            'EXPRESSION': '("INDEX" >15) AND ("DN" > 2)',
            'INPUT': outputs['RinominaCampoIndiceDiLiquefazione']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['RzIl15AndSlope2'] = processing.run('native:extractbyexpression', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(12)
        if feedback.isCanceled():
            return {}

        # zs_dissolvi
        alg_params = {
            'FIELD': [''],
            'INPUT': outputs['Zs_merge']['OUTPUT'],
            'SEPARATE_DISJOINT': True,
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['Zs_dissolvi'] = processing.run('native:dissolve', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(13)
        if feedback.isCanceled():
            return {}

        # RZ (2< IL<=5) and (slope >5 )
        alg_params = {
            'EXPRESSION': '("INDEX">2 AND "INDEX"<=5) \r\nAND ("DN" > 5 )',
            'INPUT': outputs['RinominaCampoIndiceDiLiquefazione']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['Rz2Il5AndSlope5'] = processing.run('native:extractbyexpression', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(14)
        if feedback.isCanceled():
            return {}

        # RZ (5< IL< =15) AND (Slope > 5)
        alg_params = {
            'EXPRESSION': '("INDEX" >5 AND "INDEX" <= 15) AND ("DN" > 5)',
            'INPUT': outputs['RinominaCampoIndiceDiLiquefazione']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['Rz5Il15AndSlope5'] = processing.run('native:extractbyexpression', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(15)
        if feedback.isCanceled():
            return {}

        # zr_merge
        alg_params = {
            'CRS': 'ProjectCrs',
            'LAYERS': [outputs['RzIl15AndSlope2']['OUTPUT'],outputs['Rz2Il5AndSlope5']['OUTPUT'],outputs['Rz5Il15AndSlope5']['OUTPUT'],outputs['Rz0Il2AndSlope15']['OUTPUT']],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['Zr_merge'] = processing.run('native:mergevectorlayers', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(16)
        if feedback.isCanceled():
            return {}

        # low_zo_dissolve
        alg_params = {
            'FIELD': [''],
            'INPUT': outputs['Sz00il2And2Slope5']['OUTPUT'],
            'SEPARATE_DISJOINT': True,
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['Low_zo_dissolve'] = processing.run('native:dissolve', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(17)
        if feedback.isCanceled():
            return {}

        # zr_dissolvi
        alg_params = {
            'FIELD': [''],
            'INPUT': outputs['Zr_merge']['OUTPUT'],
            'SEPARATE_DISJOINT': True,
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['Zr_dissolvi'] = processing.run('native:dissolve', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(18)
        if feedback.isCanceled():
            return {}

        # Riorganizza campi
        alg_params = {
            'FIELDS_MAPPING': [{'alias': '','comment': '','expression': 'zone','length': 255,'name': 'zone','precision': 0,'sub_type': 0,'type': 10,'type_name': 'text'}],
            'INPUT': outputs['Low_zo_dissolve']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['RiorganizzaCampi'] = processing.run('native:refactorfields', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(19)
        if feedback.isCanceled():
            return {}

        # zr_dissolve_riorganizza campi
        alg_params = {
            'FIELDS_MAPPING': [{'alias': '','comment': '','expression': 'zone_code','length': 255,'name': 'zone','precision': 0,'sub_type': 0,'type': 10,'type_name': 'text'}],
            'INPUT': outputs['Zr_dissolvi']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['Zr_dissolve_riorganizzaCampi'] = processing.run('native:refactorfields', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(20)
        if feedback.isCanceled():
            return {}

        # zs_riorganizza campi
        alg_params = {
            'FIELDS_MAPPING': [{'alias': '','comment': '','expression': 'code','length': 255,'name': 'code','precision': 0,'sub_type': 0,'type': 10,'type_name': 'text'}],
            'INPUT': outputs['Zs_dissolvi']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['Zs_riorganizzaCampi'] = processing.run('native:refactorfields', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(21)
        if feedback.isCanceled():
            return {}

        # zr_calcolatore di campi
        alg_params = {
            'FIELD_LENGTH': 255,
            'FIELD_NAME': 'zone_code',
            'FIELD_PRECISION': 0,
            'FIELD_TYPE': 2,  # Testo (stringa)
            'FORMULA': "'respect zone - RZ'",
            'INPUT': outputs['Zr_dissolve_riorganizzaCampi']['OUTPUT'],
            'OUTPUT': parameters['RespectZonesRs']
        }
        outputs['Zr_calcolatoreDiCampi'] = processing.run('native:fieldcalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)
        results['RespectZonesRs'] = outputs['Zr_calcolatoreDiCampi']['OUTPUT']

        feedback.setCurrentStep(22)
        if feedback.isCanceled():
            return {}

        # Z0 Calcolatore di campi
        alg_params = {
            'FIELD_LENGTH': 255,
            'FIELD_NAME': 'zone',
            'FIELD_PRECISION': 0,
            'FIELD_TYPE': 2,  # Testo (stringa)
            'FORMULA': "'Classe low Z0'",
            'INPUT': outputs['RiorganizzaCampi']['OUTPUT'],
            'OUTPUT': parameters['LowLateralSpreadingZ0']
        }
        outputs['Z0CalcolatoreDiCampi'] = processing.run('native:fieldcalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)
        results['LowLateralSpreadingZ0'] = outputs['Z0CalcolatoreDiCampi']['OUTPUT']

        feedback.setCurrentStep(23)
        if feedback.isCanceled():
            return {}

        # zs_calcolatore di campi
        alg_params = {
            'FIELD_LENGTH': 255,
            'FIELD_NAME': 'code',
            'FIELD_PRECISION': 0,
            'FIELD_TYPE': 2,  # Testo (stringa)
            'FORMULA': "'susceptibility zone - SZ'",
            'INPUT': outputs['Zs_riorganizzaCampi']['OUTPUT'],
            'OUTPUT': parameters['SusceptibilityZonesSz']
        }
        outputs['Zs_calcolatoreDiCampi'] = processing.run('native:fieldcalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)
        results['SusceptibilityZonesSz'] = outputs['Zs_calcolatoreDiCampi']['OUTPUT']
        return results

    def name(self):
        return 'Lateral Spreading'

    def displayName(self):
        return 'Lateral Spreading for SM'

    def group(self):
        return 'Lateral Spreading for SM'

    def groupId(self):
        return 'Lateral Spreading'

    def shortHelpString(self):
        return """<html><body><p><!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.0//EN" "http://www.w3.org/TR/REC-html40/strict.dtd">
<html><head><meta name="qrichtext" content="1" /><style type="text/css">
</style></head><body style=" font-family:'MS Shell Dlg 2'; font-size:9.5pt; font-weight:400; font-style:normal;">
<p style=" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;"><span style=" font-size:12pt; font-weight:600;">Lateral spreading for seismic microzonation</span></p>
<p style=" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;"><span style=" font-weight:600; color:#000000;">The tool calculates zones subject to lateral spreading:</span></p>
<p style=" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;"><span style=" font-weight:600; color:#33a02c;">A) Low Susceptibility Zones (Z0): </span></p>
<p style=" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;"><span style=" color:#000000;">2 &lt; Slope% ≤ 5 and 0 &lt; IL ≤ 2</span></p>
<p style=" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;"><span style=" font-weight:600; color:#ff7f00;">B) Susceptibility Zones (SZ)</span></p>
<p style=" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;"><span style=" color:#000000;">0&lt; IL ≤ 2 and 5 &lt; Slope% ≤ 15</span></p>
<p style=" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;"><span style=" color:#000000;">2&lt; IL ≤ 5 and 2 &lt; Slope% &gt; 5</span></p>
<p style=" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;"><span style=" color:#000000;">5 &lt; IL ≤ 15 and 2 &lt; Slope% ≤ 5</span></p>
<p style=" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;"><span style=" font-weight:600; color:#fc3300;">C) Respect Zones (RZ)</span></p>
<p style=" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;"><span style=" color:#000000;">0&lt; IL ≤ 2 and Slope% &gt; 15</span></p>
<p style=" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;"><span style=" color:#000000;">2&lt; IL ≤ 5 and Slope% &gt; 5</span></p>
<p style=" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;"><span style=" color:#000000;">5&lt; IL ≤ 15 and Slope% &gt; 5</span></p>
<p style=" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;"><span style=" color:#000000;">IL &gt;15 and Slope% &gt; 2</span></p>
<p style="-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; color:#000000;"><br /></p>
<p style=" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;"><span style=" color:#666666;">*IL = liquefaction index</span></p></body></html></p>
<p><!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.0//EN" "http://www.w3.org/TR/REC-html40/strict.dtd">
<html><head><meta name="qrichtext" content="1" /><style type="text/css">
</style></head><body style=" font-family:'MS Shell Dlg 2'; font-size:9.5pt; font-weight:400; font-style:normal;">
<p style="-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;"><br /></p></body></html></p><br><p align="right">Autore algoritmo: Giuseppe Cosentino (Pino)</p><p align="right">Versione algoritmo: 0.1 20250122</p></body></html>"""

    def createInstance(self):
        return SeismicMicrozonationAlgorithm()
