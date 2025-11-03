# 生成コンピューティング - アーキテクチャドキュメント

## 目次

1. [アーキテクチャ概要](#アーキテクチャ概要)
2. [設計原則](#設計原則)
3. [コンポーネント詳細](#コンポーネント詳細)
4. [データフロー](#データフロー)
5. [拡張ポイント](#拡張ポイント)
6. [パフォーマンス考慮事項](#パフォーマンス考慮事項)

## アーキテクチャ概要

生成コンピューティングは、LLMを「メガプロンプト」ではなく、構造化されたプログラミング的に活用するための4層アーキテクチャです。

### 階層構造

```
┌────────────────────────────────────────────────────────┐
│ アプリケーション層                                       │
│ - ユーザーインターフェース                              │
│ - 自然言語指示の入力                                    │
└───────────────────────┬────────────────────────────────┘
                        │
┌───────────────────────▼────────────────────────────────┐
│ インタプリタ層 (Interpreter Layer)                      │
│ - 自然言語 → 構造化タスク                               │
│ - タスク依存関係の解決                                  │
│ - 実行計画の生成                                        │
└───────────────────────┬────────────────────────────────┘
                        │
┌───────────────────────▼────────────────────────────────┐
│ 実行層 (Execution Layer)                                │
│ - タスクエグゼキューター                                │
│ - LLM組み込み関数の呼び出し                             │
│ - 結果の集約                                            │
└─────────┬────────────────────────┬─────────────────────┘
          │                        │
┌─────────▼──────────┐   ┌────────▼────────────────────┐
│ 関数ライブラリ層    │   │ ランタイム層                 │
│ - CoT              │   │ - メモリスロット管理         │
│ - 引用抽出         │   │ - チェックポイント           │
│ - データ変換       │   │ - バックトラック             │
│ - コンテキスト要約 │   │ - KVキャッシュ管理           │
└────────────────────┘   └─────────────────────────────┘
```

## 設計原則

### 1. 構造化と分離

**従来のアプローチ (メガプロンプト)**:
```
巨大な一枚岩のプロンプト
├─ データ
├─ 指示
├─ 例
├─ 制約
└─ 出力フォーマット
```

**生成コンピューティング**:
```
構造化されたコンポーネント
├─ ランタイム (データ管理)
├─ インタプリタ (指示解析)
├─ 関数ライブラリ (再利用可能な機能)
└─ タスク実行エンジン (オーケストレーション)
```

### 2. 明示的な状態管理

- **スロットベースメモリ**: コンテンツを明確なスロットに配置
- **チェックポイント**: 任意の時点の状態を保存
- **バックトラック**: 以前の状態に戻る機能

### 3. 再利用可能な機能

- **組み込み関数**: 共通タスク用の標準化された関数
- **スキルライブラリ**: タスク特化型の拡張可能な機能群
- **訓練データ生成**: 新機能のためのデータ生成機構

### 4. プログラム的制御フロー

- **タスク分解**: 複雑な指示を原子的タスクに分解
- **依存関係管理**: タスク間の依存関係を明示
- **実行順序の最適化**: トポロジカルソート

## コンポーネント詳細

### ランタイム層

#### 責務
- メモリスロットの管理 (割り当て、更新、削除、変換)
- チェックポイントの作成と復元
- 実行履歴の記録
- KVキャッシュの効率的な管理

#### 主要クラス

**GenerativeRuntime**
```python
class GenerativeRuntime:
    memory_slots: Dict[str, MemorySlot]      # スロット管理
    checkpoints: Dict[str, Checkpoint]       # チェックポイント
    execution_history: List[Dict]            # 実行履歴
    
    allocate_slot()    # スロット割り当て
    update_slot()      # スロット更新
    delete_slot()      # スロット削除
    transform_slot()   # スロット変換
    create_checkpoint()  # チェックポイント作成
    restore_checkpoint() # チェックポイント復元
```

**MemorySlot**
```python
@dataclass
class MemorySlot:
    slot_id: str               # 一意識別子
    slot_type: SlotType        # タイプ (CONTEXT, INTERMEDIATE, OUTPUT, CITATION)
    content: Any               # 実際のコンテンツ
    metadata: Dict[str, Any]   # メタデータ
    timestamp: datetime        # タイムスタンプ
```

#### スロットタイプ

1. **CONTEXT**: 入力コンテキスト
   - ユーザー提供データ
   - 長期的に保持

2. **INTERMEDIATE**: 中間結果
   - 処理中のデータ
   - タスク間の受け渡し

3. **OUTPUT**: 最終出力
   - ユーザーに返す結果
   - 長期保存の候補

4. **CITATION**: 引用情報
   - 出典の追跡
   - 検証用データ

### 関数ライブラリ層

#### ChainOfThought (CoT)

思考の連鎖を明示的に管理

```python
思考ステップ
├─ Step 0: 問題の理解 (confidence: 0.95)
├─ Step 1: データ分析 (confidence: 0.85)
├─ Step 2: 仮説の設定 (confidence: 0.70) ← 低信頼度
└─ Step 3: 結論 (confidence: 0.90)

# 低信頼度ステップを検出 → バックトラック可能
```

**主要機能**:
- `add_step()`: 思考ステップを追加
- `backtrack_to_step()`: 特定ステップに戻る
- `get_low_confidence_steps()`: 低信頼度ステップの検出
- `visualize()`: 思考チェーンの可視化

#### CitationExtractor

引用の自動抽出と検証

**サポートする引用タイプ**:
1. 学術引用: `[著者, 年]`
2. URL: `https://...`
3. 引用文: `"..."`

**検証機能**:
- 年の妥当性チェック
- 引用の完全性確認

#### DataTransformPipeline

データ変換のパイプライン処理

```python
入力データ → [変換1] → [変換2] → [変換3] → 出力
              ↓         ↓         ↓
           uppercase  strip    normalize
```

**標準変換器**:
- `uppercase`, `lowercase`: 大文字・小文字変換
- `strip`: 空白除去
- `normalize_spaces`: 空白正規化
- `extract_numbers`: 数値抽出

**拡張性**:
```python
# カスタム変換器の登録
pipeline.register_transformer("custom", custom_func)
```

#### ContextSummarizer

コンテキストの圧縮と要約

**戦略**:
1. `truncate`: 単純な切り詰め
2. `sentence_boundary`: 文境界での切断
3. `extract_key`: キーワード抽出的要約

### インタプリタ層

#### NaturalLanguageInterpreter

自然言語を構造化タスクに変換

**処理フロー**:
```
自然言語指示
    ↓
複合指示の分解
    ↓
各指示をパターンマッチング
    ↓
タスクオブジェクトの生成
    ↓
依存関係の解決
    ↓
実行計画の作成
```

**タスクタイプ**:
- `EXTRACT`: 抽出
- `TRANSFORM`: 変換
- `ANALYZE`: 分析
- `GENERATE`: 生成
- `VALIDATE`: 検証
- `ORCHESTRATE`: 統合

**依存関係の解決**:
```python
Task1 (EXTRACT) → Task2 (ANALYZE) → Task3 (GENERATE)
                      ↓
              Task2の出力がTask3の入力
```

#### TaskExecutor

実行計画に基づいてタスクを実行

**実行サイクル**:
```
1. 実行計画を受け取る
2. トポロジカルソートされた順序で実行
3. 各タスクに適した関数を選択
4. 入力スロットからデータを取得
5. 関数を実行
6. 結果を出力スロットに格納
7. 次のタスクへ
```

### 統合システム層

#### GenerativeComputingSystem

全コンポーネントの統合

**主要メソッド**:

1. `execute_natural_language()`: 基本実行
   ```python
   result = gc.execute_natural_language(
       instruction="データを抽出して分析",
       context={"data": "..."}
   )
   ```

2. `execute_with_cot()`: CoT使用実行
   ```python
   result = gc.execute_with_cot(
       instruction="複雑な問題を解決",
       max_confidence_threshold=0.7
   )
   ```

3. `backtrack_and_retry()`: バックトラック
   ```python
   gc.backtrack_and_retry(
       checkpoint_id="cp_1",
       new_instruction="別のアプローチ"
   )
   ```

#### SkillManager

機能拡張のためのライブラリ管理

**InstructLab的なアプローチ**:
```
新しいスキルの追加
    ↓
訓練データの生成
    ↓
(将来的に) LoRA的な微調整
    ↓
スキルライブラリに追加
    ↓
検索可能な形で体系化
```

## データフロー

### 典型的な実行フロー

```
1. ユーザー入力
   "論文から引用を抽出して検証し、レポートを生成"

2. インタプリタ
   → Task1: EXTRACT (引用抽出)
   → Task2: VALIDATE (検証)
   → Task3: GENERATE (レポート生成)

3. 実行計画
   Task1 → Task2 → Task3 (依存関係)

4. チェックポイント作成
   checkpoint_0: 初期状態

5. Task1実行
   - 入力: context_paper スロット
   - 関数: CitationExtractor
   - 出力: task1_output スロット

6. Task2実行
   - 入力: task1_output スロット
   - 関数: CitationExtractor.verify
   - 出力: task2_output スロット

7. Task3実行
   - 入力: task2_output スロット
   - 関数: ContextSummarizer
   - 出力: task3_output スロット (最終結果)

8. 結果の返却
```

### メモリフロー

```
割り当て → 使用 → 変換 → 削除/アーカイブ
   ↓       ↓      ↓        ↓
CONTEXT  READ  UPDATE   CLEANUP
スロット  操作   操作      操作
```

## 拡張ポイント

### 1. 新しい組み込み関数の追加

```python
class CustomFunction(BuiltInFunction):
    def execute(self, *args, **kwargs):
        # 実装
        pass
    
    def get_signature(self):
        return {...}

# ライブラリに登録
library.register("custom", CustomFunction())
```

### 2. 新しいタスクタイプの追加

```python
class TaskType(Enum):
    # 既存のタイプ...
    CUSTOM_TYPE = "custom_type"  # 新しいタイプ

# TaskExecutorを拡張
class ExtendedTaskExecutor(TaskExecutor):
    def _execute_custom_type(self, task: Task):
        # カスタム実装
        pass
```

### 3. スキルの追加

```python
skill_manager.register_skill(
    skill_id="new_skill",
    name="新機能",
    description="...",
    implementation=implementation_func,
    training_data=[...]
)
```

### 4. カスタムランタイム動作

```python
class CustomRuntime(GenerativeRuntime):
    def custom_cache_strategy(self):
        # カスタムキャッシュ戦略
        pass
```

## パフォーマンス考慮事項

### メモリ効率

**スロット管理**:
- 不要なスロットの自動削除
- タイプ別のライフサイクル管理
- メモリ使用量のモニタリング

```python
# メモリクリーンアップの例
for slot_id in runtime.list_slots_by_type(SlotType.INTERMEDIATE):
    if is_no_longer_needed(slot_id):
        runtime.delete_slot(slot_id)
```

### 実行効率

**タスク並列化の可能性**:
```
Task1 (EXTRACT)
    ↓
Task2A (ANALYZE)  Task2B (VALIDATE)  ← 並列実行可能
    ↓                ↓
    └────────┬───────┘
             ↓
Task3 (GENERATE)
```

**KVキャッシュの最適化**:
- 頻繁にアクセスされるスロットの優先保持
- 古いスロットの自動アーカイブ
- チェックポイント数の制限

### スケーラビリティ

**将来的な拡張**:

1. **分散実行**:
   ```
   タスクを複数のワーカーに分散
   - ワーカー1: Task1, Task2
   - ワーカー2: Task3, Task4
   ```

2. **永続化**:
   ```
   メモリスロット → データベース
   チェックポイント → ファイルシステム
   ```

3. **リアルタイム処理**:
   ```
   ストリーミング入力 → 増分処理 → 部分結果
   ```

## ベストプラクティス

### 1. スロット命名規則

```python
# 明確な命名
"input_document"        ✓
"extracted_citations"   ✓
"temp_1"                ✗

# タイプごとのプレフィックス
"ctx_user_query"        # CONTEXT
"int_processed_data"    # INTERMEDIATE
"out_final_report"      # OUTPUT
"cite_references"       # CITATION
```

### 2. チェックポイントの使用

```python
# 重要な決定点でチェックポイントを作成
checkpoint = runtime.create_checkpoint(
    "before_critical_step",
    "重要な処理の前の状態"
)

# 低信頼度の処理後にバックトラック
if confidence < threshold:
    runtime.restore_checkpoint("before_critical_step")
    # 別のアプローチを試す
```

### 3. CoTの活用

```python
# 複雑なタスクでCoTを使用
cot.add_step("問題理解", "...", confidence=0.95)
cot.add_step("データ収集", "...", confidence=0.90)
cot.add_step("分析", "...", confidence=0.75)  # 低信頼度

# 定期的に信頼度をチェック
if len(cot.get_low_confidence_steps(0.8)) > 0:
    # 再検討または別手法
```

## まとめ

生成コンピューティングは、LLMを従来の「プロンプト」から「プログラム」へと昇華させるアーキテクチャです。

**主要な利点**:
- ✅ 構造化された実行フロー
- ✅ 明示的な状態管理
- ✅ 再利用可能なコンポーネント
- ✅ バックトラックとエラーハンドリング
- ✅ 拡張可能な設計

**Claude Codeとの関連**:
- Skillsは組み込み関数に対応
- planモードはインタプリタ層に対応
- サブエージェント分割はタスク分解に対応

**次世代への展望**:
- LLM APIとの統合
- 分散実行サポート
- LoRAによる動的機能追加
- グラフィカルなワークフローエディタ
