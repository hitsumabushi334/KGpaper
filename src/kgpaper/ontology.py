from rdflib import Namespace, RDF, RDFS, XSD

# Define namespace
KG = Namespace("http://example.org/kgpaper/")

# Mapping for convenience
PREFIXES = {
    "kg": KG,
    "rdf": RDF,
    "rdfs": RDFS,
    "xsd": XSD
}

# Classes
CLASS_PAPER = KG.Paper
CLASS_DOCUMENT_PART = KG.DocumentPart
CLASS_EXPERIMENT = KG.Experiment

# Content Types (Classes or Instances? Usually instances or subclasses if fixed)
# Using instances for content types to be used as values for contentType property
CONTENT_TYPE_METHOD = KG.Method
CONTENT_TYPE_RESULT = KG.Result
CONTENT_TYPE_DISCUSSION = KG.Discussion
CONTENT_TYPE_CONCLUSION = KG.Conclusion

# Experiment Types (Instances)
EXP_TYPE_SYNTHESIS = KG.Synthesis
EXP_TYPE_CHARACTERIZATION = KG.Characterization
EXP_TYPE_ELECTROCHEMICAL = KG.Electrochemical
EXP_TYPE_SPECTROSCOPY = KG.Spectroscopy
EXP_TYPE_THERMAL = KG.Thermal
EXP_TYPE_MECHANICAL = KG.Mechanical
EXP_TYPE_COMPUTATIONAL = KG.Computational
EXP_TYPE_BIOLOGICAL = KG.Biological
EXP_TYPE_OTHER = KG.Other

# Properties
PROP_PAPER_TITLE = KG.paperTitle
PROP_PAPER_DOI = KG.paperDOI
PROP_SOURCE_FILE = KG.sourceFile
PROP_EXTRACTED_AT = KG.extractedAt

PROP_HAS_DOCUMENT_PART = KG.hasDocumentPart
PROP_DOCUMENT_TYPE = KG.documentType # "main" or "support"

PROP_HAS_EXPERIMENT = KG.hasExperiment
PROP_EXPERIMENT_TYPE = KG.experimentType # points to EXP_TYPE_*

PROP_HAS_CONTENT = KG.hasContent
PROP_CONTENT_TYPE = KG.contentType # points to CONTENT_TYPE_*
PROP_CONTENT_TEXT = KG.text

# Document Types (Literals or Constants)
DOC_TYPE_MAIN = "main"
DOC_TYPE_SUPPORT = "support"
