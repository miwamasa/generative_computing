"""
生成コンピューティング - インタプリタ

自然言語の指示を構造化し、タスクに分解して実行
"""

from typing import Any, Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import re


class TaskType(Enum):
    """タスクの種類"""
    EXTRACT = "extract"  # 抽出
    TRANSFORM = "transform"  # 変換
    ANALYZE = "analyze"  # 分析
    GENERATE = "generate"  # 生成
    VALIDATE = "validate"  # 検証
    ORCHESTRATE = "orchestrate"  # 統合


@dataclass
class Task:
    """タスクの表現"""
    task_id: str
    task_type: TaskType
    description: str
    input_slots: List[str]
    output_slots: List[str]
    parameters: Dict[str, Any]
    dependencies: List[str] = None
    
    def __post_init__(self):
        if self.dependencies is None:
            self.dependencies = []


@dataclass
class ExecutionPlan:
    """実行計画"""
    plan_id: str
    tasks: List[Task]
    execution_order: List[str]  # task_ids in order


class NaturalLanguageInterpreter:
    """
    自然言語インタプリタ
    
    自然言語の指示を解析し、構造化されたタスクに変換
    """
    
    def __init__(self):
        self.patterns = self._initialize_patterns()
        
    def _initialize_patterns(self) -> Dict[str, List[Tuple[str, TaskType]]]:
        """指示パターンを初期化"""
        return {
            "extract": [
                (r"(.+)から(.+)を抽出", TaskType.EXTRACT),
                (r"(.+)を見つけて", TaskType.EXTRACT),
                (r"(.+)の中から(.+)を取り出", TaskType.EXTRACT),
            ],
            "transform": [
                (r"(.+)を(.+)に変換", TaskType.TRANSFORM),
                (r"(.+)を(.+)する", TaskType.TRANSFORM),
                (r"(.+)の形式を変更", TaskType.TRANSFORM),
            ],
            "analyze": [
                (r"(.+)を分析", TaskType.ANALYZE),
                (r"(.+)について考察", TaskType.ANALYZE),
                (r"(.+)の傾向を調査", TaskType.ANALYZE),
            ],
            "generate": [
                (r"(.+)を生成", TaskType.GENERATE),
                (r"(.+)を作成", TaskType.GENERATE),
                (r"(.+)を書く", TaskType.GENERATE),
            ],
            "validate": [
                (r"(.+)を検証", TaskType.VALIDATE),
                (r"(.+)をチェック", TaskType.VALIDATE),
                (r"(.+)が正しいか確認", TaskType.VALIDATE),
            ]
        }
    
    def parse_instruction(self, instruction: str) -> List[Task]:
        """
        自然言語の指示をタスクに解析
        
        例: "テキストから引用を抽出して、それらを検証し、結果を生成する"
        → 3つのタスク: EXTRACT, VALIDATE, GENERATE
        """
        # 複合指示を分解
        sub_instructions = self._split_compound_instruction(instruction)
        
        tasks = []
        for idx, sub_inst in enumerate(sub_instructions):
            task = self._parse_single_instruction(sub_inst, f"task_{idx}")
            if task:
                tasks.append(task)
        
        # 依存関係を解決
        self._resolve_dependencies(tasks)
        
        return tasks
    
    def _split_compound_instruction(self, instruction: str) -> List[str]:
        """複合指示を分解"""
        # 接続詞で分割
        separators = ['して', 'し、', 'する。', 'の後', 'してから', 'したら']
        
        parts = [instruction]
        for sep in separators:
            new_parts = []
            for part in parts:
                new_parts.extend(part.split(sep))
            parts = new_parts
        
        return [p.strip() for p in parts if p.strip()]
    
    def _parse_single_instruction(self, instruction: str, task_id: str) -> Optional[Task]:
        """単一指示をタスクに変換"""
        for category, patterns in self.patterns.items():
            for pattern, task_type in patterns:
                match = re.search(pattern, instruction)
                if match:
                    return Task(
                        task_id=task_id,
                        task_type=task_type,
                        description=instruction,
                        input_slots=[],  # 後で解決
                        output_slots=[f"{task_id}_output"],
                        parameters={"matched_groups": match.groups()}
                    )
        
        # パターンにマッチしない場合は汎用タスク
        return Task(
            task_id=task_id,
            task_type=TaskType.ORCHESTRATE,
            description=instruction,
            input_slots=[],
            output_slots=[f"{task_id}_output"],
            parameters={}
        )
    
    def _resolve_dependencies(self, tasks: List[Task]) -> None:
        """タスク間の依存関係を解決"""
        for i in range(1, len(tasks)):
            # 前のタスクの出力を現在のタスクの入力とする
            tasks[i].input_slots = tasks[i-1].output_slots.copy()
            tasks[i].dependencies = [tasks[i-1].task_id]
    
    def create_execution_plan(self, tasks: List[Task]) -> ExecutionPlan:
        """実行計画を作成"""
        # トポロジカルソート（簡易版）
        execution_order = []
        completed = set()
        
        while len(completed) < len(tasks):
            for task in tasks:
                if task.task_id not in completed:
                    # すべての依存関係が完了しているか確認
                    if all(dep in completed for dep in task.dependencies):
                        execution_order.append(task.task_id)
                        completed.add(task.task_id)
        
        return ExecutionPlan(
            plan_id=f"plan_{len(tasks)}",
            tasks=tasks,
            execution_order=execution_order
        )
    
    def visualize_plan(self, plan: ExecutionPlan) -> str:
        """実行計画を可視化"""
        lines = ["=== Execution Plan ==="]
        lines.append(f"Plan ID: {plan.plan_id}")
        lines.append(f"Total Tasks: {len(plan.tasks)}")
        lines.append("\nExecution Order:")
        
        task_dict = {t.task_id: t for t in plan.tasks}
        
        for idx, task_id in enumerate(plan.execution_order, 1):
            task = task_dict[task_id]
            lines.append(f"\n{idx}. {task.task_id} ({task.task_type.value})")
            lines.append(f"   Description: {task.description}")
            lines.append(f"   Input Slots: {', '.join(task.input_slots) if task.input_slots else 'None'}")
            lines.append(f"   Output Slots: {', '.join(task.output_slots)}")
            if task.dependencies:
                lines.append(f"   Dependencies: {', '.join(task.dependencies)}")
        
        return "\n".join(lines)


