"""
生成コンピューティング - LLM統合

実際のLLM（Claude API）との統合実装
"""

from typing import Any, Dict, List, Optional
import json
from abc import ABC, abstractmethod


class LLMProvider(ABC):
    """LLMプロバイダーの抽象基底クラス"""
    
    @abstractmethod
    def complete(self, prompt: str, **kwargs) -> str:
        """テキスト補完を実行"""
        pass
    
    @abstractmethod
    def complete_structured(self, prompt: str, schema: Dict) -> Dict:
        """構造化された出力を生成"""
        pass


class MockLLMProvider(LLMProvider):
    """
    モックLLMプロバイダー
    
    実際のAPI呼び出しなしでテスト可能
    """
    
    def __init__(self):
        self.call_count = 0
        self.call_history: List[Dict] = []
    
    def complete(self, prompt: str, **kwargs) -> str:
        """モックの補完"""
        self.call_count += 1
        self.call_history.append({
            "prompt": prompt,
            "kwargs": kwargs,
            "type": "complete"
        })
        
        # シンプルなルールベースの応答
        if "抽出" in prompt or "extract" in prompt.lower():
            return "抽出結果: 重要な情報1, 重要な情報2, 重要な情報3"
        elif "分析" in prompt or "analyze" in prompt.lower():
            return "分析結果: データには明確なトレンドが見られます。主要な発見は以下の通りです..."
        elif "要約" in prompt or "summarize" in prompt.lower():
            return "要約: 入力テキストの主要なポイントをまとめました。"
        elif "生成" in prompt or "generate" in prompt.lower():
            return "生成結果: 要求された内容に基づいて新しいコンテンツを作成しました。"
        else:
            return "処理完了: タスクを実行しました。"
    
    def complete_structured(self, prompt: str, schema: Dict) -> Dict:
        """構造化された出力のモック"""
        self.call_count += 1
        self.call_history.append({
            "prompt": prompt,
            "schema": schema,
            "type": "complete_structured"
        })
        
        # スキーマに基づいたモックデータ生成
        result = {}
        for key, value_type in schema.items():
            if value_type == "string":
                result[key] = f"Sample {key}"
            elif value_type == "number":
                result[key] = 42
            elif value_type == "list":
                result[key] = ["item1", "item2", "item3"]
            elif value_type == "dict":
                result[key] = {"nested_key": "nested_value"}
        
        return result


class ClaudeAPIProvider(LLMProvider):
    """
    Claude API プロバイダー
    
    実際のAnthropic APIと連携（要API KEY）
    """
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key
        self._client = None
        
        if api_key:
            try:
                import anthropic
                self._client = anthropic.Anthropic(api_key=api_key)
            except ImportError:
                raise ImportError(
                    "anthropic パッケージが必要です: pip install anthropic"
                )
    
    def complete(self, prompt: str, **kwargs) -> str:
        """Claude APIで補完を実行"""
        if not self._client:
            raise ValueError("API キーが設定されていません")
        
        # デフォルトパラメータ
        params = {
            "model": "claude-sonnet-4-20250514",
            "max_tokens": 1024,
            "temperature": 0.7,
        }
        params.update(kwargs)
        
        message = self._client.messages.create(
            **params,
            messages=[{
                "role": "user",
                "content": prompt
            }]
        )
        
        return message.content[0].text
    
    def complete_structured(self, prompt: str, schema: Dict) -> Dict:
        """構造化された出力を生成"""
        # スキーマをプロンプトに組み込む
        structured_prompt = f"""
{prompt}

以下のJSON形式で応答してください:
{json.dumps(schema, indent=2, ensure_ascii=False)}

IMPORTANT: 応答は有効なJSONのみを含めてください。説明文は含めないでください。
"""
        
        response = self.complete(structured_prompt, temperature=0.3)
        
        # JSONを抽出
        try:
            # マークダウンのコードブロックを除去
            clean_response = response.strip()
            if clean_response.startswith("```"):
                clean_response = clean_response.split("```")[1]
                if clean_response.startswith("json"):
                    clean_response = clean_response[4:]
            
            return json.loads(clean_response.strip())
        except json.JSONDecodeError as e:
            raise ValueError(f"LLMの応答を解析できませんでした: {e}\n応答: {response}")


