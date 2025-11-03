"""
生成コンピューティング - 統合システム

ランタイム、インタプリタ、組み込み関数を統合した完全なシステム
"""

from typing import Any, Dict, List, Optional
from datetime import datetime
import json

from runtime import GenerativeRuntime, SlotType
from builtin_functions import FunctionLibrary
from interpreter import NaturalLanguageInterpreter, TaskExecutor


class GenerativeComputingSystem:
    """
    生成コンピューティングシステム
    
    LLMを構造化され、プログラミング的に活用するための統合環境
    """
    
    def __init__(self):
        self.runtime = GenerativeRuntime()
        self.function_library = FunctionLibrary()
        self.interpreter = NaturalLanguageInterpreter()
        self.executor = TaskExecutor(self.runtime, self.function_library)
        self.session_id = f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
    def execute_natural_language(
        self, 
        instruction: str,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        自然言語の指示を実行
        
        Args:
            instruction: 自然言語の指示
            context: オプションのコンテキストデータ
            
        Returns:
            実行結果
        """
        # 1. コンテキストを準備
        if context:
            for key, value in context.items():
                self.runtime.allocate_slot(
                    slot_id=f"context_{key}",
                    slot_type=SlotType.CONTEXT,
                    content=value
                )
        
        # 2. 指示を解析してタスクに分解
        tasks = self.interpreter.parse_instruction(instruction)
        
        # 3. 実行計画を作成
        plan = self.interpreter.create_execution_plan(tasks)
        
        # 4. チェックポイントを作成
        checkpoint_id = f"checkpoint_{len(self.runtime.checkpoints)}"
        self.runtime.create_checkpoint(
            checkpoint_id=checkpoint_id,
            description=f"Before executing: {instruction}"
        )
        
        # 5. 実行計画を実行
        results = self.executor.execute_plan(plan)
        
        # 6. 結果をまとめる
        return {
            "session_id": self.session_id,
            "instruction": instruction,
            "execution_plan": self.interpreter.visualize_plan(plan),
            "checkpoint_id": checkpoint_id,
            "results": results,
            "memory_usage": self.runtime.get_memory_usage(),
            "timestamp": datetime.now().isoformat()
        }
    
    def execute_with_cot(
        self,
        instruction: str,
        max_confidence_threshold: float = 0.7
    ) -> Dict[str, Any]:
        """
        CoT（連鎖思考）を使用して実行
        
        低信頼度の思考ステップを検出し、バックトラックできる
        """
        # CoTを初期化
        cot = self.function_library.get("cot")
        
        # 初期ステップ
        cot.add_step(
            description="指示の解析開始",
            reasoning=f"指示: {instruction}",
            confidence=1.0,
            checkpoint_id="start"
        )
        
        # タスクに分解
        tasks = self.interpreter.parse_instruction(instruction)
        cot.add_step(
            description=f"{len(tasks)}個のタスクに分解",
            reasoning="タスク分解完了",
            confidence=0.9
        )
        
        # 実行計画作成
        plan = self.interpreter.create_execution_plan(tasks)
        cot.add_step(
            description="実行計画作成",
            reasoning=f"実行順序: {' -> '.join(plan.execution_order)}",
            confidence=0.85
        )
        
        # チェックポイント作成
        checkpoint_id = f"cot_checkpoint_{len(self.runtime.checkpoints)}"
        self.runtime.create_checkpoint(checkpoint_id, "CoT execution checkpoint")
        
        # 実行
        results = self.executor.execute_plan(plan)
        cot.add_step(
            description="実行完了",
            reasoning=f"{len(results['results'])}個のタスクが完了",
            confidence=0.95
        )
        
        # 低信頼度ステップをチェック
        low_confidence_steps = cot.get_low_confidence_steps(max_confidence_threshold)
        
        return {
            "session_id": self.session_id,
            "instruction": instruction,
            "cot_visualization": cot.visualize(),
            "low_confidence_steps": len(low_confidence_steps),
            "results": results,
            "checkpoint_id": checkpoint_id
        }
    
    def backtrack_and_retry(
        self,
        checkpoint_id: str,
        new_instruction: str
    ) -> Dict[str, Any]:
        """
        チェックポイントに戻って新しい指示で再実行
        """
        # チェックポイントに戻る
        self.runtime.restore_checkpoint(checkpoint_id)
        
        # 新しい指示を実行
        return self.execute_natural_language(new_instruction)
    
    def add_custom_skill(
        self,
        skill_name: str,
        skill_function: Any
    ) -> None:
        """
        カスタムスキルを追加（機能拡張のライブラリ）
        """
        self.function_library.register(skill_name, skill_function)
    
    def export_session(self, filepath: str) -> None:
        """セッション状態をエクスポート"""
        session_data = {
            "session_id": self.session_id,
            "runtime_state": self.runtime.export_state(),
            "available_functions": self.function_library.list_functions(),
            "export_time": datetime.now().isoformat()
        }
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(session_data, f, indent=2, ensure_ascii=False)
    
    def get_system_status(self) -> Dict[str, Any]:
        """システムステータスを取得"""
        return {
            "session_id": self.session_id,
            "runtime": {
                "memory_usage": self.runtime.get_memory_usage(),
                "total_checkpoints": len(self.runtime.checkpoints),
                "execution_history_length": len(self.runtime.execution_history)
            },
            "function_library": {
                "available_functions": len(self.function_library.functions),
                "function_list": [f["name"] for f in self.function_library.list_functions()]
            }
        }


class SkillManager:
    """
    スキルマネージャー
    
    タスク特化型の関数群を管理（InstructLab的な機能ライブラリ）
    """
    
    def __init__(self):
        self.skills: Dict[str, Dict[str, Any]] = {}
    
    def register_skill(
        self,
        skill_id: str,
        name: str,
        description: str,
        implementation: Any,
        training_data: Optional[List[Dict]] = None
    ) -> None:
        """
        新しいスキルを登録
        
        Args:
            skill_id: スキルID
            name: スキル名
            description: 説明
            implementation: 実装（関数またはクラス）
            training_data: 訓練データ（将来的な微調整用）
        """
        self.skills[skill_id] = {
            "name": name,
            "description": description,
            "implementation": implementation,
            "training_data": training_data or [],
            "usage_count": 0,
            "created_at": datetime.now().isoformat()
        }
    
    def get_skill(self, skill_id: str) -> Optional[Dict[str, Any]]:
        """スキルを取得"""
        skill = self.skills.get(skill_id)
        if skill:
            skill["usage_count"] += 1
        return skill
    
    def search_skills(self, query: str) -> List[Dict[str, Any]]:
        """スキルを検索"""
        results = []
        query_lower = query.lower()
        
        for skill_id, skill in self.skills.items():
            if (query_lower in skill["name"].lower() or 
                query_lower in skill["description"].lower()):
                results.append({
                    "skill_id": skill_id,
                    **skill
                })
        
        return results
    
    def generate_training_data_for_skill(
        self,
        skill_id: str,
        examples: List[Dict[str, Any]]
    ) -> List[Dict]:
        """
        スキルのための訓練データを生成（InstructLab的）
        
        Args:
            skill_id: スキルID
            examples: 入力/出力の例
            
        Returns:
            生成された訓練データ
        """
        if skill_id not in self.skills:
            raise ValueError(f"Skill {skill_id} not found")
        
        training_data = []
        
        for example in examples:
            # 訓練データ形式に変換
            training_sample = {
                "instruction": example.get("instruction", ""),
                "input": example.get("input", ""),
                "output": example.get("output", ""),
                "skill_id": skill_id,
                "generated_at": datetime.now().isoformat()
            }
            training_data.append(training_sample)
        
        # スキルに訓練データを追加
        self.skills[skill_id]["training_data"].extend(training_data)
        
        return training_data
    
    def export_skills(self, filepath: str) -> None:
        """スキルライブラリをエクスポート"""
        export_data = {
            "skills": {
                skill_id: {
                    k: v for k, v in skill.items() 
                    if k != "implementation"  # 実装は除外
                }
                for skill_id, skill in self.skills.items()
            },
            "total_skills": len(self.skills),
            "export_time": datetime.now().isoformat()
        }
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, indent=2, ensure_ascii=False)