class TaskExecutor:
    """
    タスク実行エンジン
    
    実行計画に基づいてタスクを実行
    """
    
    def __init__(self, runtime, function_library):
        """
        Args:
            runtime: GenerativeRuntime インスタンス
            function_library: FunctionLibrary インスタンス
        """
        self.runtime = runtime
        self.function_library = function_library
        self.execution_results: Dict[str, Any] = {}
    
    def execute_plan(self, plan: ExecutionPlan) -> Dict[str, Any]:
        """実行計画を実行"""
        from runtime import SlotType
        task_dict = {t.task_id: t for t in plan.tasks}
        
        for task_id in plan.execution_order:
            task = task_dict[task_id]
            result = self._execute_task(task)
            self.execution_results[task_id] = result
            
            # 結果をメモリスロットに格納
            for output_slot in task.output_slots:
                self.runtime.allocate_slot(
                    slot_id=output_slot,
                    slot_type=SlotType.OUTPUT,
                    content=result,
                    metadata={"task_id": task_id, "task_type": task.task_type.value}
                )
        
        return {
            "plan_id": plan.plan_id,
            "completed_tasks": len(self.execution_results),
            "results": self.execution_results
        }
    
    def _execute_task(self, task: Task) -> Any:
        """個別タスクを実行"""
        # タスクタイプに応じて適切な組み込み関数を呼び出す
        if task.task_type == TaskType.EXTRACT:
            return self._execute_extract(task)
        elif task.task_type == TaskType.TRANSFORM:
            return self._execute_transform(task)
        elif task.task_type == TaskType.ANALYZE:
            return self._execute_analyze(task)
        elif task.task_type == TaskType.GENERATE:
            return self._execute_generate(task)
        elif task.task_type == TaskType.VALIDATE:
            return self._execute_validate(task)
        else:
            return {"status": "not_implemented", "task": task.description}
    
    def _execute_extract(self, task: Task) -> Any:
        """抽出タスクを実行"""
        # 入力データを取得
        input_data = self._get_input_data(task.input_slots)
        
        # 引用抽出器を使用
        citation_func = self.function_library.get("citation")
        if citation_func and isinstance(input_data, str):
            return citation_func.execute(input_data, verify=False)
        
        return {"extracted": input_data}
    
    def _execute_transform(self, task: Task) -> Any:
        """変換タスクを実行"""
        input_data = self._get_input_data(task.input_slots)
        
        # データ変換パイプラインを使用
        transform_func = self.function_library.get("transform")
        if transform_func:
            # デフォルトのパイプライン
            pipeline = ["strip", "normalize_spaces"]
            return transform_func.execute(input_data, pipeline)
        
        return {"transformed": input_data}
    
    def _execute_analyze(self, task: Task) -> Any:
        """分析タスクを実行"""
        input_data = self._get_input_data(task.input_slots)
        
        # CoTを使って分析
        cot = self.function_library.get("cot")
        if cot:
            cot.add_step(
                description=f"Analyzing: {task.description}",
                reasoning="データを分析中",
                confidence=0.8
            )
        
        return {"analysis": "分析完了", "data": input_data}
    
    def _execute_generate(self, task: Task) -> Any:
        """生成タスクを実行"""
        input_data = self._get_input_data(task.input_slots)
        return {"generated": f"Generated content based on {input_data}"}
    
    def _execute_validate(self, task: Task) -> Any:
        """検証タスクを実行"""
        input_data = self._get_input_data(task.input_slots)
        
        citation_func = self.function_library.get("citation")
        if citation_func and isinstance(input_data, dict) and "citations" in input_data:
            results = []
            for citation in input_data["citations"]:
                results.append(citation_func.verify_citation(citation))
            return {"validation_results": results}
        
        return {"validated": True, "data": input_data}
    
    def _get_input_data(self, slot_ids: List[str]) -> Any:
        """入力スロットからデータを取得"""
        if not slot_ids:
            return None
        
        if len(slot_ids) == 1:
            slot = self.runtime.get_slot(slot_ids[0])
            return slot.content if slot else None
        
        return [
            self.runtime.get_slot(slot_id).content 
            for slot_id in slot_ids 
            if self.runtime.get_slot(slot_id)
        ]
