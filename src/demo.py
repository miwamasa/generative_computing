"""
生成コンピューティング - デモプログラム

システムの使用例を示すデモ
"""

import sys
sys.path.append('/home/claude/generative_computing')

from system import GenerativeComputingSystem, SkillManager
from builtin_functions import BuiltInFunction
from typing import Any, Dict


def demo_basic_execution():
    """基本的な実行のデモ"""
    print("=" * 60)
    print("デモ1: 基本的な自然言語実行")
    print("=" * 60)
    
    # システムを初期化
    gc_system = GenerativeComputingSystem()
    
    # サンプルテキストを用意
    sample_text = """
    機械学習の研究[Smith, 2023]によると、大規模言語モデルは自然言語処理において
    革命的な進歩をもたらしている。"LLMは人間のような理解を示す"という主張もある。
    詳細はhttps://arxiv.org/example を参照。
    """
    
    # 自然言語の指示を実行
    instruction = "テキストから引用を抽出して検証する"
    
    result = gc_system.execute_natural_language(
        instruction=instruction,
        context={"source_text": sample_text}
    )
    
    print(f"\n指示: {instruction}")
    print(f"\nセッションID: {result['session_id']}")
    print(f"\n実行計画:\n{result['execution_plan']}")
    print(f"\nメモリ使用状況: {result['memory_usage']}")
    print(f"\nチェックポイントID: {result['checkpoint_id']}")
    
    return gc_system


def demo_cot_execution():
    """CoT（連鎖思考）を使った実行のデモ"""
    print("\n" + "=" * 60)
    print("デモ2: CoT（連鎖思考）による実行")
    print("=" * 60)
    
    gc_system = GenerativeComputingSystem()
    
    instruction = "データを抽出して分析し、結果を生成する"
    
    result = gc_system.execute_with_cot(instruction)
    
    print(f"\n指示: {instruction}")
    print(f"\n{result['cot_visualization']}")
    print(f"\n低信頼度ステップ: {result['low_confidence_steps']}個")
    
    return gc_system


def demo_backtrack():
    """バックトラックのデモ"""
    print("\n" + "=" * 60)
    print("デモ3: チェックポイントとバックトラック")
    print("=" * 60)
    
    gc_system = GenerativeComputingSystem()
    
    # 最初の実行
    result1 = gc_system.execute_natural_language(
        "テキストを分析する",
        context={"text": "サンプルテキスト"}
    )
    checkpoint_id = result1['checkpoint_id']
    print(f"\n最初の実行完了 - チェックポイント: {checkpoint_id}")
    
    # 追加の実行
    gc_system.execute_natural_language("データを変換する")
    print(f"追加実行完了 - メモリスロット数: {gc_system.runtime.get_memory_usage()['total_slots']}")
    
    # バックトラック
    print(f"\nチェックポイント {checkpoint_id} に戻ります...")
    result2 = gc_system.backtrack_and_retry(
        checkpoint_id=checkpoint_id,
        new_instruction="テキストを抽出する"
    )
    print(f"バックトラック後 - メモリスロット数: {result2['memory_usage']['total_slots']}")
    
    return gc_system


def demo_custom_skill():
    """カスタムスキルの追加デモ"""
    print("\n" + "=" * 60)
    print("デモ4: カスタムスキルの追加（機能拡張ライブラリ）")
    print("=" * 60)
    
    # カスタムスキルを定義
    class SentimentAnalysisSkill(BuiltInFunction):
        """感情分析スキル"""
        
        def execute(self, text: str) -> Dict[str, Any]:
            # 簡易的な感情分析（実際はLLMを使用）
            positive_words = ['良い', '素晴らしい', '最高', '優れた']
            negative_words = ['悪い', '最悪', '問題', '困難']
            
            positive_count = sum(1 for word in positive_words if word in text)
            negative_count = sum(1 for word in negative_words if word in text)
            
            if positive_count > negative_count:
                sentiment = "positive"
            elif negative_count > positive_count:
                sentiment = "negative"
            else:
                sentiment = "neutral"
            
            return {
                "sentiment": sentiment,
                "positive_score": positive_count,
                "negative_score": negative_count
            }
        
        def get_signature(self) -> Dict[str, Any]:
            return {
                "name": "sentiment_analysis",
                "params": ["text"],
                "description": "テキストの感情分析"
            }
    
    gc_system = GenerativeComputingSystem()
    
    # スキルを追加
    sentiment_skill = SentimentAnalysisSkill()
    gc_system.add_custom_skill("sentiment", sentiment_skill)
    
    print("\nカスタムスキル 'sentiment' を追加しました")
    print(f"利用可能な関数: {gc_system.get_system_status()['function_library']['function_list']}")
    
    # スキルを使用
    result = sentiment_skill.execute("これは素晴らしい結果です")
    print(f"\n感情分析結果: {result}")
    
    return gc_system


