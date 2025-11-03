"""
生成コンピューティング - ランタイムのテストケース

ランタイムコンポーネントの機能を検証するユニットテスト
"""

import unittest
import sys
sys.path.append('/home/claude/generative_computing')

from runtime import GenerativeRuntime, MemorySlot, SlotType, Checkpoint


class TestMemorySlot(unittest.TestCase):
    """MemorySlotクラスのテスト"""
    
    def test_slot_creation(self):
        """スロットが正しく作成されるか"""
        slot = MemorySlot(
            slot_id="test_slot",
            slot_type=SlotType.CONTEXT,
            content="test content"
        )
        
        self.assertEqual(slot.slot_id, "test_slot")
        self.assertEqual(slot.slot_type, SlotType.CONTEXT)
        self.assertEqual(slot.content, "test content")
        self.assertIsInstance(slot.metadata, dict)
    
    def test_slot_to_dict(self):
        """スロットが辞書に変換できるか"""
        slot = MemorySlot(
            slot_id="test",
            slot_type=SlotType.OUTPUT,
            content={"data": 123},
            metadata={"source": "test"}
        )
        
        slot_dict = slot.to_dict()
        self.assertIn("slot_id", slot_dict)
        self.assertIn("slot_type", slot_dict)
        self.assertIn("content", slot_dict)
        self.assertEqual(slot_dict["slot_type"], "output")


class TestGenerativeRuntime(unittest.TestCase):
    """GenerativeRuntimeクラスのテスト"""
    
    def setUp(self):
        """各テストの前に実行"""
        self.runtime = GenerativeRuntime()
    
    def test_allocate_slot(self):
        """スロットの割り当てテスト"""
        slot = self.runtime.allocate_slot(
            slot_id="test_1",
            slot_type=SlotType.CONTEXT,
            content="data"
        )
        
        self.assertIsInstance(slot, MemorySlot)
        self.assertEqual(slot.slot_id, "test_1")
        self.assertIn("test_1", self.runtime.memory_slots)
    
    def test_update_slot(self):
        """スロットの更新テスト"""
        self.runtime.allocate_slot("slot_1", SlotType.INTERMEDIATE, "initial")
        self.runtime.update_slot("slot_1", "updated")
        
        slot = self.runtime.get_slot("slot_1")
        self.assertEqual(slot.content, "updated")
    
    def test_update_nonexistent_slot(self):
        """存在しないスロットの更新でエラーが発生するか"""
        with self.assertRaises(KeyError):
            self.runtime.update_slot("nonexistent", "data")
    
    def test_merge_update(self):
        """マージ更新のテスト"""
        self.runtime.allocate_slot(
            "slot_1", 
            SlotType.INTERMEDIATE, 
            {"a": 1, "b": 2}
        )
        self.runtime.update_slot("slot_1", {"c": 3}, merge=True)
        
        slot = self.runtime.get_slot("slot_1")
        self.assertEqual(slot.content, {"a": 1, "b": 2, "c": 3})
    
    def test_delete_slot(self):
        """スロットの削除テスト"""
        self.runtime.allocate_slot("temp", SlotType.INTERMEDIATE, "data")
        self.assertEqual(len(self.runtime.memory_slots), 1)
        
        self.runtime.delete_slot("temp")
        self.assertEqual(len(self.runtime.memory_slots), 0)
    
    def test_get_slot(self):
        """スロットの取得テスト"""
        self.runtime.allocate_slot("slot_1", SlotType.CONTEXT, "test")
        
        slot = self.runtime.get_slot("slot_1")
        self.assertIsNotNone(slot)
        self.assertEqual(slot.content, "test")
        
        # 存在しないスロット
        slot = self.runtime.get_slot("nonexistent")
        self.assertIsNone(slot)
    
    def test_transform_slot(self):
        """スロットの変換テスト"""
        self.runtime.allocate_slot("num_slot", SlotType.INTERMEDIATE, 10)
        self.runtime.transform_slot("num_slot", lambda x: x * 2)
        
        slot = self.runtime.get_slot("num_slot")
        self.assertEqual(slot.content, 20)
    
    def test_transform_nonexistent_slot(self):
        """存在しないスロットの変換でエラーが発生するか"""
        with self.assertRaises(KeyError):
            self.runtime.transform_slot("nonexistent", lambda x: x)
    
    def test_list_slots_by_type(self):
        """タイプ別スロット取得のテスト"""
        self.runtime.allocate_slot("ctx_1", SlotType.CONTEXT, "data1")
        self.runtime.allocate_slot("ctx_2", SlotType.CONTEXT, "data2")
        self.runtime.allocate_slot("out_1", SlotType.OUTPUT, "result")
        
        context_slots = self.runtime.list_slots_by_type(SlotType.CONTEXT)
        self.assertEqual(len(context_slots), 2)
        
        output_slots = self.runtime.list_slots_by_type(SlotType.OUTPUT)
        self.assertEqual(len(output_slots), 1)
    
    def test_create_checkpoint(self):
        """チェックポイント作成のテスト"""
        self.runtime.allocate_slot("slot_1", SlotType.CONTEXT, "data")
        
        checkpoint = self.runtime.create_checkpoint(
            "cp_1", 
            "Test checkpoint"
        )
        
        self.assertIsInstance(checkpoint, Checkpoint)
        self.assertEqual(checkpoint.checkpoint_id, "cp_1")
        self.assertIn("cp_1", self.runtime.checkpoints)
    
    def test_restore_checkpoint(self):
        """チェックポイント復元のテスト"""
        # 初期状態
        self.runtime.allocate_slot("slot_1", SlotType.CONTEXT, "original")
        checkpoint = self.runtime.create_checkpoint("cp_1", "Before change")
        
        # 状態を変更
        self.runtime.update_slot("slot_1", "modified")
        self.runtime.allocate_slot("slot_2", SlotType.INTERMEDIATE, "new")
        
        # 復元
        self.runtime.restore_checkpoint("cp_1")
        
        slot = self.runtime.get_slot("slot_1")
        self.assertEqual(slot.content, "original")
        self.assertIsNone(self.runtime.get_slot("slot_2"))
    
    def test_restore_nonexistent_checkpoint(self):
        """存在しないチェックポイントの復元でエラーが発生するか"""
        with self.assertRaises(KeyError):
            self.runtime.restore_checkpoint("nonexistent")
    
    def test_get_memory_usage(self):
        """メモリ使用状況取得のテスト"""
        self.runtime.allocate_slot("ctx_1", SlotType.CONTEXT, "data")
        self.runtime.allocate_slot("out_1", SlotType.OUTPUT, "result")
        
        usage = self.runtime.get_memory_usage()
        
        self.assertEqual(usage["total_slots"], 2)
        self.assertIn("by_type", usage)
        self.assertEqual(usage["by_type"]["context"], 1)
        self.assertEqual(usage["by_type"]["output"], 1)
    
    def test_execution_history(self):
        """実行履歴の記録テスト"""
        self.runtime.allocate_slot("slot_1", SlotType.CONTEXT, "data")
        self.runtime.update_slot("slot_1", "updated")
        self.runtime.delete_slot("slot_1")
        
        self.assertEqual(len(self.runtime.execution_history), 3)
        self.assertEqual(self.runtime.execution_history[0]["action"], "allocate_slot")
        self.assertEqual(self.runtime.execution_history[1]["action"], "update_slot")
        self.assertEqual(self.runtime.execution_history[2]["action"], "delete_slot")
    
    def test_export_state(self):
        """状態のエクスポートテスト"""
        self.runtime.allocate_slot("slot_1", SlotType.CONTEXT, "data")
        self.runtime.create_checkpoint("cp_1", "Test")
        
        state = self.runtime.export_state()
        
        self.assertIn("memory_slots", state)
        self.assertIn("checkpoints", state)
        self.assertIn("execution_history", state)
        self.assertIn("memory_usage", state)