class LLMEnhancedFunction:
    """
    LLMを活用した拡張関数
    
    組み込み関数にLLMの能力を追加
    """
    
    def __init__(self, llm_provider: LLMProvider):
        self.llm = llm_provider
    
    def extract_information(self, text: str, target: str) -> List[str]:
        """LLMを使用して情報を抽出"""
        prompt = f"""
以下のテキストから、{target}を抽出してください。

テキスト:
{text}

抽出した{target}をリスト形式で返してください。
"""
        
        response = self.llm.complete(prompt)
        
        # 簡易的なリスト抽出
        items = []
        for line in response.split('\n'):
            line = line.strip()
            if line.startswith('-') or line.startswith('•'):
                items.append(line[1:].strip())
            elif line and len(line) > 3:
                items.append(line)
        
        return items[:10]  # 最大10項目
    
    def analyze_sentiment(self, text: str) -> Dict[str, Any]:
        """LLMを使用して感情分析"""
        schema = {
            "sentiment": "string (positive/negative/neutral)",
            "confidence": "number (0-1)",
            "key_points": "list of strings",
            "summary": "string"
        }
        
        prompt = f"""
以下のテキストの感情を分析してください:

{text}

分析結果を提供してください。
"""
        
        try:
            return self.llm.complete_structured(prompt, schema)
        except Exception:
            # フォールバック: シンプルな分析
            response = self.llm.complete(prompt)
            return {
                "sentiment": "neutral",
                "confidence": 0.5,
                "key_points": [response[:100]],
                "summary": response[:200]
            }
    
    def generate_summary(self, text: str, max_length: int = 200) -> str:
        """LLMを使用して要約を生成"""
        prompt = f"""
以下のテキストを{max_length}文字程度で要約してください:

{text}

要約:
"""
        
        summary = self.llm.complete(prompt, max_tokens=max_length * 2)
        return summary.strip()
    
    def transform_data(self, data: Any, transformation: str) -> Any:
        """LLMを使用してデータ変換"""
        prompt = f"""
以下のデータに対して、次の変換を行ってください: {transformation}

データ:
{json.dumps(data, ensure_ascii=False, indent=2)}

変換後のデータを同じ形式で返してください。
"""
        
        response = self.llm.complete(prompt)
        
        try:
            return json.loads(response)
        except json.JSONDecodeError:
            return {"transformed": response}
    
    def validate_content(self, content: str, criteria: List[str]) -> Dict[str, Any]:
        """LLMを使用してコンテンツを検証"""
        criteria_text = "\n".join(f"- {c}" for c in criteria)
        
        prompt = f"""
以下のコンテンツを、次の基準に基づいて検証してください:

基準:
{criteria_text}

コンテンツ:
{content}

各基準について、合格/不合格と理由を提供してください。
"""
        
        response = self.llm.complete(prompt)
        
        return {
            "is_valid": "合格" in response or "valid" in response.lower(),
            "validation_details": response,
            "criteria_checked": len(criteria)
        }


