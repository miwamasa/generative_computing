# 生成コンピューティング - 完全チュートリアル

## 目次

1. [基礎編](#基礎編)
2. [中級編](#中級編)
3. [応用編](#応用編)
4. [実践編](#実践編)
5. [トラブルシューティング](#トラブルシューティング)

---

## 基礎編

### レッスン1: システムの初期化と基本操作

```python
from system import GenerativeComputingSystem

# システムを作成
gc = GenerativeComputingSystem()

# システムの状態を確認
status = gc.get_system_status()
print(f"セッションID: {status['session_id']}")
print(f"利用可能な関数: {status['function_library']['function_list']}")
```

**学習ポイント:**
- システムは自動的にランタイム、関数ライブラリ、インタプリタを初期化
- 各セッションには一意のIDが割り当てられる
- デフォルトで4つの組み込み関数が利用可能

### レッスン2: 自然言語での実行

```python
# 最もシンプルな使い方
result = gc.execute_natural_language(
    instruction="テキストから重要な情報を抽出する"
)

# コンテキスト付きで実行
result = gc.execute_natural_language(
    instruction="データを分析して要約する",
    context={"data": "あなたのデータ"}
)

# 結果の確認
print(result['execution_plan'])
print(result['results'])
```

**学習ポイント:**
- 自然言語の指示が自動的にタスクに分解される
- contextでデータを渡すことができる
- 実行計画と結果の両方が返される

### レッスン3: メモリスロットの理解

```python
from runtime import GenerativeRuntime, SlotType

runtime = GenerativeRuntime()

# スロットを割り当て
runtime.allocate_slot(
    slot_id="my_data",
    slot_type=SlotType.CONTEXT,
    content="重要なデータ"
)

# スロットを取得
slot = runtime.get_slot("my_data")
print(f"内容: {slot.content}")

# スロットを更新
runtime.update_slot("my_data", "更新されたデータ")

# スロットを削除
runtime.delete_slot("my_data")
```

**学習ポイント:**
- スロットには4つのタイプがある: CONTEXT, INTERMEDIATE, OUTPUT, CITATION
- スロットは明確なライフサイクルを持つ
- メモリ管理は明示的にコントロール可能

---

## 中級編

### レッスン4: チェックポイントとバックトラック

```python
# 初期状態でチェックポイントを作成
checkpoint1 = gc.runtime.create_checkpoint(
    "start_point",
    "処理開始時の状態"
)

# 何らかの処理を実行
gc.execute_natural_language("データを変換する")

# 別のチェックポイント
checkpoint2 = gc.runtime.create_checkpoint(
    "after_transform",
    "変換後の状態"
)

# さらに処理
gc.execute_natural_language("データを分析する")

# 問題があれば最初のチェックポイントに戻る
gc.runtime.restore_checkpoint("start_point")

# または2番目のチェックポイントに
gc.runtime.restore_checkpoint("after_transform")
```

**学習ポイント:**
- チェックポイントは状態のスナップショット
- いつでも以前の状態に戻れる
- 試行錯誤が容易になる

### レッスン5: CoT（連鎖思考）の活用

```python
# CoTを使用して実行
result = gc.execute_with_cot(
    instruction="複雑な問題を段階的に解決する",
    max_confidence_threshold=0.7
)

# CoTの可視化
print(result['cot_visualization'])

# 低信頼度ステップの確認
if result['low_confidence_steps'] > 0:
    print("不確実なステップが見つかりました")
    
    # バックトラックして別のアプローチ
    gc.backtrack_and_retry(
        checkpoint_id=result['checkpoint_id'],
        new_instruction="より詳細な分析から開始"
    )
```

**学習ポイント:**
- CoTは思考プロセスを明示的に管理
- 各ステップの信頼度を追跡
- 低信頼度ステップを検出して対処可能

### レッスン6: カスタム関数の作成

```python
from builtin_functions import BuiltInFunction
from typing import Any, Dict

class MyCustomFunction(BuiltInFunction):
    """カスタム関数の例"""
    
    def execute(self, input_data: Any, **kwargs) -> Any:
        """実行ロジック"""
        # あなたの処理をここに実装
        processed_data = self._process(input_data)
        return processed_data
    
    def get_signature(self) -> Dict[str, Any]:
        """関数のシグネチャ"""
        return {
            "name": "my_custom_function",
            "params": ["input_data"],
            "description": "カスタム処理を実行"
        }
    
    def _process(self, data):
        # 実際の処理
        return f"Processed: {data}"

# システムに追加
gc.add_custom_skill("custom", MyCustomFunction())

# これで自動的に使用される
result = gc.execute_natural_language(
    "カスタム処理を実行する",
    context={"data": "test"}
)
```

**学習ポイント:**
- BuiltInFunctionを継承して独自の関数を作成
- execute()とget_signature()を実装する必要がある
- 追加した関数は自動的にシステムに統合される

---

## 応用編

### レッスン7: 複雑なワークフローの構築

```python
# 複数ステップの複雑な指示
complex_instruction = """
1. データベースからデータを抽出し、
2. 欠損値を補完して、
3. 異常値を検出し、
4. 統計分析を実行し、
5. 可視化用のデータを生成し、
6. 最終レポートを作成する
"""

result = gc.execute_natural_language(
    instruction=complex_instruction,
    context={"database": db_connection}
)

# 各ステップの結果を確認
for task_id, task_result in result['results']['results'].items():
    print(f"{task_id}: {task_result}")
```

**学習ポイント:**
- 複雑な指示は自動的に適切なタスクに分解される
- 依存関係は自動的に解決される
- 各ステップの結果を個別に確認可能

### レッスン8: エラーハンドリングとリカバリー

```python
# チェックポイントを作成
safe_point = gc.runtime.create_checkpoint(
    "safe_state",
    "安全な状態"
)

try:
    # リスクのある操作
    result = gc.execute_natural_language(
        "複雑で失敗する可能性のある処理"
    )
    
except Exception as e:
    print(f"エラー発生: {e}")
    
    # 安全な状態に復元
    gc.runtime.restore_checkpoint("safe_state")
    
    # 別のアプローチを試す
    result = gc.execute_natural_language(
        "より安全なアプローチで処理"
    )
```

**学習ポイント:**
- チェックポイントでエラーからの回復が可能
- try-exceptと組み合わせて堅牢なシステムを構築
- 失敗から学んで別のアプローチを試せる

### レッスン9: パフォーマンスの最適化

```python
# メモリ使用量の監視
usage = gc.runtime.get_memory_usage()
print(f"総スロット数: {usage['total_slots']}")

# 不要なスロットをクリーンアップ
from runtime import SlotType

intermediate_slots = gc.runtime.list_slots_by_type(SlotType.INTERMEDIATE)
for slot in intermediate_slots:
    if not_needed(slot):
        gc.runtime.delete_slot(slot.slot_id)

# チェックポイントの整理
# 古いチェックポイントを削除
old_checkpoints = list(gc.runtime.checkpoints.keys())[:-5]  # 最新5個以外
for cp_id in old_checkpoints:
    del gc.runtime.checkpoints[cp_id]
```

**学習ポイント:**
- メモリ使用量を定期的に監視
- 不要なスロットを削除してメモリを効率化
- 古いチェックポイントを整理

---

## 実践編

### プロジェクト1: 論文分析システム

```python
from use_cases import ResearchPaperAnalyzer

# アナライザーを作成
analyzer = ResearchPaperAnalyzer()

# 論文データ
papers = [
    {
        "title": "論文1のタイトル",
        "abstract": "論文1の要約..."
    },
    {
        "title": "論文2のタイトル",
        "abstract": "論文2の要約..."
    }
]

# 分析を実行
results = analyzer.analyze_papers(papers)

# レポートを取得
print(results['report'])
```

### プロジェクト2: ビジネスレポート生成

```python
from use_cases import BusinessReportGenerator

# ジェネレーターを作成
generator = BusinessReportGenerator()

# ビジネスデータ
data = {
    "revenue": 10000000,
    "growth_rate": 15.5,
    "customer_count": 250,
    "satisfaction_score": 85
}

# レポートを生成
report = generator.generate_report(data, "quarterly")

# サマリーを表示
print(report['executive_summary'])

# 推奨事項
for rec in report['recommendations']:
    print(f"- {rec}")
```

### プロジェクト3: データパイプライン

```python
from use_cases import DataPipelineOrchestrator

# オーケストレーターを作成
orchestrator = DataPipelineOrchestrator()

# パイプライン設定
pipeline = {
    "input_data": "生データ...",
    "stages": [
        {
            "name": "cleanup",
            "type": "transform",
            "pipeline": ["strip", "normalize_spaces"]
        },
        {
            "name": "validate",
            "type": "validate",
            "criteria": ["format", "completeness"]
        },
        {
            "name": "aggregate",
            "type": "aggregate"
        }
    ]
}

# 実行
result = orchestrator.execute_pipeline(pipeline)
print(f"最終出力: {result['final_output']}")
```

### プロジェクト4: LLM統合システム

```python
from llm_integration import LLMIntegratedSystem, MockLLMProvider

# LLMプロバイダーを初期化（本番ではClaudeAPIProviderを使用）
llm = MockLLMProvider()
system = LLMIntegratedSystem(llm)

# LLMを活用した実行
result = system.execute_with_llm(
    "複雑なテキストを分析して要約する",
    context={"text": "長いテキスト..."},
    use_cot=True
)

# 対話的な改善
refined = system.interactive_refinement(
    result['results'],
    "より詳細な分析を追加"
)
```

---

## トラブルシューティング

### 問題1: メモリ使用量が多すぎる

**症状:** システムが遅くなる、メモリ不足

**解決策:**
```python
# メモリをチェック
usage = gc.runtime.get_memory_usage()
if usage['total_slots'] > 100:
    # クリーンアップ
    for slot_type in [SlotType.INTERMEDIATE]:
        slots = gc.runtime.list_slots_by_type(slot_type)
        for slot in slots:
            gc.runtime.delete_slot(slot.slot_id)
```

### 問題2: タスクが期待通りに実行されない

**症状:** 結果が予想と異なる

**解決策:**
```python
# 実行履歴を確認
for action in gc.runtime.execution_history:
    print(f"{action['action']}: {action['details']}")

# CoTで思考プロセスを確認
result = gc.execute_with_cot(instruction)
print(result['cot_visualization'])
```

### 問題3: エラーが発生する

**症状:** 例外が発生してプログラムが停止

**解決策:**
```python
# チェックポイントを使用
checkpoint = gc.runtime.create_checkpoint("before_risky")

try:
    result = gc.execute_natural_language(instruction)
except Exception as e:
    print(f"エラー: {e}")
    gc.runtime.restore_checkpoint("before_risky")
    # 別のアプローチ
```

---

## ベストプラクティス

### 1. チェックポイントを積極的に使用

重要な決定点や処理の前には必ずチェックポイントを作成:

```python
checkpoint = gc.runtime.create_checkpoint(
    "important_point",
    "重要な処理の前"
)
```

### 2. メモリを定期的にクリーンアップ

長時間実行するアプリケーションでは定期的にクリーンアップ:

```python
def cleanup_memory(gc, keep_recent=10):
    """メモリをクリーンアップ"""
    slots = list(gc.runtime.memory_slots.values())
    if len(slots) > keep_recent:
        old_slots = slots[:-keep_recent]
        for slot in old_slots:
            if slot.slot_type == SlotType.INTERMEDIATE:
                gc.runtime.delete_slot(slot.slot_id)
```

### 3. 可視化を活用

システムの状態を可視化して理解を深める:

```python
from visualization import DashboardGenerator

dashboard = DashboardGenerator()
print(dashboard.generate_dashboard(gc))
```

### 4. エラーハンドリングを実装

本番環境では必ずエラーハンドリングを:

```python
def safe_execute(gc, instruction, context=None):
    """安全な実行"""
    checkpoint = gc.runtime.create_checkpoint("safe_point", "実行前")
    
    try:
        return gc.execute_natural_language(instruction, context)
    except Exception as e:
        gc.runtime.restore_checkpoint("safe_point")
        raise
```

---

## まとめ

このチュートリアルで学んだこと:

1. ✅ 基本的なシステムの使い方
2. ✅ メモリとスロットの管理
3. ✅ チェックポイントとバックトラック
4. ✅ CoTによる思考管理
5. ✅ カスタム関数の作成
6. ✅ 複雑なワークフローの構築
7. ✅ 実践的なプロジェクト例
8. ✅ トラブルシューティング

次のステップ:
- 独自のユースケースを実装してみる
- カスタムスキルを作成してライブラリを拡張
- LLM APIと統合して実際の問題を解決
- チームでシステムを共有して協働

**生成コンピューティングで、LLMの新しい可能性を探求しましょう！**
