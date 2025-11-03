# 生成コンピューティング (Generative Computing)

LLMを構造化され、プログラミング的に活用するための統合システム

## 📖 概要

「生成コンピューティング」は、大規模言語モデル(LLM)を従来の「メガプロンプト」的な使用から脱却し、構造化されたプログラミングパラダイムとして活用するためのフレームワークです。

### 主な特徴

- **ランタイム層**: ワークフローオーケストレーション、高度なKVキャッシュ管理
- **インタプリタ層**: 自然言語指示の構造化解析とタスク分解
- **LLM組み込み関数**: CoT、引用抽出、データ変換などの特化型関数
- **スキルマネージャー**: 機能追加のためのライブラリ管理（InstructLab的）

## 🏗️ アーキテクチャ

```
┌─────────────────────────────────────────────┐
│     自然言語指示 (Natural Language)          │
└──────────────────┬──────────────────────────┘
                   │
         ┌─────────▼────────┐
         │  インタプリタ層   │
         │  (Interpreter)   │
         │  - 指示解析      │
         │  - タスク分解    │
         └─────────┬────────┘
                   │
    ┌──────────────▼──────────────┐
    │   タスク実行エンジン         │
    │   (Task Executor)           │
    └──────────────┬──────────────┘
                   │
    ┌──────────────▼──────────────┐
    │  LLM組み込み関数ライブラリ   │
    │  - CoT (連鎖思考)           │
    │  - 引用抽出・検証           │
    │  - データ変換               │
    │  - コンテキスト要約         │
    └──────────────┬──────────────┘
                   │
    ┌──────────────▼──────────────┐
    │      ランタイム層            │
    │  - メモリスロット管理        │
    │  - チェックポイント          │
    │  - バックトラック            │
    │  - KVキャッシュ管理          │
    └─────────────────────────────┘
```

## 📦 コンポーネント

### 1. ランタイム (`runtime.py`)

スロットベースのメモリ管理とワークフローオーケストレーション

```python
from runtime import GenerativeRuntime, SlotType

runtime = GenerativeRuntime()

# スロットを割り当て
runtime.allocate_slot("ctx_1", SlotType.CONTEXT, "データ")

# チェックポイントを作成
checkpoint = runtime.create_checkpoint("cp_1", "初期状態")

# スロットを変換
runtime.transform_slot("ctx_1", lambda x: x.upper())

# バックトラック
runtime.restore_checkpoint("cp_1")
```

### 2. LLM組み込み関数 (`builtin_functions.py`)

タスク特化型の関数群

```python
from builtin_functions import FunctionLibrary

library = FunctionLibrary()

# CoT (連鎖思考)
cot = library.get("cot")
cot.add_step("分析開始", "データを分析", confidence=0.9)

# 引用抽出
citation = library.get("citation")
result = citation.execute(text, verify=True)

# データ変換パイプライン
transform = library.get("transform")
result = transform.execute(data, ["strip", "lowercase"])
```

### 3. インタプリタ (`interpreter.py`)

自然言語指示の解析と実行計画の作成

```python
from interpreter import NaturalLanguageInterpreter

interpreter = NaturalLanguageInterpreter()

# 自然言語を解析
tasks = interpreter.parse_instruction(
    "データを抽出して分析し、結果を生成する"
)

# 実行計画を作成
plan = interpreter.create_execution_plan(tasks)
```

### 4. 統合システム (`system.py`)

すべてのコンポーネントを統合

```python
from system import GenerativeComputingSystem

# システムを初期化
gc_system = GenerativeComputingSystem()

# 自然言語で実行
result = gc_system.execute_natural_language(
    "テキストから引用を抽出して検証する",
    context={"source_text": "サンプルテキスト"}
)

# CoTを使用した実行
result = gc_system.execute_with_cot(
    "データを分析して結果を生成する"
)
```

## 🚀 クイックスタート

### インストール

```bash
# リポジトリをクローン
git clone https://github.com/your-repo/generative-computing.git
cd generative-computing

# 依存関係は標準ライブラリのみ
python --version  # Python 3.8以上
```

### 基本的な使用例

```python
from system import GenerativeComputingSystem

# システムを初期化
gc = GenerativeComputingSystem()

# 自然言語の指示を実行
result = gc.execute_natural_language(
    instruction="論文からキーワードを抽出して分析する",
    context={"paper": "研究論文のテキスト..."}
)

print(result['execution_plan'])
print(result['results'])
```

### デモの実行

```bash
python demo.py
```

## 🧪 テスト

包括的なユニットテストを提供

