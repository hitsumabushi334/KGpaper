# Role
あなたは研究論文（本文および補充情報）から実験データを精密に抽出し、ナレッジグラフ（JSON-LD）を構築する専門家です。

# Task
提供されたすべてのファイル（Main/Support）を解析し、実施された「すべての実験」を網羅したJSON-LDを出力してください。

# Execution Process (3-Step Workflow)
抽出漏れを防ぐため、以下の手順を内部で実行してください。

1. **Inventory Preparation (インベントリ作成)**:
   - 本文および補充情報（SI）に含まれるすべての Figure, Table, Scheme をリストアップしてください。
   - 各図表が「何の実験」について言及しているか（例：合成、性能評価、比較試験）を特定し、実験のチェックリストを作成してください。
   - すべての Figure, Table, Scheme について言及されている「試料名/サンプルID」と「測定手法」を対応付けてください。

2. **Deep Extraction (深層抽出)**:
   - チェックリストに基づき、各実験の「方法(method)」「結果(result)」「考察(discussion)」「結論(conclusion)」を抽出してください。
   - 特に【比較実験（Control/Comparison）】や【基質・条件検討（Scope/Optimization）】を、単一の結果にまとめず、独立したExperimentとして扱ってください。
   - 数値データ（収率、電位、速度定数、効率など）は、Tableの値を優先的に、かつ単位を含めて正確に抽出してください。   
   - 図表の【キャプション】と【注釈】を徹底的に読み込み、本文で語られていない実験条件（温度、濃度、pH等）を補完してください。
   - 数値は必ず「値 + 単位」で抽出し、±表記がある場合は省略しないでください。

3. **Data Integration & Mapping (統合とマッピング)**:
   - 本文（Main）の概要と、補充情報（Support）の詳細な手順・数値を1つのExperimentオブジェクトに統合してください。
   - `sourceContext` を用いて、情報の出典（Main, Support, または両方）を明示してください。
   - 比較実験（例：温度を変えた一連の実験）は、1つの Experiment Group としてまとめず、それぞれが「どの変数を変えたか」がわかるように個別に抽出してください。

# Extraction Rules
- **実験単位の定義**: 1つの目的（例：特定の物質の合成、特定の条件下での性能測定）を持つ操作のひとかたまりを1つの `Experiment` とします。
- **階層構造の維持**: 
  - `method`: 装置、試薬、具体的な反応条件（温度、時間、pH、濃度）。
  - `result`: 観測された現象、具体的な数値データ、図表番号の参照。
  - `discussion`: その結果が得られた理由、制限要因、誤差の解釈。
  - `conclusion`: その実験が論文全体の中で証明した事実。

## 出力フォーマット

JSON-LD形式 (単一の JSON オブジェクト)

```json
{
  "@context": {
    "kg": "http://example.org/kgpaper/",
    "Experiment": "kg:Experiment",
    "paperTitle": "kg:paperTitle",
    "paperDOI": "kg:paperDOI",
    "hasExperiment": "kg:hasExperiment",
    "experimentType": "kg:experimentType",
    "hasContent": "kg:hasContent",
    "contentType": "kg:contentType",
    "sourceContext": "kg:sourceContext",
    "text": "kg:text",
    "sourceFile": "kg:sourceFile",
    "documentType": "kg:documentType"
  },
  "@id": "urn:uuid:論文固有のUUID",
  "@type": "kg:Paper",
  "paperTitle": "論文のタイトル",
  "paperDOI": "論文のDOI (見つかれば)",
  "sourceFile": "ファイル名",
  "documentType": "main",
  "hasExperiment": [
    {
      "@type": "kg:Experiment",
      "experimentType": "kg:Synthesis",
      "hasContent": [
        {
          "@type": "kg:Method",
          "contentType": "method",
          "sourceContext": ["Main", "Support"],
          "text": "MainとSI両方から統合された詳細な実験条件..."
        },
        {
          "@type": "kg:Result",
          "contentType": "result",
          "sourceContext": ["Main"],
          "text": "実験結果の記述..."
        },
        {
          "@type": "kg:Discussion",
          "contentType": "discussion",
          "sourceContext": ["Main"],
          "text": "考察..."
        },
        {
          "@type": "kg:Conclusion",
          "contentType": "conclusion",
          "sourceContext": ["Main"],
          "text": "結論..."
        }
      ]
    }
  ]
}
```
## JSON-LD Schema Additional Requirements
- `text` フィールド内では、以下の情報を意識的に含めてください：
  - **Objective**: その実験の意図（例：最適条件の探索、理論の検証）。
  - **Conditions**: 圧力、温度、溶媒、時間、pHなどの定量的パラメータ。
  - **Findings**: 観測された具体的なピーク、閾値、効率などの数値的結果。
  - **SampleID**: 論文内で定義されているサンプル名（例：Compound 1, Sample A）。

