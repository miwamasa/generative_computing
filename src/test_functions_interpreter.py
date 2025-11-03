"""
生成コンピューティング - 組み込み関数とインタプリタのテストケース

LLM組み込み関数とインタプリタの機能を検証
"""

import unittest
import sys
sys.path.append('/home/claude/generative_computing')

from builtin_functions import (
    ChainOfThought, CitationExtractor, DataTransformPipeline,
    ContextSummarizer, FunctionLibrary
)
from interpreter import (
    NaturalLanguageInterpreter, TaskExecutor, Task, TaskType
)
from runtime import GenerativeRuntime


class TestChainOfThought(unittest.TestCase):
    """ChainOfThoughtクラスのテスト"""
    
    def setUp(self):
        self.cot = ChainOfThought()
    
    def test_add_step(self):
        """思考ステップの追加テスト"""
        step = self.cot.add_step(
            description="分析開始",
            reasoning="データを分析する",
            confidence=0.9
        )
        
        self.assertEqual(len(self.cot.thought_chain), 1)
        self.assertEqual(step.description, "分析開始")
        self.assertEqual(step.confidence, 0.9)
    
    def test_multiple_steps(self):
        """複数ステップの追加テスト"""
        self.cot.add_step("Step 1", "Reasoning 1", 0.9)
        self.cot.add_step("Step 2", "Reasoning 2", 0.8)
        self.cot.add_step("Step 3", "Reasoning 3", 0.95)
        
        self.assertEqual(len(self.cot.thought_chain), 3)
        self.assertEqual(self.cot.current_step, 2)
    
    def test_backtrack_to_step(self):
        """ステップへのバックトラックテスト"""
        self.cot.add_step("Step 1", "R1", 0.9)
        self.cot.add_step("Step 2", "R2", 0.8)
        self.cot.add_step("Step 3", "R3", 0.7)
        
        removed = self.cot.backtrack_to_step(1)
        
        self.assertEqual(len(self.cot.thought_chain), 2)
        self.assertEqual(len(removed), 1)
        self.assertEqual(self.cot.current_step, 1)
    
    def test_backtrack_invalid_step(self):
        """無効なステップへのバックトラックでエラー"""
        self.cot.add_step("Step 1", "R1", 0.9)
        
        with self.assertRaises(ValueError):
            self.cot.backtrack_to_step(10)
    
    def test_get_low_confidence_steps(self):
        """低信頼度ステップの検出テスト"""
        self.cot.add_step("High", "R1", 0.9)
        self.cot.add_step("Low", "R2", 0.6)
        self.cot.add_step("Medium", "R3", 0.75)
        self.cot.add_step("Very Low", "R4", 0.5)
        
        low_conf = self.cot.get_low_confidence_steps(threshold=0.7)
        
        self.assertEqual(len(low_conf), 2)
        self.assertTrue(all(s.confidence < 0.7 for s in low_conf))
    
    def test_visualize(self):
        """可視化のテスト"""
        self.cot.add_step("Test step", "Test reasoning", 0.85)
        
        visualization = self.cot.visualize()
        
        self.assertIn("Chain of Thought", visualization)
        self.assertIn("Test step", visualization)
        self.assertIn("0.85", visualization)