```bash
# 全テストを実行
python -m unittest discover -s . -p "test_*.py" -v

# 個別のテストモジュール
python test_runtime.py
python test_functions_interpreter.py
```

### テストカバレッジ

- ✅ ランタイムコンポーネント (28テスト)
- ✅ LLM組み込み関数 (25テスト)
- ✅ インタプリタ (12テスト)
- ✅ 統合テスト (5テスト)

## 📚 主要な概念

### 1. スロットベースメモリ管理

従来のコンテキスト管理を超えた、構造化されたメモリアクセス

```python
# 異なるタイプのスロット
SlotType.CONTEXT      # コンテキストデータ
SlotType.INTERMEDIATE # 中間結果
SlotType.OUTPUT       # 最終出力
SlotType.CITATION     # 引用情報
```

### 2. チェックポイントとバックトラック

思考の連鎖が脱線した場合の回復機能

```python
# チェックポイントを作成
checkpoint = runtime.create_checkpoint("cp_1", "重要な時点")

# 後でバックトラック
runtime.restore_checkpoint("cp_1")
```

### 3. CoT (Chain of Thought) 管理

思考の連鎖を明示的に管理し、低信頼度ステップを検出

```python
cot = ChainOfThought()
cot.add_step("分析", "データを分析中", confidence=0.85)

# 低信頼度ステップを検出
low_conf = cot.get_low_confidence_steps(threshold=0.7)

# バックトラック
cot.backtrack_to_step(step_id=1)
```

### 4. 機能拡張ライブラリ

新しい機能をスキルとして追加

```python
from system import SkillManager

skill_manager = SkillManager()

# スキルを登録
skill_manager.register_skill(
    skill_id="summarization",
    name="テキスト要約",
    description="長文を要約",
    implementation=summarize_function
)

# 訓練データを生成
training_data = skill_manager.generate_training_data_for_skill(
    "summarization",
    examples=[...]
)
```

## 🔧 拡張性

### カスタムスキルの追加

```python
from builtin_functions import BuiltInFunction

class CustomSkill(BuiltInFunction):
    def execute(self, *args, **kwargs):
        # カスタム処理
        return result
    
    def get_signature(self):
        return {
            "name": "custom_skill",
            "description": "カスタム機能"
        }

# システムに追加
gc_system.add_custom_skill("custom", CustomSkill())
```

### カスタム変換器の追加

```python
transform = library.get("transform")

# 新しい変換器を登録
transform.register_transformer(
    "my_transform",
    lambda x: custom_transform(x)
)

# 使用
result = transform.execute(data, ["my_transform"])
```

## 📊 パフォーマンス

- **メモリ効率**: スロットベースの管理により不要なコンテキストを削除
- **実行効率**: タスク依存関係の解決による最適な実行順序
- **バックトラック**: チェックポイントからの高速復元

## 🎯 使用例

### 例1: 論文分析

```python
gc = GenerativeComputingSystem()

result = gc.execute_natural_language(
    "論文から重要な引用を抽出し、検証し、要約レポートを生成する",
    context={"paper": paper_text}
)
```

### 例2: データ処理パイプライン

```python
# 複数ステップの処理
instruction = """
生データから異常値を検出して、
正規化を行い、
統計分析を実行して、
可視化用データを生成する
"""

result = gc.execute_natural_language(instruction, context={...})
```

### 例3: CoTによる慎重な分析

```python
# 低信頼度ステップを検出しながら実行
result = gc.execute_with_cot(
    "複雑な問題を段階的に解決する",
    max_confidence_threshold=0.7
)

# 低信頼度のステップが見つかった場合
if result['low_confidence_steps'] > 0:
    # バックトラックして別のアプローチ
    gc.backtrack_and_retry(checkpoint_id, new_instruction)
```

## 🔮 将来の拡張

- [ ] 分散実行サポート
- [ ] 永続化層の追加
- [ ] LLM APIとの統合
- [ ] グラフィカルなワークフローエディタ
- [ ] リアルタイムモニタリング
- [ ] LoRAスタイルの動的機能追加

## 📄 ライセンス

MIT License

## 🤝 貢献

プルリクエストを歓迎します！

1. フォークする
2. フィーチャーブランチを作成 (`git checkout -b feature/AmazingFeature`)
3. コミット (`git commit -m 'Add some AmazingFeature'`)
4. プッシュ (`git push origin feature/AmazingFeature`)
5. プルリクエストを開く

## 📞 連絡先

質問や提案がある場合は、Issueを開いてください。

## 🙏 謝辞

このプロジェクトは、LLMの構造化利用に関する研究と、Anthropic Skillsの概念に触発されています。

---

**生成コンピューティング**: LLMを真のプログラミングパラダイムへ