def demo_skill_library():
    """スキルライブラリの管理デモ"""
    print("\n" + "=" * 60)
    print("デモ5: スキルライブラリの管理（InstructLab的）")
    print("=" * 60)
    
    skill_manager = SkillManager()
    
    # スキルを登録
    skill_manager.register_skill(
        skill_id="summarization",
        name="テキスト要約",
        description="長文テキストを要約する",
        implementation=lambda x: x[:100] + "..."
    )
    
    skill_manager.register_skill(
        skill_id="translation",
        name="翻訳",
        description="英語を日本語に翻訳する",
        implementation=lambda x: f"[翻訳] {x}"
    )
    
    print("\n登録されたスキル:")
    for skill_id, skill in skill_manager.skills.items():
        print(f"  - {skill_id}: {skill['name']}")
        print(f"    説明: {skill['description']}")
    
    # スキルを検索
    print("\n'要約'で検索:")
    results = skill_manager.search_skills("要約")
    for result in results:
        print(f"  - {result['skill_id']}: {result['name']}")
    
    # 訓練データを生成
    print("\n訓練データを生成:")
    examples = [
        {
            "instruction": "次のテキストを要約してください",
            "input": "長い文章...",
            "output": "要約された文章"
        }
    ]
    training_data = skill_manager.generate_training_data_for_skill(
        "summarization",
        examples
    )
    print(f"  生成されたデータ数: {len(training_data)}")
    
    # エクスポート
    skill_manager.export_skills("/tmp/skills_library.json")
    print("\nスキルライブラリをエクスポートしました: /tmp/skills_library.json")
    
    return skill_manager


def demo_memory_management():
    """高度なメモリ管理のデモ"""
    print("\n" + "=" * 60)
    print("デモ6: 高度なメモリ管理（KVキャッシュ）")
    print("=" * 60)
    
    gc_system = GenerativeComputingSystem()
    runtime = gc_system.runtime
    
    # 各種スロットを割り当て
    from runtime import SlotType
    
    runtime.allocate_slot("ctx_1", SlotType.CONTEXT, "コンテキストデータ1")
    runtime.allocate_slot("ctx_2", SlotType.CONTEXT, "コンテキストデータ2")
    runtime.allocate_slot("work_1", SlotType.INTERMEDIATE, {"step": 1, "data": [1, 2, 3]})
    runtime.allocate_slot("output_1", SlotType.OUTPUT, "最終結果")
    
    print("\nメモリスロットを割り当て:")
    print(f"  総スロット数: {runtime.get_memory_usage()['total_slots']}")
    print(f"  タイプ別: {runtime.get_memory_usage()['by_type']}")
    
    # スロットの変換
    print("\nスロット変換を実行:")
    runtime.transform_slot("work_1", lambda x: {**x, "processed": True})
    print(f"  変換後: {runtime.get_slot('work_1').content}")
    
    # 不要なスロットを削除
    print("\nコンテキストスロットをクリーンアップ:")
    runtime.delete_slot("ctx_1")
    runtime.delete_slot("ctx_2")
    print(f"  残りスロット数: {runtime.get_memory_usage()['total_slots']}")
    
    # 実行履歴
    print("\n実行履歴:")
    for action in runtime.execution_history[-5:]:
        print(f"  - {action['action']}: {action['details']}")
    
    return gc_system


def demo_workflow_orchestration():
    """ワークフローオーケストレーションのデモ"""
    print("\n" + "=" * 60)
    print("デモ7: ワークフローオーケストレーション")
    print("=" * 60)
    
    gc_system = GenerativeComputingSystem()
    
    # 複雑な複合指示
    complex_instruction = """
    論文からキーワードを抽出して、
    それを分析し、
    類似研究を検索して、
    最終的にレポートを生成する
    """
    
    result = gc_system.execute_natural_language(complex_instruction)
    
    print(f"\n複合指示:\n{complex_instruction}")
    print(f"\n実行計画:\n{result['execution_plan']}")
    print(f"\n完了したタスク数: {result['results']['completed_tasks']}")
    
    # セッションをエクスポート
    gc_system.export_session("/tmp/gc_session.json")
    print("\nセッション状態をエクスポートしました: /tmp/gc_session.json")
    
    return gc_system


def main():
    """メインデモ関数"""
    print("\n")
    print("╔" + "=" * 58 + "╗")
    print("║" + " " * 10 + "生成コンピューティング デモ" + " " * 19 + "║")
    print("╚" + "=" * 58 + "╝")
    
    try:
        # 各デモを実行
        demo_basic_execution()
        demo_cot_execution()
        demo_backtrack()
        demo_custom_skill()
        demo_skill_library()
        demo_memory_management()
        demo_workflow_orchestration()
        
        print("\n" + "=" * 60)
        print("全デモが完了しました！")
        print("=" * 60)
        
    except Exception as e:
        print(f"\nエラーが発生しました: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