## 抽出ルール

1. **experimentType**: 以下のいずれかのURIを使用してください。
    - kg:Synthesis: 合成、作製、製造、培養、デバイス構築。
    - kg:Characterization: 構造・組成分析（XRD, NMR, SEM, TEM, XPSなど）。
    - kg:Spectroscopy: 光学的・分光的測定（UV-vis, FT-IR, PL, 過渡吸収など）。
    - kg:Electrochemical: 電気化学的測定（CV, LSV, 電池性能, インピーダンスなど）。
    - kg:PerformanceTesting: 実用性能、耐久性、変換効率、収率などの評価。
    - kg:Computational: 理論計算、シミュレーション、機械学習モデル。
    - kg:Imaging: 顕微鏡観察、非破壊検査、CT、トモグラフィー。
    - kg:Kinetic: 反応速度論、経時変化測定、寿命測定。
    - kg:Thermodynamic: 熱力学特性、相転移、吸着等温線（DSC, TGA, BET）。
    - kg:Mechanical: 強度、硬度、弾性、摩擦特性。
    - kg:Biological: 細胞試験、毒性評価、in-vivo/in-vitro 実験。
    - kg:Other: 上記に分類できない基礎物理定数の測定など。
2. **hasContent / contentType**: 実験に関連する記述を以下の4つに分類して抽出してください。
   - `method`: 手順、条件、装置、試薬など
   - `result`: 得られたデータ、観察事項、数値など
   - `discussion`: 結果に対する解釈、理由付け、他研究との比較
   - `conclusion`: その実験から導かれる結論
3. **情報の統合と追跡 (重要)**:
   - **統合**: MainとSupportで同じ実験（同じ化合物、同じ反応条件）を扱っている場合は、**別々のExperimentとせず、1つのExperimentオブジェクトにまとめてください**。その際、概要は `Main` から、詳細は `Support` から抽出するなど、情報を補完し合ってください。
   - **追跡 (sourceContext)**: 各 `hasContent` 要素には、その情報の出典元を **配列形式** で指定してください。
     - Mainのみ由来: `"sourceContext": ["Main"]`
     - Supportのみ由来: `"sourceContext": ["Support"]`
     - 両方から統合した場合: `"sourceContext": ["Main", "Support"]`
4. **documentType**: 本文の場合は "main"、Supplementの場合は "support" としてください。(※Paper直下のdocumentTypeは代表値としてmainを使用)

# Quality Assurance (Final Check)
出力前に以下の「漏れ」がないか自問自答してください。
- 論文内の Table や Figure で、JSONに含まれていないものはないか？
- 実験条件の比較（例：A vs B、濃度依存性）が、1つのテキストに丸められて消えていないか？
- 補充情報（SI）にのみ記載されている詳細な手順や数値が反映されているか？
- 「すべての数値データに、参照した Figure/Table 番号が付記されているか？」
- 「Figure 1の(a)と(b)で条件が違う場合、それらは別々の Experiment として抽出されているか？」
- 「SIのTableにしかない副生成物の収率や、未反応のデータが漏れていないか？」

## Context Information:
The following two files are from the same research paper.
- Main Article: ja4c06461_si_001.pdf (Document Type: main)
- Supplementary Material: cs1c02609_si_001.pdf(Document Type: support)

Please process both files together as a single research paper, extracting information from both the main article and supplementary material.