class LLMIntegratedSystem:
    """
    LLM統合システム
    
    生成コンピューティングシステムにLLM機能を追加
    """
    
    def __init__(self, llm_provider: LLMProvider):
        self.llm = llm_provider
        self.enhanced_functions = LLMEnhancedFunction(llm_provider)
    
    def execute_with_llm(
        self,
        instruction: str,
        context: Optional[Dict[str, Any]] = None,
        use_cot: bool = True
    ) -> Dict[str, Any]:
        """
        LLMを活用した実行
        
        Args:
            instruction: 実行する指示
            context: コンテキストデータ
            use_cot: CoT（連鎖思考）を使用するか
            
        Returns:
            実行結果
        """
        from system import GenerativeComputingSystem
        
        # 基本システムを初期化
        gc = GenerativeComputingSystem()
        
        # LLMを使用してタスクを分解
        task_decomposition = self._decompose_tasks_with_llm(instruction)
        
        # 各タスクをLLMで実行
        results = {}
        for task_id, task_desc in task_decomposition.items():
            if "抽出" in task_desc or "extract" in task_desc.lower():
                results[task_id] = self.enhanced_functions.extract_information(
                    str(context),
                    "重要な情報"
                )
            elif "分析" in task_desc or "analyze" in task_desc.lower():
                results[task_id] = self.enhanced_functions.analyze_sentiment(
                    str(context)
                )
            elif "要約" in task_desc or "summarize" in task_desc.lower():
                results[task_id] = self.enhanced_functions.generate_summary(
                    str(context)
                )
            else:
                # 汎用的な処理
                results[task_id] = self.llm.complete(
                    f"{task_desc}\n\nコンテキスト: {context}"
                )
        
        return {
            "instruction": instruction,
            "task_decomposition": task_decomposition,
            "results": results,
            "llm_calls": getattr(self.llm, 'call_count', 0)
        }
    
    def _decompose_tasks_with_llm(self, instruction: str) -> Dict[str, str]:
        """LLMを使用してタスクを分解"""
        prompt = f"""
以下の指示を、実行可能な個別のタスクに分解してください:

指示: {instruction}

各タスクに番号を付けて、明確に説明してください。
"""
        
        response = self.llm.complete(prompt, max_tokens=500)
        
        # タスクを抽出（簡易パーサー）
        tasks = {}
        task_counter = 0
        
        for line in response.split('\n'):
            line = line.strip()
            if line and (line[0].isdigit() or line.startswith('-')):
                task_counter += 1
                # 番号や記号を除去
                task_text = line.lstrip('0123456789.-) ').strip()
                if task_text:
                    tasks[f"task_{task_counter}"] = task_text
        
        # 最低1つのタスクは必要
        if not tasks:
            tasks["task_1"] = instruction
        
        return tasks
    
    def interactive_refinement(
        self,
        initial_result: Any,
        refinement_instruction: str
    ) -> Any:
        """
        対話的な改善
        
        結果を見て、LLMに改善を依頼
        """
        prompt = f"""
以下の結果を、次の指示に従って改善してください:

改善指示: {refinement_instruction}

現在の結果:
{json.dumps(initial_result, ensure_ascii=False, indent=2)}

改善された結果を同じ形式で返してください。
"""
        
        response = self.llm.complete(prompt)
        
        try:
            return json.loads(response)
        except json.JSONDecodeError:
            return {"refined_result": response}


# 使用例を含むデモ関数
def demo_llm_integration():
    """LLM統合のデモ"""
    print("=" * 60)
    print("LLM統合デモ")
    print("=" * 60)
    
    # モックプロバイダーを使用（実際のAPI不要）
    llm_provider = MockLLMProvider()
    
    # 統合システムを初期化
    system = LLMIntegratedSystem(llm_provider)
    
    # サンプルテキスト
    sample_text = """
    人工知能技術は急速に発展しています。特に大規模言語モデルは、
    自然言語処理において革命的な進歩をもたらしました。
    これらの技術は、様々な産業で活用されています。
    """
    
    print("\n1. 情報抽出")
    extracted = system.enhanced_functions.extract_information(
        sample_text,
        "キーワード"
    )
    print(f"抽出結果: {extracted}")
    
    print("\n2. 感情分析")
    sentiment = system.enhanced_functions.analyze_sentiment(sample_text)
    print(f"感情分析: {sentiment}")
    
    print("\n3. 要約生成")
    summary = system.enhanced_functions.generate_summary(sample_text, max_length=50)
    print(f"要約: {summary}")
    
    print("\n4. LLM統合実行")
    result = system.execute_with_llm(
        "テキストを分析して要約する",
        context={"text": sample_text}
    )
    print(f"タスク分解: {result['task_decomposition']}")
    print(f"LLM呼び出し回数: {result['llm_calls']}")
    
    print("\n" + "=" * 60)
    print(f"総LLM呼び出し: {llm_provider.call_count}")
    print("=" * 60)


if __name__ == "__main__":
    demo_llm_integration()
