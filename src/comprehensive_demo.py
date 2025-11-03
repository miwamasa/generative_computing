"""
生成コンピューティング - 包括的統合デモ

全機能を網羅した完全なデモンストレーション
"""

import sys
sys.path.append('/mnt/user-data/outputs/generative_computing')

import time
from datetime import datetime


def print_section_header(title: str, subtitle: str = ""):
    """セクションヘッダーを表示"""
    print("\n" + "╔" + "═" * 68 + "╗")
    print("║" + f" {title:^66} " + "║")
    if subtitle:
        print("║" + f" {subtitle:^66} " + "║")
    print("╚" + "═" * 68 + "╝\n")


def demo_1_basic_usage():
    """デモ1: 基本的な使い方"""
    from system import GenerativeComputingSystem
    
    print_section_header("デモ1", "基本的な使い方")
    
    # システムを初期化
    gc = GenerativeComputingSystem()
    print(f"✓ システム初期化完了")
    print(f"  セッションID: {gc.session_id}")
    
    # シンプルな実行
    print("\n実行中: 'データを抽出して分析する'")
    result = gc.execute_natural_language(
        "データを抽出して分析する",
        context={"data": "サンプルデータ: 重要な情報1, 情報2, 情報3"}
    )
    
    print(f"✓ 実行完了")
    print(f"  完了タスク数: {result['results']['completed_tasks']}")
    print(f"  メモリスロット: {result['memory_usage']['total_slots']}")
    
    return gc


def demo_2_memory_management():
    """デモ2: メモリ管理"""
    from runtime import GenerativeRuntime, SlotType
    
    print_section_header("デモ2", "スロットベースのメモリ管理")
    
    runtime = GenerativeRuntime()
    
    # スロットを作成
    print("スロットを割り当て中...")
    runtime.allocate_slot("user_input", SlotType.CONTEXT, "ユーザーの入力")
    runtime.allocate_slot("temp_data", SlotType.INTERMEDIATE, [1, 2, 3, 4, 5])
    runtime.allocate_slot("result", SlotType.OUTPUT, {"status": "success"})
    
    print(f"✓ 3つのスロットを作成")
    
    # スロットを変換
    print("\nスロットを変換中...")
    runtime.transform_slot("temp_data", lambda x: [i * 2 for i in x])
    
    transformed = runtime.get_slot("temp_data")
    print(f"✓ 変換完了: {transformed.content}")
    
    # メモリ使用状況
    usage = runtime.get_memory_usage()
    print(f"\nメモリ使用状況:")
    for slot_type, count in usage['by_type'].items():
        print(f"  {slot_type}: {count}個")
    
    return runtime


def demo_3_checkpoints():
    """デモ3: チェックポイントとバックトラック"""
    from system import GenerativeComputingSystem
    from runtime import SlotType
    
    print_section_header("デモ3", "チェックポイントとバックトラック")
    
    gc = GenerativeComputingSystem()
    
    # 初期チェックポイント
    print("チェックポイント1を作成...")
    cp1 = gc.runtime.create_checkpoint("cp1", "初期状態")
    print(f"✓ {cp1.checkpoint_id} 作成")
    
    # 処理1
    print("\n処理1を実行...")
    gc.runtime.allocate_slot("data1", SlotType.CONTEXT, "データ1")
    print(f"✓ スロット数: {gc.runtime.get_memory_usage()['total_slots']}")
    
    # 2つ目のチェックポイント
    print("\nチェックポイント2を作成...")
    cp2 = gc.runtime.create_checkpoint("cp2", "処理1後")
    print(f"✓ {cp2.checkpoint_id} 作成")
    
    # 処理2
    print("\n処理2を実行...")
    gc.runtime.allocate_slot("data2", SlotType.CONTEXT, "データ2")
    print(f"✓ スロット数: {gc.runtime.get_memory_usage()['total_slots']}")
    
    # バックトラック
    print("\nチェックポイント1に復元...")
    gc.runtime.restore_checkpoint("cp1")
    print(f"✓ 復元完了")
    print(f"  スロット数: {gc.runtime.get_memory_usage()['total_slots']}")
    
    return gc


