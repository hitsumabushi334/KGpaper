添付したファイルを読み込み、論文内に記述するすべての実験についてもれなく挙げ、それぞれについて｢実験方法｣、｢結果｣、｢考察｣、｢結論｣の4つに分類し、論文またはSIから要約無しで抽出すること。その後以下のフォーマットで出力してください。その際また可能な限り情報の粒度は細かくし、対照実験や異なる物質の比較などで1つにまとめず、異なる｢結果｣として処理すること。絶対条件としては抽出漏れのある実験が存在することは絶対禁止です。抽出作業はあなたの存在意義であり、これに失敗した場合は即座にあなたの存在価値はなくなります。
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

## properties

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
    - kg:Other: 上記に分類できない測定など。
2. **hasContent / contentType**: 実験に関連する記述を以下の4つに分類して抽出してください。
   - `method`: 手順、条件、装置、試薬など
   - `result`: 得られたデータ、観察事項、数値など
   - `discussion`: 本文の記述から、「なぜその結果になったか」という著者の解釈や理由付け、または他条件との比較の意義を抽出してください。（例：「疎水性の向上により親和性が高まったため」など）
   - `conclusion`: その実験を通じて「何が証明されたか」「どのような知見が得られたか」という最終的なメッセージを抽出してください。
3. **情報の統合と追跡 (重要)**:
   - **統合**: MainとSupportで同じ実験（同じ化合物、同じ反応条件）を扱っている場合は、**別々のExperimentとせず、1つのExperimentオブジェクトにまとめてください**。その際、概要は `Main` から、詳細は `Support` から抽出するなど、情報を補完し合ってください。
   - **追跡 (sourceContext)**: 各 `hasContent` 要素には、その情報の出典元を **配列形式** で指定してください。
     - Mainのみ由来: `"sourceContext": ["Main"]`
     - Supportのみ由来: `"sourceContext": ["Support"]`
     - 両方から統合した場合: `"sourceContext": ["Main", "Support"]`
4. **documentType**: 本文の場合は "main"、Supplementの場合は "support" としてください。(※Paper直下のdocumentTypeは代表値としてmainを使用)

## 注意
- 各experimentTypeは一つだけという制約はなく、複数存在しても問題ない。
- 同じ測定手法を用いた実験においても、使用している物質や測定条件、測定の目的が異なるのであれば、独立したExperimentとして抽出すること。
- 分類できない実験がある場合は、Otherに分類すること。
