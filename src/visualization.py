"""
生成コンピューティング - 可視化とモニタリング

システムの状態と実行フローを可視化
"""

import sys
sys.path.append('/mnt/user-data/outputs/generative_computing')

from typing import Dict, List, Any, Optional
from datetime import datetime
import json


class ExecutionVisualizer:
    """
    実行フローの可視化
    
    タスクの実行順序、依存関係、タイミングを視覚化
    """
    
    def __init__(self):
        self.execution_data: List[Dict] = []
    
    def visualize_execution_plan(self, plan) -> str:
        """実行計画をASCIIアートで可視化"""
        lines = []
        lines.append("┌" + "─" * 58 + "┐")
        lines.append("│" + " " * 18 + "実行計画" + " " * 32 + "│")
        lines.append("└" + "─" * 58 + "┘")
        lines.append("")
        
        task_dict = {t.task_id: t for t in plan.tasks}
        
        for idx, task_id in enumerate(plan.execution_order, 1):
            task = task_dict[task_id]
            
            # タスクボックス
            lines.append(f"  [{idx}] {task.task_id}")
            lines.append(f"  ┌{'─' * 50}┐")
            lines.append(f"  │ Type: {task.task_type.value:<43}│")
            lines.append(f"  │ Desc: {task.description[:42]:<42}│")
            
            if task.input_slots:
                inputs = ", ".join(task.input_slots[:2])
                if len(task.input_slots) > 2:
                    inputs += "..."
                lines.append(f"  │ Input: {inputs:<42}│")
            
            outputs = ", ".join(task.output_slots[:2])
            lines.append(f"  │ Output: {outputs:<41}│")
            lines.append(f"  └{'─' * 50}┘")
            
            # 依存関係の矢印
            if idx < len(plan.execution_order):
                lines.append("       │")
                lines.append("       ↓")
            
            lines.append("")
        
        return "\n".join(lines)
    
    def visualize_memory_state(self, runtime) -> str:
        """メモリ状態を可視化"""
        usage = runtime.get_memory_usage()
        
        lines = []
        lines.append("┌" + "─" * 58 + "┐")
        lines.append("│" + " " * 20 + "メモリ状態" + " " * 28 + "│")
        lines.append("└" + "─" * 58 + "┘")
        lines.append("")
        
        lines.append(f"  総スロット数: {usage['total_slots']}")
        lines.append(f"  チェックポイント数: {usage['checkpoints']}")
        lines.append("")
        lines.append("  スロットタイプ別:")
        
        # タイプ別の棒グラフ
        max_count = max(usage['by_type'].values()) if usage['by_type'] else 1
        
        for slot_type, count in usage['by_type'].items():
            bar_length = int((count / max_count) * 30) if max_count > 0 else 0
            bar = "█" * bar_length
            lines.append(f"    {slot_type:12} │{bar} {count}")
        
        lines.append("")
        
        # 最近のスロット
        lines.append("  最近のスロット:")
        recent_slots = list(runtime.memory_slots.values())[-3:]
        for slot in recent_slots:
            content_preview = str(slot.content)[:30]
            lines.append(f"    • {slot.slot_id}: {content_preview}...")
        
        return "\n".join(lines)
    
    def visualize_cot(self, cot) -> str:
        """CoT（連鎖思考）を可視化"""
        lines = []
        lines.append("┌" + "─" * 58 + "┐")
        lines.append("│" + " " * 18 + "連鎖思考" + " " * 32 + "│")
        lines.append("└" + "─" * 58 + "┘")
        lines.append("")
        
        for step in cot.thought_chain:
            is_current = step.step_id == cot.current_step
            marker = "►" if is_current else " "
            
            # 信頼度バー
            conf_level = int(step.confidence * 10)
            conf_bar = "●" * conf_level + "○" * (10 - conf_level)
            
            lines.append(f"{marker} Step {step.step_id}")
            lines.append(f"  ├─ {step.description}")
            lines.append(f"  ├─ 信頼度: [{conf_bar}] {step.confidence:.2f}")
            
            if step.checkpoint_id:
                lines.append(f"  └─ CP: {step.checkpoint_id}")
            else:
                lines.append(f"  └─")
            
            lines.append("")
        
        # 低信頼度の警告
        low_conf = cot.get_low_confidence_steps(0.7)
        if low_conf:
            lines.append(f"  ⚠ 低信頼度ステップ: {len(low_conf)}個")
            for step in low_conf:
                lines.append(f"    - Step {step.step_id}: {step.confidence:.2f}")
        
        return "\n".join(lines)
    
    def create_timeline(self, execution_history: List[Dict]) -> str:
        """実行履歴のタイムラインを作成"""
        lines = []
        lines.append("┌" + "─" * 58 + "┐")
        lines.append("│" + " " * 16 + "実行タイムライン" + " " * 26 + "│")
        lines.append("└" + "─" * 58 + "┘")
        lines.append("")
        
        if not execution_history:
            lines.append("  実行履歴なし")
            return "\n".join(lines)
        
        for i, action in enumerate(execution_history[-10:], 1):  # 最新10件
            action_name = action.get('action', 'unknown')
            timestamp = action.get('timestamp', '')
            
            # アクションアイコン
            icon = {
                'allocate_slot': '🔵',
                'update_slot': '🔄',
                'delete_slot': '🗑',
                'transform_slot': '⚡',
                'create_checkpoint': '💾',
                'restore_checkpoint': '⏮'
            }.get(action_name, '•')
            
            lines.append(f"  {i:2}. {icon} {action_name}")
            
            # 詳細
            if 'details' in action:
                for key, value in list(action['details'].items())[:2]:
                    lines.append(f"      └─ {key}: {value}")
        
        return "\n".join(lines)