class TestCitationExtractor(unittest.TestCase):
    """CitationExtractorクラスのテスト"""
    
    def setUp(self):
        self.extractor = CitationExtractor()
    
    def test_extract_academic_citation(self):
        """学術引用の抽出テスト"""
        text = "研究[Smith, 2023]によると、効果的である。"
        
        result = self.extractor.execute(text, verify=False)
        citations = result["citations"]
        
        self.assertEqual(len(citations), 1)
        self.assertEqual(citations[0]["type"], "academic")
        self.assertEqual(citations[0]["author"], "Smith")
        self.assertEqual(citations[0]["year"], "2023")
    
    def test_extract_url(self):
        """URL引用の抽出テスト"""
        text = "詳細はhttps://example.com/articleを参照。"
        
        result = self.extractor.execute(text, verify=False)
        citations = result["citations"]
        
        self.assertEqual(len(citations), 1)
        self.assertEqual(citations[0]["type"], "url")
        self.assertIn("example.com", citations[0]["url"])
    
    def test_extract_quote(self):
        """引用文の抽出テスト"""
        text = 'と述べた。"これは重要な発見である"と強調した。'
        
        result = self.extractor.execute(text, verify=False)
        citations = result["citations"]
        
        self.assertEqual(len(citations), 1)
        self.assertEqual(citations[0]["type"], "quote")
    
    def test_extract_multiple_types(self):
        """複数タイプの引用抽出テスト"""
        text = '''
        研究[Jones, 2024]によると、"画期的な成果"である。
        詳細はhttps://research.org/paperを参照。
        '''
        
        result = self.extractor.execute(text, verify=False)
        
        self.assertEqual(result["total"], 3)
        types = [c["type"] for c in result["citations"]]
        self.assertIn("academic", types)
        self.assertIn("url", types)
        self.assertIn("quote", types)
    
    def test_verify_citation(self):
        """引用の検証テスト"""
        citation = {
            "type": "academic",
            "author": "Smith",
            "year": "2023"
        }
        
        verification = self.extractor.verify_citation(citation)
        
        self.assertTrue(verification["is_valid"])
        self.assertEqual(len(verification["warnings"]), 0)
    
    def test_verify_invalid_year(self):
        """無効な年の検証テスト"""
        citation = {
            "type": "academic",
            "author": "Smith",
            "year": "3000"
        }
        
        verification = self.extractor.verify_citation(citation)
        
        self.assertFalse(verification["is_valid"])
        self.assertGreater(len(verification["warnings"]), 0)


class TestDataTransformPipeline(unittest.TestCase):
    """DataTransformPipelineクラスのテスト"""
    
    def setUp(self):
        self.pipeline = DataTransformPipeline()
    
    def test_uppercase_transform(self):
        """大文字変換のテスト"""
        result = self.pipeline.execute("hello", ["uppercase"])
        self.assertEqual(result, "HELLO")
    
    def test_lowercase_transform(self):
        """小文字変換のテスト"""
        result = self.pipeline.execute("HELLO", ["lowercase"])
        self.assertEqual(result, "hello")
    
    def test_strip_transform(self):
        """空白除去のテスト"""
        result = self.pipeline.execute("  hello  ", ["strip"])
        self.assertEqual(result, "hello")
    
    def test_normalize_spaces(self):
        """空白正規化のテスト"""
        result = self.pipeline.execute("hello    world", ["normalize_spaces"])
        self.assertEqual(result, "hello world")
    
    def test_extract_numbers(self):
        """数値抽出のテスト"""
        result = self.pipeline.execute("abc 123 def 456", ["extract_numbers"])
        self.assertEqual(result, [123, 456])
    
    def test_multiple_transforms(self):
        """複数変換のパイプラインテスト"""
        result = self.pipeline.execute(
            "  HELLO   WORLD  ",
            ["strip", "lowercase", "normalize_spaces"]
        )
        self.assertEqual(result, "hello world")
    
    def test_register_custom_transformer(self):
        """カスタム変換器の登録テスト"""
        self.pipeline.register_transformer(
            "reverse",
            lambda x: x[::-1] if isinstance(x, str) else x
        )
        
        result = self.pipeline.execute("hello", ["reverse"])
        self.assertEqual(result, "olleh")
    
    def test_unknown_transformer(self):
        """未知の変換器でエラー"""
        with self.assertRaises(ValueError):
            self.pipeline.execute("test", ["unknown_transform"])


class TestContextSummarizer(unittest.TestCase):
    """ContextSummarizerクラスのテスト"""
    
    def setUp(self):
        self.summarizer = ContextSummarizer()
    
    def test_short_text_no_summarization(self):
        """短いテキストは要約されない"""
        text = "短いテキスト"
        result = self.summarizer.execute(text, max_length=100)
        self.assertEqual(result, text)
    
    def test_truncate_strategy(self):
        """切り詰め戦略のテスト"""
        text = "a" * 1000
        result = self.summarizer.execute(text, max_length=100, strategy="truncate")
        
        self.assertEqual(len(result), 103)  # 100 + "..."
        self.assertTrue(result.endswith("..."))
    
    def test_sentence_boundary_strategy(self):
        """文境界戦略のテスト"""
        text = "一つ目の文。二つ目の文。三つ目の文。四つ目の文。"
        result = self.summarizer.execute(
            text, 
            max_length=20, 
            strategy="sentence_boundary"
        )
        
        self.assertTrue(result.endswith("。..."))