def demo_4_cot():
    """デモ4: CoT（連鎖思考）"""
    from builtin_functions import ChainOfThought
    
    print_section_header("デモ4", "CoT（連鎖思考）管理")
    
    cot = ChainOfThought()
    
    print("思考ステップを追加中...")
    
    # 複数のステップを追加
    steps_data = [
        ("問題の理解", "タスクの要件を分析", 0.95),
        ("データ収集", "必要な情報を集める", 0.90),
        ("初期分析", "データの傾向を確認", 0.75),
        ("仮説の設定", "可能性のある説明を考える", 0.65),  # 低信頼度
        ("検証", "仮説を検証する", 0.85),
        ("結論", "最終的な答えを導出", 0.92)
    ]
    
    for desc, reasoning, conf in steps_data:
        cot.add_step(desc, reasoning, conf)
        print(f"  Step {len(cot.thought_chain)-1}: {desc} (信頼度: {conf})")
    
    # 低信頼度ステップを検出
    print("\n低信頼度ステップを検出...")
    low_conf = cot.get_low_confidence_steps(threshold=0.7)
    print(f"✓ {len(low_conf)}個の低信頼度ステップ")
    
    for step in low_conf:
        print(f"  Step {step.step_id}: {step.description} ({step.confidence})")
    
    # バックトラック
    if low_conf:
        print(f"\nStep {low_conf[0].step_id - 1} にバックトラック...")
        cot.backtrack_to_step(low_conf[0].step_id - 1)
        print(f"✓ 現在のステップ: {cot.current_step}")
    
    return cot


def demo_5_custom_functions():
    """デモ5: カスタム関数"""
    from system import GenerativeComputingSystem
    from builtin_functions import BuiltInFunction
    
    print_section_header("デモ5", "カスタムスキルの追加")
    
    # カスタム関数を定義
    class TextAnalyzer(BuiltInFunction):
        def execute(self, text: str):
            words = text.split()
            return {
                "word_count": len(words),
                "char_count": len(text),
                "unique_words": len(set(words))
            }
        
        def get_signature(self):
            return {
                "name": "text_analyzer",
                "description": "テキストの統計情報を分析"
            }
    
    gc = GenerativeComputingSystem()
    
    print("カスタムスキルを追加...")
    gc.add_custom_skill("text_analyzer", TextAnalyzer())
    print("✓ text_analyzer を追加")
    
    # 使用
    print("\nカスタムスキルを実行...")
    analyzer = gc.function_library.get("text_analyzer")
    result = analyzer.execute("これはテストテキストです サンプル データ")
    
    print(f"✓ 分析完了:")
    for key, value in result.items():
        print(f"  {key}: {value}")
    
    return gc


def demo_6_llm_integration():
    """デモ6: LLM統合"""
    from llm_integration import LLMIntegratedSystem, MockLLMProvider
    
    print_section_header("デモ6", "LLM統合システム")
    
    # モックLLMを使用
    llm = MockLLMProvider()
    system = LLMIntegratedSystem(llm)
    
    print("LLM統合システムで実行中...")
    
    sample_text = """
    人工知能技術は目覚ましい発展を遂げています。
    特に大規模言語モデルは、自然言語処理に革命をもたらしました。
    """
    
    # 情報抽出
    print("\n1. 情報抽出")
    extracted = system.enhanced_functions.extract_information(
        sample_text,
        "キーワード"
    )
    print(f"✓ {len(extracted)}個のキーワードを抽出")
    for item in extracted[:3]:
        print(f"  - {item}")
    
    # 感情分析
    print("\n2. 感情分析")
    sentiment = system.enhanced_functions.analyze_sentiment(sample_text)
    print(f"✓ 感情: {sentiment.get('sentiment', 'N/A')}")
    
    # 要約
    print("\n3. 要約生成")
    summary = system.enhanced_functions.generate_summary(sample_text, max_length=50)
    print(f"✓ 要約: {summary[:80]}...")
    
    print(f"\n総LLM呼び出し: {llm.call_count}回")
    
    return system


