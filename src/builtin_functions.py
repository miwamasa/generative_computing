"""
生成コンピューティング - LLM組み込み関数ライブラリ

CoT、引用抽出、データ変換などの特化型関数を提供
"""

from typing import Any, Dict, List, Optional, Tuple, Callable
from dataclasses import dataclass
import re
from abc import ABC, abstractmethod


@dataclass
class ThoughtStep:
    """思考ステップの表現"""
    step_id: int
    description: str
    reasoning: str
    confidence: float  # 0.0 - 1.0
    checkpoint_id: Optional[str] = None


class BuiltInFunction(ABC):
    """LLM組み込み関数の基底クラス"""
    
    @abstractmethod
    def execute(self, *args, **kwargs) -> Any:
        """関数を実行"""
        pass
    
    @abstractmethod
    def get_signature(self) -> Dict[str, Any]:
        """関数のシグネチャを返す"""
        pass


class ChainOfThought(BuiltInFunction):
    """
    CoT（連鎖思考）管理関数
    
    思考の連鎖を管理し、チェックポイントとバックトラックをサポート
    """
    
    def __init__(self):
        self.thought_chain: List[ThoughtStep] = []
        self.current_step = 0
        
    def add_step(
        self, 
        description: str, 
        reasoning: str, 
        confidence: float = 1.0,
        checkpoint_id: Optional[str] = None
    ) -> ThoughtStep:
        """思考ステップを追加"""
        step = ThoughtStep(
            step_id=len(self.thought_chain),
            description=description,
            reasoning=reasoning,
            confidence=confidence,
            checkpoint_id=checkpoint_id
        )
        self.thought_chain.append(step)
        self.current_step = len(self.thought_chain) - 1
        return step
    
    def backtrack_to_step(self, step_id: int) -> List[ThoughtStep]:
        """指定されたステップまで巻き戻し"""
        if 0 <= step_id < len(self.thought_chain):
            removed_steps = self.thought_chain[step_id + 1:]
            self.thought_chain = self.thought_chain[:step_id + 1]
            self.current_step = step_id
            return removed_steps
        raise ValueError(f"Invalid step_id: {step_id}")
    
    def get_low_confidence_steps(self, threshold: float = 0.7) -> List[ThoughtStep]:
        """低信頼度のステップを取得（脱線検出）"""
        return [step for step in self.thought_chain if step.confidence < threshold]
    
    def execute(self, operation: str, *args, **kwargs) -> Any:
        """CoT操作を実行"""
        if operation == "add":
            return self.add_step(*args, **kwargs)
        elif operation == "backtrack":
            return self.backtrack_to_step(*args, **kwargs)
        elif operation == "check_confidence":
            return self.get_low_confidence_steps(*args, **kwargs)
        else:
            raise ValueError(f"Unknown operation: {operation}")
    
    def get_signature(self) -> Dict[str, Any]:
        return {
            "name": "chain_of_thought",
            "operations": ["add", "backtrack", "check_confidence"],
            "description": "連鎖思考の管理とバックトラック機能"
        }
    
    def visualize(self) -> str:
        """思考チェーンを可視化"""
        lines = ["=== Chain of Thought ==="]
        for step in self.thought_chain:
            marker = "→" if step.step_id == self.current_step else " "
            lines.append(f"{marker} Step {step.step_id}: {step.description}")
            lines.append(f"  Reasoning: {step.reasoning}")
            lines.append(f"  Confidence: {step.confidence:.2f}")
            if step.checkpoint_id:
                lines.append(f"  Checkpoint: {step.checkpoint_id}")
        return "\n".join(lines)


class CitationExtractor(BuiltInFunction):
    """
    引用抽出関数
    
    テキストから引用を抽出し、検証する
    """
    
    def extract_citations(self, text: str) -> List[Dict[str, Any]]:
        """テキストから引用を抽出"""
        citations = []
        
        # [著者, 年] 形式
        pattern1 = r'\[([^\]]+),\s*(\d{4})\]'
        for match in re.finditer(pattern1, text):
            citations.append({
                "type": "academic",
                "author": match.group(1),
                "year": match.group(2),
                "position": match.start()
            })
        
        # URL形式
        pattern2 = r'https?://[^\s<>"{}|\\^`\[\]]+'
        for match in re.finditer(pattern2, text):
            citations.append({
                "type": "url",
                "url": match.group(0),
                "position": match.start()
            })
        
        # 引用符形式
        pattern3 = r'"([^"]{10,})"'
        for match in re.finditer(pattern3, text):
            citations.append({
                "type": "quote",
                "text": match.group(1),
                "position": match.start()
            })
        
        return citations
    
    def verify_citation(self, citation: Dict[str, Any]) -> Dict[str, Any]:
        """引用の検証（簡易版）"""
        verification = {
            "citation": citation,
            "is_valid": True,
            "warnings": []
        }
        
        if citation["type"] == "academic":
            year = int(citation["year"])
            if year > 2025 or year < 1900:
                verification["is_valid"] = False
                verification["warnings"].append("年が不自然です")
        
        elif citation["type"] == "quote":
            if len(citation["text"]) < 10:
                verification["warnings"].append("引用が短すぎます")
        
        return verification
    
    def execute(self, text: str, verify: bool = True) -> Dict[str, Any]:
        """引用を抽出し、オプションで検証"""
        citations = self.extract_citations(text)
        
        if verify:
            verifications = [self.verify_citation(c) for c in citations]
            return {
                "citations": citations,
                "verifications": verifications,
                "total": len(citations)
            }
        
        return {
            "citations": citations,
            "total": len(citations)
        }
    
    def get_signature(self) -> Dict[str, Any]:
        return {
            "name": "citation_extractor",
            "params": ["text", "verify"],
            "description": "引用の抽出と検証"
        }