class PerformanceMonitor:
    """
    パフォーマンスモニター
    
    システムの性能を追跡・分析
    """
    
    def __init__(self):
        self.metrics: Dict[str, List[float]] = {
            'execution_time': [],
            'memory_usage': [],
            'task_count': [],
            'llm_calls': []
        }
        self.start_time: Optional[datetime] = None
    
    def start_monitoring(self):
        """モニタリング開始"""
        self.start_time = datetime.now()
    
    def record_execution(
        self,
        execution_time: float,
        memory_slots: int,
        task_count: int,
        llm_calls: int = 0
    ):
        """実行メトリクスを記録"""
        self.metrics['execution_time'].append(execution_time)
        self.metrics['memory_usage'].append(memory_slots)
        self.metrics['task_count'].append(task_count)
        self.metrics['llm_calls'].append(llm_calls)
    
    def get_statistics(self) -> Dict[str, Any]:
        """統計情報を取得"""
        stats = {}
        
        for metric_name, values in self.metrics.items():
            if values:
                stats[metric_name] = {
                    'count': len(values),
                    'min': min(values),
                    'max': max(values),
                    'avg': sum(values) / len(values),
                    'total': sum(values)
                }
            else:
                stats[metric_name] = {
                    'count': 0,
                    'min': 0,
                    'max': 0,
                    'avg': 0,
                    'total': 0
                }
        
        return stats
    
    def generate_report(self) -> str:
        """パフォーマンスレポートを生成"""
        stats = self.get_statistics()
        
        lines = []
        lines.append("╔" + "═" * 58 + "╗")
        lines.append("║" + " " * 15 + "パフォーマンスレポート" + " " * 21 + "║")
        lines.append("╚" + "═" * 58 + "╝")
        lines.append("")
        
        # 実行時間
        exec_stats = stats['execution_time']
        lines.append("📊 実行時間:")
        lines.append(f"  平均: {exec_stats['avg']:.3f}秒")
        lines.append(f"  最小: {exec_stats['min']:.3f}秒")
        lines.append(f"  最大: {exec_stats['max']:.3f}秒")
        lines.append(f"  合計: {exec_stats['total']:.3f}秒")
        lines.append("")
        
        # メモリ使用
        mem_stats = stats['memory_usage']
        lines.append("💾 メモリ使用:")
        lines.append(f"  平均スロット数: {mem_stats['avg']:.1f}")
        lines.append(f"  最大スロット数: {int(mem_stats['max'])}")
        lines.append("")
        
        # タスク数
        task_stats = stats['task_count']
        lines.append("📋 タスク処理:")
        lines.append(f"  総実行回数: {exec_stats['count']}")
        lines.append(f"  総タスク数: {int(task_stats['total'])}")
        lines.append(f"  平均タスク数: {task_stats['avg']:.1f}")
        lines.append("")
        
        # LLM呼び出し
        llm_stats = stats['llm_calls']
        if llm_stats['total'] > 0:
            lines.append("🤖 LLM呼び出し:")
            lines.append(f"  総呼び出し数: {int(llm_stats['total'])}")
            lines.append(f"  平均: {llm_stats['avg']:.1f}/実行")
            lines.append("")
        
        # 効率指標
        if exec_stats['count'] > 0 and task_stats['total'] > 0:
            efficiency = task_stats['total'] / exec_stats['total']
            lines.append("⚡ 効率指標:")
            lines.append(f"  タスク処理速度: {efficiency:.2f} tasks/sec")
        
        return "\n".join(lines)


