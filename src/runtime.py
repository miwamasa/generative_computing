"""
生成コンピューティング - ランタイムコア

LLMベースの構造化実行環境を提供します。
- スロットベースのメモリ管理
- ワークフローオーケストレーション
- チェックポイント/バックトラック機能
"""

from typing import Any, Dict, List, Optional, Callable
from dataclasses import dataclass, field
from datetime import datetime
import json
from enum import Enum
import copy


class SlotType(Enum):
    """メモリスロットの種類"""
    CONTEXT = "context"
    INTERMEDIATE = "intermediate"
    OUTPUT = "output"
    CITATION = "citation"


@dataclass
class MemorySlot:
    """スロットベースのメモリ管理"""
    slot_id: str
    slot_type: SlotType
    content: Any
    metadata: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict:
        return {
            "slot_id": self.slot_id,
            "slot_type": self.slot_type.value,
            "content": self.content,
            "metadata": self.metadata,
            "timestamp": self.timestamp.isoformat()
        }


@dataclass
class Checkpoint:
    """思考チェーンのチェックポイント"""
    checkpoint_id: str
    state: Dict[str, Any]
    memory_snapshot: List[MemorySlot]
    timestamp: datetime = field(default_factory=datetime.now)
    description: str = ""


class GenerativeRuntime:
    """
    生成コンピューティングのランタイム
    
    高度なKVキャッシュ管理とワークフローオーケストレーションを提供
    """
    
    def __init__(self):
        self.memory_slots: Dict[str, MemorySlot] = {}
        self.checkpoints: Dict[str, Checkpoint] = {}
        self.execution_history: List[Dict] = []
        self.current_workflow: Optional[str] = None
        
    def allocate_slot(
        self, 
        slot_id: str, 
        slot_type: SlotType,
        content: Any = None,
        metadata: Optional[Dict] = None
    ) -> MemorySlot:
        """スロットを割り当て"""
        slot = MemorySlot(
            slot_id=slot_id,
            slot_type=slot_type,
            content=content,
            metadata=metadata or {}
        )
        self.memory_slots[slot_id] = slot
        self._log_action("allocate_slot", {"slot_id": slot_id, "type": slot_type.value})
        return slot
    
    def update_slot(self, slot_id: str, content: Any, merge: bool = False) -> None:
        """スロットの内容を更新"""
        if slot_id not in self.memory_slots:
            raise KeyError(f"Slot {slot_id} not found")
        
        if merge and isinstance(content, dict) and isinstance(self.memory_slots[slot_id].content, dict):
            self.memory_slots[slot_id].content.update(content)
        else:
            self.memory_slots[slot_id].content = content
        
        self.memory_slots[slot_id].timestamp = datetime.now()
        self._log_action("update_slot", {"slot_id": slot_id})
    
    def delete_slot(self, slot_id: str) -> None:
        """スロットを削除（KVキャッシュのクリーニング）"""
        if slot_id in self.memory_slots:
            del self.memory_slots[slot_id]
            self._log_action("delete_slot", {"slot_id": slot_id})
    
    def get_slot(self, slot_id: str) -> Optional[MemorySlot]:
        """スロットを取得"""
        return self.memory_slots.get(slot_id)
    
    def transform_slot(
        self, 
        slot_id: str, 
        transform_fn: Callable[[Any], Any]
    ) -> None:
        """スロット内容を変換"""
        if slot_id not in self.memory_slots:
            raise KeyError(f"Slot {slot_id} not found")
        
        old_content = self.memory_slots[slot_id].content
        new_content = transform_fn(old_content)
        self.update_slot(slot_id, new_content)
        self._log_action("transform_slot", {"slot_id": slot_id})
    
    def create_checkpoint(self, checkpoint_id: str, description: str = "") -> Checkpoint:
        """現在の状態のチェックポイントを作成"""
        checkpoint = Checkpoint(
            checkpoint_id=checkpoint_id,
            state=self._capture_state(),
            memory_snapshot=copy.deepcopy(list(self.memory_slots.values())),
            description=description
        )
        self.checkpoints[checkpoint_id] = checkpoint
        self._log_action("create_checkpoint", {"checkpoint_id": checkpoint_id})
        return checkpoint
    
    def restore_checkpoint(self, checkpoint_id: str) -> None:
        """チェックポイントから状態を復元（バックトラック）"""
        if checkpoint_id not in self.checkpoints:
            raise KeyError(f"Checkpoint {checkpoint_id} not found")
        
        checkpoint = self.checkpoints[checkpoint_id]
        self.memory_slots = {
            slot.slot_id: copy.deepcopy(slot) 
            for slot in checkpoint.memory_snapshot
        }
        self._log_action("restore_checkpoint", {"checkpoint_id": checkpoint_id})
    
    def list_slots_by_type(self, slot_type: SlotType) -> List[MemorySlot]:
        """タイプ別にスロットを取得"""
        return [slot for slot in self.memory_slots.values() if slot.slot_type == slot_type]
    
    def get_memory_usage(self) -> Dict[str, Any]:
        """メモリ使用状況を取得"""
        return {
            "total_slots": len(self.memory_slots),
            "by_type": {
                slot_type.value: len(self.list_slots_by_type(slot_type))
                for slot_type in SlotType
            },
            "checkpoints": len(self.checkpoints)
        }
    
    def _capture_state(self) -> Dict[str, Any]:
        """現在の状態をキャプチャ"""
        return {
            "workflow": self.current_workflow,
            "slot_count": len(self.memory_slots),
            "timestamp": datetime.now().isoformat()
        }
    
    def _log_action(self, action: str, details: Dict[str, Any]) -> None:
        """アクションをログに記録"""
        self.execution_history.append({
            "action": action,
            "details": details,
            "timestamp": datetime.now().isoformat()
        })
    
    def export_state(self) -> Dict[str, Any]:
        """ランタイムの状態をエクスポート"""
        return {
            "memory_slots": {
                slot_id: slot.to_dict() 
                for slot_id, slot in self.memory_slots.items()
            },
            "checkpoints": {
                cp_id: {
                    "checkpoint_id": cp.checkpoint_id,
                    "description": cp.description,
                    "timestamp": cp.timestamp.isoformat()
                }
                for cp_id, cp in self.checkpoints.items()
            },
            "execution_history": self.execution_history,
            "memory_usage": self.get_memory_usage()
        }