class DataTransformPipeline(BuiltInFunction):
    """
    データ変換パイプライン
    
    複数の変換ステップを連鎖させる
    """
    
    def __init__(self):
        self.transformers: Dict[str, Callable] = {
            "uppercase": lambda x: x.upper() if isinstance(x, str) else x,
            "lowercase": lambda x: x.lower() if isinstance(x, str) else x,
            "strip": lambda x: x.strip() if isinstance(x, str) else x,
            "normalize_spaces": lambda x: " ".join(x.split()) if isinstance(x, str) else x,
            "extract_numbers": lambda x: [int(n) for n in re.findall(r'\d+', x)] if isinstance(x, str) else x,
        }
    
    def register_transformer(self, name: str, func: Callable) -> None:
        """新しい変換関数を登録"""
        self.transformers[name] = func
    
    def execute(self, data: Any, pipeline: List[str]) -> Any:
        """パイプラインを実行"""
        result = data
        for transform_name in pipeline:
            if transform_name not in self.transformers:
                raise ValueError(f"Unknown transformer: {transform_name}")
            result = self.transformers[transform_name](result)
        return result
    
    def get_signature(self) -> Dict[str, Any]:
        return {
            "name": "data_transform_pipeline",
            "params": ["data", "pipeline"],
            "available_transformers": list(self.transformers.keys()),
            "description": "データ変換パイプライン"
        }


class ContextSummarizer(BuiltInFunction):
    """
    コンテキスト要約関数
    
    長いコンテキストを圧縮して管理
    """
    
    def execute(self, text: str, max_length: int = 500, strategy: str = "truncate") -> str:
        """コンテキストを要約"""
        if len(text) <= max_length:
            return text
        
        if strategy == "truncate":
            return text[:max_length] + "..."
        
        elif strategy == "sentence_boundary":
            # 文境界で切る
            sentences = text.split('。')
            result = []
            current_length = 0
            
            for sentence in sentences:
                if current_length + len(sentence) <= max_length:
                    result.append(sentence)
                    current_length += len(sentence)
                else:
                    break
            
            return '。'.join(result) + '。...'
        
        elif strategy == "extract_key":
            # キーワード抽出的な要約（簡易版）
            lines = text.split('\n')
            important_lines = [line for line in lines if any(
                keyword in line for keyword in ['重要', '結論', '要約', 'まとめ']
            )]
            
            if important_lines:
                summary = '\n'.join(important_lines)
                if len(summary) <= max_length:
                    return summary
            
            return text[:max_length] + "..."
        
        return text[:max_length] + "..."
    
    def get_signature(self) -> Dict[str, Any]:
        return {
            "name": "context_summarizer",
            "params": ["text", "max_length", "strategy"],
            "strategies": ["truncate", "sentence_boundary", "extract_key"],
            "description": "コンテキストの圧縮と要約"
        }


class FunctionLibrary:
    """LLM組み込み関数のライブラリ管理"""
    
    def __init__(self):
        self.functions: Dict[str, BuiltInFunction] = {
            "cot": ChainOfThought(),
            "citation": CitationExtractor(),
            "transform": DataTransformPipeline(),
            "summarize": ContextSummarizer()
        }
    
    def register(self, name: str, function: BuiltInFunction) -> None:
        """新しい関数を登録"""
        self.functions[name] = function
    
    def get(self, name: str) -> Optional[BuiltInFunction]:
        """関数を取得"""
        return self.functions.get(name)
    
    def list_functions(self) -> List[Dict[str, Any]]:
        """利用可能な関数のリストを取得"""
        return [func.get_signature() for func in self.functions.values()]
    
    def execute(self, function_name: str, *args, **kwargs) -> Any:
        """関数を実行"""
        if function_name not in self.functions:
            raise ValueError(f"Function {function_name} not found")
        return self.functions[function_name].execute(*args, **kwargs)