class TestRuntimeIntegration(unittest.TestCase):
    """ランタイムの統合テスト"""
    
    def test_complex_workflow(self):
        """複雑なワークフローのテスト"""
        runtime = GenerativeRuntime()
        
        # ステップ1: コンテキストを設定
        runtime.allocate_slot("input", SlotType.CONTEXT, "raw data")
        
        # ステップ2: チェックポイントを作成
        cp1 = runtime.create_checkpoint("before_processing", "Initial state")
        
        # ステップ3: 中間処理
        runtime.allocate_slot("temp", SlotType.INTERMEDIATE, None)
        runtime.transform_slot("input", lambda x: x.upper())
        
        # ステップ4: 結果を生成
        runtime.allocate_slot("output", SlotType.OUTPUT, None)
        input_data = runtime.get_slot("input").content
        runtime.update_slot("output", f"Processed: {input_data}")
        
        # 検証
        output = runtime.get_slot("output")
        self.assertEqual(output.content, "Processed: RAW DATA")
        
        # ステップ5: バックトラック
        runtime.restore_checkpoint("before_processing")
        
        # 復元後の検証
        self.assertIsNone(runtime.get_slot("output"))
        input_slot = runtime.get_slot("input")
        self.assertEqual(input_slot.content, "raw data")


if __name__ == '__main__':
    # テストスイートを実行
    unittest.main(verbosity=2)
