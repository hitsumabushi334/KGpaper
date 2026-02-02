from rdflib import Namespace, RDF, RDFS, XSD

# Define namespace
KG = Namespace("http://example.org/kgpaper/")

# Mapping for convenience
PREFIXES = {"kg": KG, "rdf": RDF, "rdfs": RDFS, "xsd": XSD}

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
EXP_TYPE_SYNTHESIS = KG.Synthesis  # 合成、作製、製造、培養、デバイス構築
EXP_TYPE_CHARACTERIZATION = (
    KG.Characterization
)  # 構造・組成分析（XRD, NMR, SEM, TEM, XPSなど）
EXP_TYPE_SPECTROSCOPY = (
    KG.Spectroscopy
)  # 光学的・分光的測定（UV-vis, FT-IR, PL, 過渡吸収など）
EXP_TYPE_ELECTROCHEMICAL = (
    KG.Electrochemical
)  # 電気化学的測定（CV, LSV, 電池性能, インピーダンスなど）
EXP_TYPE_PERFORMANCE_TESTING = (
    KG.PerformanceTesting
)  # 実用性能、耐久性、変換効率、収率などの評価
EXP_TYPE_COMPUTATIONAL = KG.Computational  # 理論計算、シミュレーション、機械学習モデル
EXP_TYPE_IMAGING = KG.Imaging  # 顕微鏡観察、非破壊検査、CT、トモグラフィー
EXP_TYPE_KINETIC = KG.Kinetic  # 反応速度論、経時変化測定、寿命測定
EXP_TYPE_THERMODYNAMIC = (
    KG.Thermodynamic
)  # 熱力学特性、相転移、吸着等温線（DSC, TGA, BET）
EXP_TYPE_MECHANICAL = KG.Mechanical  # 強度、硬度、弾性、摩擦特性
EXP_TYPE_BIOLOGICAL = KG.Biological  # 細胞試験、毒性評価、in-vivo/in-vitro 実験
EXP_TYPE_OTHER = KG.Other  # 上記に分類できない基礎物理定数の測定など

# Properties
PROP_PAPER_TITLE = KG.paperTitle
PROP_PAPER_DOI = KG.paperDOI
PROP_SOURCE_FILE = KG.sourceFile
PROP_EXTRACTED_AT = KG.extractedAt

PROP_HAS_DOCUMENT_PART = KG.hasDocumentPart
PROP_DOCUMENT_TYPE = KG.documentType  # "main" or "support"

PROP_HAS_EXPERIMENT = KG.hasExperiment
PROP_EXPERIMENT_TYPE = KG.experimentType  # points to EXP_TYPE_*

PROP_HAS_CONTENT = KG.hasContent
PROP_CONTENT_TYPE = KG.contentType  # points to CONTENT_TYPE_*
PROP_SOURCE_CONTEXT = KG.sourceContext  # "Main", "Support", or both
PROP_CONTENT_TEXT = KG.text

# Document Types (Literals or Constants)
DOC_TYPE_MAIN = "main"
DOC_TYPE_SUPPORT = "support"