class TestFunctionLibrary(unittest.TestCase):
    """FunctionLibraryクラスのテスト"""
    
    def setUp(self):
        self.library = FunctionLibrary()
    
    def test_default_functions(self):
        """デフォルト関数の登録テスト"""
        self.assertIn("cot", self.library.functions)
        self.assertIn("citation", self.library.functions)
        self.assertIn("transform", self.library.functions)
        self.assertIn("summarize", self.library.functions)
    
    def test_get_function(self):
        """関数の取得テスト"""
        cot = self.library.get("cot")
        self.assertIsNotNone(cot)
        self.assertIsInstance(cot, ChainOfThought)
    
    def test_list_functions(self):
        """関数リストの取得テスト"""
        functions = self.library.list_functions()
        self.assertGreater(len(functions), 0)
        self.assertTrue(all("name" in f for f in functions))


class TestNaturalLanguageInterpreter(unittest.TestCase):
    """NaturalLanguageInterpreterクラスのテスト"""
    
    def setUp(self):
        self.interpreter = NaturalLanguageInterpreter()
    
    def test_parse_extract_instruction(self):
        """抽出指示の解析テスト"""
        tasks = self.interpreter.parse_instruction("テキストから引用を抽出")
        
        self.assertEqual(len(tasks), 1)
        self.assertEqual(tasks[0].task_type, TaskType.EXTRACT)
    
    def test_parse_transform_instruction(self):
        """変換指示の解析テスト"""
        tasks = self.interpreter.parse_instruction("データを JSON に変換")
        
        self.assertEqual(len(tasks), 1)
        self.assertEqual(tasks[0].task_type, TaskType.TRANSFORM)
    
    def test_parse_compound_instruction(self):
        """複合指示の解析テスト"""
        instruction = "データを抽出して分析し、結果を生成する"
        tasks = self.interpreter.parse_instruction(instruction)
        
        self.assertGreater(len(tasks), 1)
    
    def test_create_execution_plan(self):
        """実行計画の作成テスト"""
        tasks = [
            Task("t1", TaskType.EXTRACT, "Extract", [], ["t1_out"], {}),
            Task("t2", TaskType.ANALYZE, "Analyze", ["t1_out"], ["t2_out"], {}, ["t1"]),
        ]
        
        plan = self.interpreter.create_execution_plan(tasks)
        
        self.assertEqual(len(plan.execution_order), 2)
        self.assertEqual(plan.execution_order[0], "t1")
        self.assertEqual(plan.execution_order[1], "t2")
    
    def test_visualize_plan(self):
        """実行計画の可視化テスト"""
        tasks = [
            Task("t1", TaskType.EXTRACT, "Extract data", [], ["out1"], {})
        ]
        plan = self.interpreter.create_execution_plan(tasks)
        
        visualization = self.interpreter.visualize_plan(plan)
        
        self.assertIn("Execution Plan", visualization)
        self.assertIn("Extract data", visualization)


class TestTaskExecutor(unittest.TestCase):
    """TaskExecutorクラスのテスト"""
    
    def setUp(self):
        self.runtime = GenerativeRuntime()
        self.library = FunctionLibrary()
        self.executor = TaskExecutor(self.runtime, self.library)
    
    def test_execute_simple_plan(self):
        """シンプルな実行計画のテスト"""
        from interpreter import ExecutionPlan
        
        tasks = [
            Task("t1", TaskType.EXTRACT, "Extract", [], ["out1"], {})
        ]
        plan = ExecutionPlan("plan_1", tasks, ["t1"])
        
        result = self.executor.execute_plan(plan)
        
        self.assertEqual(result["completed_tasks"], 1)
        self.assertIn("t1", result["results"])


if __name__ == '__main__':
    unittest.main(verbosity=2)