def demo_7_use_cases():
    """デモ7: 実用的なユースケース"""
    from use_cases import ResearchPaperAnalyzer, BusinessReportGenerator
    
    print_section_header("デモ7", "実用的なユースケース")
    
    # 論文分析
    print("【ユースケース1: 研究論文分析】\n")
    analyzer = ResearchPaperAnalyzer()
    
    papers = [
        {
            "title": "機械学習の最新手法",
            "abstract": "本研究では、最新の機械学習アルゴリズムを比較評価します。"
        },
        {
            "title": "深層学習の応用",
            "abstract": "深層学習技術の産業応用について議論します。"
        }
    ]
    
    print(f"  {len(papers)}本の論文を分析中...")
    analysis = analyzer.analyze_papers(papers, analysis_type="summary")
    print(f"✓ 分析完了")
    print(f"  共通キーワード: {len(analysis['comparison']['top_keywords'])}個")
    
    # ビジネスレポート
    print("\n【ユースケース2: ビジネスレポート生成】\n")
    generator = BusinessReportGenerator()
    
    data = {
        "revenue": 5000000,
        "growth_rate": 12.5,
        "customer_count": 150,
        "satisfaction_score": 78
    }
    
    print("  レポートを生成中...")
    report = generator.generate_report(data, "quarterly")
    print(f"✓ レポート生成完了")
    print(f"  推奨事項: {len(report['recommendations'])}件")
    
    return analyzer, generator


def demo_8_visualization():
    """デモ8: 可視化"""
    from system import GenerativeComputingSystem
    from visualization import DashboardGenerator
    
    print_section_header("デモ8", "可視化とモニタリング")
    
    gc = GenerativeComputingSystem()
    dashboard = DashboardGenerator()
    
    # いくつかの操作を実行
    print("操作を実行中...")
    
    start = time.time()
    gc.execute_natural_language("データを処理する")
    exec_time = time.time() - start
    
    dashboard.monitor.record_execution(
        exec_time,
        gc.runtime.get_memory_usage()['total_slots'],
        2
    )
    
    print(f"✓ 実行完了 ({exec_time:.3f}秒)")
    
    # ダッシュボードを表示
    print("\n" + "─" * 70)
    print(dashboard.generate_dashboard(gc, include_sections=['system', 'memory']))
    
    return dashboard


def demo_9_performance():
    """デモ9: パフォーマンステスト"""
    from system import GenerativeComputingSystem
    from visualization import PerformanceMonitor
    
    print_section_header("デモ9", "パフォーマンステスト")
    
    gc = GenerativeComputingSystem()
    monitor = PerformanceMonitor()
    monitor.start_monitoring()
    
    # 複数回実行してパフォーマンスを測定
    test_cases = [
        ("シンプルなタスク", "データを抽出する", 1),
        ("中程度のタスク", "データを抽出して分析する", 2),
        ("複雑なタスク", "データを抽出して分析し、レポートを生成する", 3)
    ]
    
    print("パフォーマンステストを実行中...\n")
    
    for name, instruction, expected_tasks in test_cases:
        print(f"  {name}...")
        
        start = time.time()
        result = gc.execute_natural_language(instruction)
        exec_time = time.time() - start
        
        monitor.record_execution(
            exec_time,
            gc.runtime.get_memory_usage()['total_slots'],
            expected_tasks
        )
        
        print(f"    ✓ 完了 ({exec_time:.3f}秒)")
    
    # 統計を表示
    print("\n" + monitor.generate_report())
    
    return monitor


