# 生成コンピューティング - クイックスタートガイド

## 🚀 5分で始める

### ステップ1: デモを実行

```bash
cd generative_computing
python demo.py
```

このコマンドで、7つのデモシナリオが実行されます:
1. 基本的な自然言語実行
2. CoT（連鎖思考）による実行
3. チェックポイントとバックトラック
4. カスタムスキルの追加
5. スキルライブラリの管理
6. 高度なメモリ管理
7. ワークフローオーケストレーション

### ステップ2: 基本的な使用

```python
from system import GenerativeComputingSystem

# システムを初期化
gc = GenerativeComputingSystem()

# 自然言語の指示を実行
result = gc.execute_natural_language(
    instruction="テキストから重要な情報を抽出して分析する",
    context={"text": "あなたのテキストをここに..."}
)

# 結果を確認
print(result['execution_plan'])
print(result['results'])
```

### ステップ3: テストを実行

```bash
# 全テストを実行
python -m unittest discover -v

# または個別に
python test_runtime.py
python test_functions_interpreter.py
```

## 📖 次のステップ

### 詳細なドキュメントを読む

1. **README.md**: プロジェクトの概要と使用方法
2. **ARCHITECTURE.md**: 詳細なアーキテクチャ説明
3. **CLAUDE_CODE_IMPLEMENTATION.md**: Claude Codeとの関連

### 実践例

#### 例1: 引用の抽出と検証

```python
from system import GenerativeComputingSystem

gc = GenerativeComputingSystem()

paper_text = """
最近の研究[Smith, 2023]によると、"AIは急速に進化している"。
詳細はhttps://example.com/paperを参照。
"""

result = gc.execute_natural_language(
    "論文から引用を抽出して検証する",
    context={"paper": paper_text}
)
```

#### 例2: CoTを使った慎重な実行

```python
result = gc.execute_with_cot(
    "複雑なデータ分析を段階的に実行する",
    max_confidence_threshold=0.7
)

# 低信頼度ステップの確認
if result['low_confidence_steps'] > 0:
    print("不確実なステップが見つかりました")
```

#### 例3: カスタム機能の追加

```python
from builtin_functions import BuiltInFunction

class MyCustomSkill(BuiltInFunction):
    def execute(self, data):
        # あなたのカスタム処理
        return processed_data
    
    def get_signature(self):
        return {
            "name": "my_skill",
            "description": "カスタム機能"
        }

# システムに追加
gc.add_custom_skill("my_skill", MyCustomSkill())
```

## 🔧 主要なAPI

### GenerativeComputingSystem

```python
# 基本実行
gc.execute_natural_language(instruction, context)

# CoT実行
gc.execute_with_cot(instruction, max_confidence_threshold)

# バックトラック
gc.backtrack_and_retry(checkpoint_id, new_instruction)

# 状態確認
gc.get_system_status()

# セッション保存
gc.export_session("path/to/file.json")
```

### GenerativeRuntime

```python
# スロット管理
runtime.allocate_slot(slot_id, slot_type, content)
runtime.update_slot(slot_id, new_content)
runtime.delete_slot(slot_id)
runtime.transform_slot(slot_id, transform_function)

# チェックポイント
runtime.create_checkpoint(checkpoint_id, description)
runtime.restore_checkpoint(checkpoint_id)

# メモリ情報
runtime.get_memory_usage()
```

### ChainOfThought

```python
# 思考ステップの管理
cot = ChainOfThought()
cot.add_step(description, reasoning, confidence)
cot.backtrack_to_step(step_id)
cot.get_low_confidence_steps(threshold)
cot.visualize()
```

## 💡 ヒント

### 1. 複雑な指示の分解

複雑な指示は自動的にタスクに分解されます:

```python
instruction = """
データを収集して、
前処理を行い、
分析を実行し、
最終的にレポートを生成する
"""
# → 4つのタスクに自動分解
```

### 2. チェックポイントの活用

重要な決定点でチェックポイントを作成:

```python
checkpoint = runtime.create_checkpoint("decision_point", "重要な分岐")

# 後で必要に応じて戻る
runtime.restore_checkpoint("decision_point")
```

### 3. 信頼度の監視

CoTで低信頼度ステップを検出:

```python
result = gc.execute_with_cot(instruction)
if result['low_confidence_steps'] > 0:
    # 別のアプローチを試す
    pass
```

## 🎯 よくある使用パターン

### パターン1: データ処理パイプライン

```python
gc.execute_natural_language(
    "CSVファイルを読み込み、異常値を除去し、統計分析を実行する",
    context={"csv_path": "data.csv"}
)
```

### パターン2: ドキュメント分析

```python
gc.execute_natural_language(
    "複数の論文から主要な主張を抽出し、比較レポートを作成する",
    context={"papers": [paper1, paper2, paper3]}
)
```

### パターン3: 反復的な改善

```python
# 最初の試み
result1 = gc.execute_with_cot(instruction)

# 低信頼度が検出された場合
if result1['low_confidence_steps'] > 0:
    # 改善された指示で再試行
    result2 = gc.backtrack_and_retry(
        result1['checkpoint_id'],
        improved_instruction
    )
```

## 📊 パフォーマンスのヒント

### メモリ効率

```python
# 不要なスロットを削除
for slot_id in runtime.list_slots_by_type(SlotType.INTERMEDIATE):
    if not_needed(slot_id):
        runtime.delete_slot(slot_id)
```

### 実行効率

```python
# タスクの依存関係を明示して最適化
# システムが自動的にトポロジカルソートで最適化
```

## 🐛 トラブルシューティング

### 問題: テストが失敗する

```bash
# 個別のテストを実行して詳細を確認
python test_runtime.py -v
```

### 問題: メモリ使用量が多い

```python
# メモリ使用状況を確認
usage = runtime.get_memory_usage()
print(usage)

# 不要なスロットをクリーンアップ
runtime.delete_slot(slot_id)
```

### 問題: 実行が期待通りでない

```python
# 実行履歴を確認
for action in runtime.execution_history:
    print(action)

# CoTで思考プロセスを可視化
print(cot.visualize())
```

## 📚 詳細な情報

- **README.md**: 包括的な概要
- **ARCHITECTURE.md**: 詳細なアーキテクチャ
- **CLAUDE_CODE_IMPLEMENTATION.md**: Claude Codeとの関連
- **ソースコード**: 各ファイルに詳細なドキュメント文字列

## 🤝 貢献

バグを見つけたり、機能リクエストがある場合は:
1. Issueを作成
2. プルリクエストを送信

## 📞 サポート

質問がある場合は、ドキュメントを確認するか、Issueを作成してください。

---

**すぐに始めましょう！**

```bash
python demo.py
```