class DashboardGenerator:
    """
    ダッシュボードジェネレーター
    
    システム全体の状態を一覧表示
    """
    
    def __init__(self):
        self.visualizer = ExecutionVisualizer()
        self.monitor = PerformanceMonitor()
    
    def generate_dashboard(
        self,
        gc_system,
        include_sections: Optional[List[str]] = None
    ) -> str:
        """
        総合ダッシュボードを生成
        
        Args:
            gc_system: GenerativeComputingSystemインスタンス
            include_sections: 含めるセクション（Noneで全て）
        """
        all_sections = ['header', 'system', 'memory', 'history', 'performance']
        sections = include_sections or all_sections
        
        lines = []
        
        # ヘッダー
        if 'header' in sections:
            lines.append("")
            lines.append("╔" + "═" * 66 + "╗")
            lines.append("║" + " " * 15 + "生成コンピューティング ダッシュボード" + " " * 13 + "║")
            lines.append("╚" + "═" * 66 + "╝")
            lines.append("")
        
        # システム状態
        if 'system' in sections:
            status = gc_system.get_system_status()
            lines.append("┌─ システム状態 " + "─" * 50 + "┐")
            lines.append(f"│ セッションID: {status['session_id']:<43}│")
            lines.append(f"│ 実行履歴: {status['runtime']['execution_history_length']}件{' ' * 45}│")
            lines.append(f"│ 利用可能関数: {status['function_library']['available_functions']}個{' ' * 42}│")
            lines.append("└" + "─" * 66 + "┘")
            lines.append("")
        
        # メモリ状態
        if 'memory' in sections:
            memory_viz = self.visualizer.visualize_memory_state(gc_system.runtime)
            lines.append(memory_viz)
            lines.append("")
        
        # 実行履歴
        if 'history' in sections:
            timeline = self.visualizer.create_timeline(
                gc_system.runtime.execution_history
            )
            lines.append(timeline)
            lines.append("")
        
        # パフォーマンス
        if 'performance' in sections and self.monitor.metrics['execution_time']:
            perf_report = self.monitor.generate_report()
            lines.append(perf_report)
            lines.append("")
        
        return "\n".join(lines)
    
    def export_dashboard(
        self,
        gc_system,
        filepath: str,
        format: str = 'txt'
    ):
        """ダッシュボードをファイルにエクスポート"""
        dashboard = self.generate_dashboard(gc_system)
        
        if format == 'txt':
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(dashboard)
        
        elif format == 'json':
            data = {
                'session_id': gc_system.session_id,
                'timestamp': datetime.now().isoformat(),
                'system_status': gc_system.get_system_status(),
                'memory_usage': gc_system.runtime.get_memory_usage(),
                'performance_stats': self.monitor.get_statistics()
            }
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        
        print(f"ダッシュボードをエクスポート: {filepath}")


def demo_visualization():
    """可視化機能のデモ"""
    from system import GenerativeComputingSystem
    import time
    
    print("\n" + "="*70)
    print("可視化とモニタリングのデモ")
    print("="*70)
    
    # システムを初期化
    gc = GenerativeComputingSystem()
    
    # ダッシュボードとモニターを初期化
    dashboard = DashboardGenerator()
    dashboard.monitor.start_monitoring()
    
    # いくつかの操作を実行
    print("\n操作を実行中...")
    
    start_time = time.time()
    
    # 操作1: データ処理
    result1 = gc.execute_natural_language(
        "データを抽出して分析する",
        context={"data": "サンプルデータ"}
    )
    
    exec_time1 = time.time() - start_time
    dashboard.monitor.record_execution(
        exec_time1,
        gc.runtime.get_memory_usage()['total_slots'],
        2
    )
    
    # 操作2: CoT実行
    start_time = time.time()
    result2 = gc.execute_with_cot("複雑な問題を解決する")
    exec_time2 = time.time() - start_time
    dashboard.monitor.record_execution(
        exec_time2,
        gc.runtime.get_memory_usage()['total_slots'],
        3
    )
    
    # ダッシュボードを表示
    print("\n" + "="*70)
    print(dashboard.generate_dashboard(gc))
    
    # ダッシュボードをエクスポート
    dashboard.export_dashboard(
        gc,
        '/tmp/gc_dashboard.txt',
        format='txt'
    )
    dashboard.export_dashboard(
        gc,
        '/tmp/gc_dashboard.json',
        format='json'
    )
    
    print("\n✓ ダッシュボードをエクスポートしました")
    print("  - /tmp/gc_dashboard.txt")
    print("  - /tmp/gc_dashboard.json")


if __name__ == "__main__":
    demo_visualization()