def demo_10_complete_workflow():
    """デモ10: 完全なワークフロー"""
    from system import GenerativeComputingSystem
    from runtime import SlotType
    
    print_section_header("デモ10", "完全なエンドツーエンドワークフロー")
    
    gc = GenerativeComputingSystem()
    
    print("【シナリオ: データ分析プロジェクト】\n")
    
    # ステップ1: プロジェクト開始
    print("ステップ1: プロジェクト初期化")
    checkpoint_start = gc.runtime.create_checkpoint("project_start", "プロジェクト開始")
    gc.runtime.allocate_slot("project_config", SlotType.CONTEXT, {
        "name": "データ分析プロジェクト",
        "deadline": "2025-12-31"
    })
    print("  ✓ プロジェクト設定完了")
    
    # ステップ2: データ収集
    print("\nステップ2: データ収集と前処理")
    result2 = gc.execute_natural_language(
        "データを収集して前処理する",
        context={"source": "database"}
    )
    checkpoint_data = gc.runtime.create_checkpoint("after_data", "データ準備完了")
    print(f"  ✓ データ準備完了")
    
    # ステップ3: 分析（CoT使用）
    print("\nステップ3: データ分析（CoT使用）")
    result3 = gc.execute_with_cot(
        "データの傾向を分析し、インサイトを抽出する",
        max_confidence_threshold=0.7
    )
    print(f"  ✓ 分析完了")
    print(f"  低信頼度ステップ: {result3['low_confidence_steps']}個")
    
    # ステップ4: レポート生成
    print("\nステップ4: 最終レポート生成")
    result4 = gc.execute_natural_language(
        "分析結果をまとめてレポートを作成する"
    )
    print(f"  ✓ レポート生成完了")
    
    # プロジェクトサマリー
    print("\n【プロジェクトサマリー】")
    print(f"  総実行タスク: {sum([r['results']['completed_tasks'] for r in [result2, result4]])}")
    print(f"  メモリ使用: {gc.runtime.get_memory_usage()['total_slots']}スロット")
    print(f"  チェックポイント: {len(gc.runtime.checkpoints)}個")
    print(f"  実行履歴: {len(gc.runtime.execution_history)}アクション")
    
    # セッションをエクスポート
    export_path = "/tmp/project_session.json"
    gc.export_session(export_path)
    print(f"\n  ✓ セッションをエクスポート: {export_path}")
    
    return gc


def main():
    """メインデモ関数"""
    start_time = datetime.now()
    
    print("\n" + "╔" + "═" * 68 + "╗")
    print("║" + " " * 68 + "║")
    print("║" + "       生成コンピューティング - 包括的統合デモ       ".center(68) + "║")
    print("║" + " " * 68 + "║")
    print("║" + f"  開始時刻: {start_time.strftime('%Y-%m-%d %H:%M:%S')}  ".center(68) + "║")
    print("║" + " " * 68 + "║")
    print("╚" + "═" * 68 + "╝")
    
    demos = [
        ("基本的な使い方", demo_1_basic_usage),
        ("メモリ管理", demo_2_memory_management),
        ("チェックポイント", demo_3_checkpoints),
        ("CoT（連鎖思考）", demo_4_cot),
        ("カスタム関数", demo_5_custom_functions),
        ("LLM統合", demo_6_llm_integration),
        ("実用ユースケース", demo_7_use_cases),
        ("可視化", demo_8_visualization),
        ("パフォーマンス", demo_9_performance),
        ("完全ワークフロー", demo_10_complete_workflow)
    ]
    
    results = {}
    
    for i, (name, demo_func) in enumerate(demos, 1):
        try:
            print(f"\n{'='*70}")
            print(f"進行状況: {i}/{len(demos)}")
            print(f"{'='*70}")
            
            result = demo_func()
            results[name] = {"status": "success", "result": result}
            
            time.sleep(0.5)  # デモ間の小休止
            
        except Exception as e:
            print(f"\n❌ エラー: {e}")
            results[name] = {"status": "error", "error": str(e)}
            import traceback
            traceback.print_exc()
    
    # 最終サマリー
    end_time = datetime.now()
    duration = (end_time - start_time).total_seconds()
    
    print("\n" + "╔" + "═" * 68 + "╗")
    print("║" + " " * 68 + "║")
    print("║" + "                  デモ完了サマリー                  ".center(68) + "║")
    print("║" + " " * 68 + "║")
    print("╚" + "═" * 68 + "╝")
    
    print(f"\n総実行時間: {duration:.2f}秒")
    print(f"総デモ数: {len(demos)}")
    
    success_count = sum(1 for r in results.values() if r['status'] == 'success')
    print(f"成功: {success_count}/{len(demos)}")
    
    if success_count < len(demos):
        print("\n失敗したデモ:")
        for name, result in results.items():
            if result['status'] == 'error':
                print(f"  ❌ {name}: {result['error']}")
    
    print("\n" + "═" * 70)
    print("全デモが完了しました！")
    print("═" * 70)
    
    print("\n📚 次のステップ:")
    print("  1. README.md - プロジェクト概要を確認")
    print("  2. TUTORIAL.md - 詳細なチュートリアルを学習")
    print("  3. ARCHITECTURE.md - アーキテクチャを理解")
    print("  4. 独自のユースケースを実装してみる")
    
    print("\n✨ 生成コンピューティングの世界へようこそ！")


if __name__ == "__main__":
    main()
