"""
生成コンピューティング - 実用的なユースケース

実際のビジネス・研究シナリオでの使用例
"""

import sys
sys.path.append('/mnt/user-data/outputs/generative_computing')

from system import GenerativeComputingSystem, SkillManager
from llm_integration import LLMIntegratedSystem, MockLLMProvider
from runtime import SlotType
from typing import Dict, List, Any
import json


class ResearchPaperAnalyzer:
    """
    研究論文分析システム
    
    複数の論文を分析し、比較レポートを生成
    """
    
    def __init__(self):
        self.gc = GenerativeComputingSystem()
        self.llm_system = LLMIntegratedSystem(MockLLMProvider())
    
    def analyze_papers(
        self,
        papers: List[Dict[str, str]],
        analysis_type: str = "comprehensive"
    ) -> Dict[str, Any]:
        """
        複数の論文を分析
        
        Args:
            papers: 論文のリスト [{"title": ..., "abstract": ...}, ...]
            analysis_type: 分析タイプ (comprehensive/summary/comparison)
            
        Returns:
            分析結果
        """
        print(f"\n{'='*60}")
        print(f"研究論文分析: {len(papers)}本の論文を分析")
        print(f"{'='*60}\n")
        
        # ステップ1: 各論文から重要情報を抽出
        print("ステップ1: 重要情報の抽出...")
        extracted_data = []
        for i, paper in enumerate(papers, 1):
            print(f"  論文 {i}/{len(papers)}: {paper['title'][:50]}...")
            
            extraction = self.llm_system.enhanced_functions.extract_information(
                paper.get('abstract', paper.get('content', '')),
                "キーワード、手法、結論"
            )
            
            extracted_data.append({
                "title": paper['title'],
                "extracted": extraction
            })
        
        # ステップ2: 引用の検証
        print("\nステップ2: 引用の検証...")
        citation_results = []
        for data in extracted_data:
            # 引用を含むテキストをチェック
            text = str(data)
            result = self.gc.function_library.execute(
                "citation",
                text,
                verify=True
            )
            citation_results.append(result)
        
        # ステップ3: 比較分析
        print("\nステップ3: 比較分析...")
        comparison = self._compare_papers(extracted_data)
        
        # ステップ4: レポート生成
        print("\nステップ4: レポート生成...")
        report = self._generate_report(
            extracted_data,
            comparison,
            analysis_type
        )
        
        return {
            "papers_analyzed": len(papers),
            "extracted_data": extracted_data,
            "citations": citation_results,
            "comparison": comparison,
            "report": report
        }
    
    def _compare_papers(self, extracted_data: List[Dict]) -> Dict[str, Any]:
        """論文の比較分析"""
        # 共通キーワードを見つける
        all_keywords = []
        for data in extracted_data:
            all_keywords.extend(data.get('extracted', []))
        
        # 頻度分析（簡易版）
        keyword_freq = {}
        for keyword in all_keywords:
            keyword_freq[keyword] = keyword_freq.get(keyword, 0) + 1
        
        # トップ5のキーワード
        top_keywords = sorted(
            keyword_freq.items(),
            key=lambda x: x[1],
            reverse=True
        )[:5]
        
        return {
            "total_keywords": len(set(all_keywords)),
            "top_keywords": [k for k, v in top_keywords],
            "common_themes": top_keywords[:3]
        }
    
    def _generate_report(
        self,
        extracted_data: List[Dict],
        comparison: Dict,
        analysis_type: str
    ) -> str:
        """分析レポートを生成"""
        report_lines = [
            "# 研究論文分析レポート",
            "",
            f"## 分析対象: {len(extracted_data)}本の論文",
            "",
            "## 主要な発見",
            ""
        ]
        
        # トップキーワード
        if comparison['top_keywords']:
            report_lines.append("### 頻出キーワード:")
            for keyword in comparison['top_keywords']:
                report_lines.append(f"- {keyword}")
            report_lines.append("")
        
        # 各論文のサマリー
        report_lines.append("## 論文サマリー")
        report_lines.append("")
        
        for i, data in enumerate(extracted_data, 1):
            report_lines.append(f"### 論文 {i}: {data['title']}")
            report_lines.append(f"抽出された情報:")
            for item in data.get('extracted', [])[:3]:
                report_lines.append(f"- {item}")
            report_lines.append("")
        
        return "\n".join(report_lines)


class BusinessReportGenerator:
    """
    ビジネスレポート生成システム
    
    データを分析してビジネスレポートを生成
    """
    
    def __init__(self):
        self.gc = GenerativeComputingSystem()
        self.llm_system = LLMIntegratedSystem(MockLLMProvider())
    
    def generate_report(
        self,
        data: Dict[str, Any],
        report_type: str = "quarterly"
    ) -> Dict[str, Any]:
        """
        ビジネスレポートを生成
        
        Args:
            data: ビジネスデータ
            report_type: レポートタイプ (quarterly/annual/executive)
            
        Returns:
            生成されたレポート
        """
        print(f"\n{'='*60}")
        print(f"ビジネスレポート生成: {report_type}")
        print(f"{'='*60}\n")
        
        # チェックポイントを作成
        checkpoint = self.gc.runtime.create_checkpoint(
            "before_analysis",
            "データ分析前の状態"
        )
        print(f"チェックポイント作成: {checkpoint.checkpoint_id}")
        
        # ステップ1: データの前処理
        print("\nステップ1: データの前処理...")
        processed_data = self._preprocess_data(data)
        
        # ステップ2: 主要指標の計算
        print("ステップ2: 主要指標の計算...")
        metrics = self._calculate_metrics(processed_data)
        
        # ステップ3: トレンド分析
        print("ステップ3: トレンド分析...")
        trends = self._analyze_trends(metrics)
        
        # ステップ4: 推奨事項の生成
        print("ステップ4: 推奨事項の生成...")
        recommendations = self._generate_recommendations(trends)
        
        # ステップ5: エグゼクティブサマリー
        print("ステップ5: エグゼクティブサマリー...")
        executive_summary = self._create_executive_summary(
            metrics,
            trends,
            recommendations
        )
        
        # 最終レポート
        report = {
            "report_type": report_type,
            "executive_summary": executive_summary,
            "key_metrics": metrics,
            "trends": trends,
            "recommendations": recommendations,
            "checkpoint_id": checkpoint.checkpoint_id
        }
        
        # レポートをメモリスロットに保存
        self.gc.runtime.allocate_slot(
            "final_report",
            SlotType.OUTPUT,
            report
        )
        
        print(f"\n✓ レポート生成完了")
        print(f"メモリ使用: {self.gc.runtime.get_memory_usage()}")
        
        return report
    
    def _preprocess_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """データの前処理"""
        # データ変換パイプラインを使用
        transform = self.gc.function_library.get("transform")
        
        processed = {}
        for key, value in data.items():
            if isinstance(value, str):
                processed[key] = transform.execute(
                    value,
                    ["strip", "normalize_spaces"]
                )
            else:
                processed[key] = value
        
        return processed
    
    def _calculate_metrics(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """主要指標を計算"""
        metrics = {
            "revenue": data.get("revenue", 0),
            "growth_rate": data.get("growth_rate", 0),
            "customer_count": data.get("customer_count", 0),
            "satisfaction_score": data.get("satisfaction_score", 0)
        }
        
        # 追加の計算指標
        if metrics["customer_count"] > 0:
            metrics["revenue_per_customer"] = (
                metrics["revenue"] / metrics["customer_count"]
            )
        
        return metrics
    
    def _analyze_trends(self, metrics: Dict[str, Any]) -> Dict[str, str]:
        """トレンドを分析"""
        trends = {}
        
        # 簡易的なトレンド判定
        if metrics.get("growth_rate", 0) > 0:
            trends["revenue_trend"] = "上昇傾向"
        elif metrics.get("growth_rate", 0) < 0:
            trends["revenue_trend"] = "下降傾向"
        else:
            trends["revenue_trend"] = "横ばい"
        
        if metrics.get("satisfaction_score", 0) > 80:
            trends["satisfaction_trend"] = "高い満足度"
        elif metrics.get("satisfaction_score", 0) > 60:
            trends["satisfaction_trend"] = "中程度の満足度"
        else:
            trends["satisfaction_trend"] = "改善が必要"
        
        return trends
    
    def _generate_recommendations(self, trends: Dict[str, str]) -> List[str]:
        """推奨事項を生成"""
        recommendations = []
        
        if "下降傾向" in trends.get("revenue_trend", ""):
            recommendations.append("収益改善のための施策を実施してください")
            recommendations.append("コスト削減の機会を探索してください")
        
        if "改善が必要" in trends.get("satisfaction_trend", ""):
            recommendations.append("顧客満足度向上プログラムを開始してください")
            recommendations.append("顧客フィードバックの収集を強化してください")
        
        if not recommendations:
            recommendations.append("現状を維持しつつ、成長機会を探索してください")
        
        return recommendations
    
    def _create_executive_summary(
        self,
        metrics: Dict[str, Any],
        trends: Dict[str, str],
        recommendations: List[str]
    ) -> str:
        """エグゼクティブサマリーを作成"""
        summary_parts = [
            f"収益: ¥{metrics.get('revenue', 0):,}",
            f"成長率: {metrics.get('growth_rate', 0)}%",
            f"収益トレンド: {trends.get('revenue_trend', 'データなし')}",
            f"主要推奨事項: {recommendations[0] if recommendations else 'なし'}"
        ]
        
        return " | ".join(summary_parts)


class DataPipelineOrchestrator:
    """
    データパイプラインオーケストレーター
    
    複雑なデータ処理ワークフローを管理
    """
    
    def __init__(self):
        self.gc = GenerativeComputingSystem()
    
    def execute_pipeline(
        self,
        pipeline_config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        データパイプラインを実行
        
        Args:
            pipeline_config: パイプライン設定
            
        Returns:
            実行結果
        """
        print(f"\n{'='*60}")
        print("データパイプライン実行")
        print(f"{'='*60}\n")
        
        stages = pipeline_config.get("stages", [])
        input_data = pipeline_config.get("input_data", {})
        
        # 初期データをスロットに配置
        self.gc.runtime.allocate_slot(
            "pipeline_input",
            SlotType.CONTEXT,
            input_data
        )
        
        results = {}
        current_data = input_data
        
        # 各ステージを実行
        for i, stage in enumerate(stages, 1):
            print(f"ステージ {i}/{len(stages)}: {stage['name']}")
            
            # チェックポイントを作成
            checkpoint = self.gc.runtime.create_checkpoint(
                f"stage_{i}_start",
                f"ステージ {i} 開始前"
            )
            
            try:
                # ステージを実行
                stage_result = self._execute_stage(stage, current_data)
                
                # 結果を保存
                results[stage['name']] = stage_result
                current_data = stage_result
                
                # スロットに保存
                self.gc.runtime.allocate_slot(
                    f"stage_{i}_output",
                    SlotType.INTERMEDIATE,
                    stage_result
                )
                
                print(f"  ✓ 完了")
                
            except Exception as e:
                print(f"  ✗ エラー: {e}")
                print(f"  チェックポイント {checkpoint.checkpoint_id} に復元")
                self.gc.runtime.restore_checkpoint(checkpoint.checkpoint_id)
                results[stage['name']] = {"error": str(e)}
        
        # 最終結果
        self.gc.runtime.allocate_slot(
            "pipeline_output",
            SlotType.OUTPUT,
            current_data
        )
        
        return {
            "stages_executed": len(stages),
            "results": results,
            "final_output": current_data,
            "memory_usage": self.gc.runtime.get_memory_usage()
        }
    
    def _execute_stage(
        self,
        stage: Dict[str, Any],
        input_data: Any
    ) -> Any:
        """個別ステージを実行"""
        stage_type = stage.get("type", "transform")
        
        if stage_type == "transform":
            # データ変換
            transform = self.gc.function_library.get("transform")
            pipeline = stage.get("pipeline", ["strip"])
            
            if isinstance(input_data, str):
                return transform.execute(input_data, pipeline)
            else:
                return input_data
        
        elif stage_type == "filter":
            # データフィルタリング
            condition = stage.get("condition", lambda x: True)
            if isinstance(input_data, list):
                return [x for x in input_data if condition(x)]
            else:
                return input_data
        
        elif stage_type == "aggregate":
            # データ集約
            if isinstance(input_data, list):
                return {
                    "count": len(input_data),
                    "items": input_data[:5]  # 最初の5項目
                }
            else:
                return input_data
        
        else:
            return input_data


def demo_use_cases():
    """実用的なユースケースのデモ"""
    
    # ユースケース1: 研究論文分析
    print("\n" + "="*70)
    print("ユースケース1: 研究論文分析")
    print("="*70)
    
    analyzer = ResearchPaperAnalyzer()
    
    sample_papers = [
        {
            "title": "大規模言語モデルの最新動向",
            "abstract": "本研究では、大規模言語モデルの発展と応用について調査します。"
        },
        {
            "title": "自然言語処理における転移学習",
            "abstract": "転移学習を用いた自然言語処理タスクの性能向上を実証します。"
        },
        {
            "title": "AIの倫理的考察",
            "abstract": "人工知能技術の社会実装における倫理的課題を議論します。"
        }
    ]
    
    paper_analysis = analyzer.analyze_papers(sample_papers)
    print("\n--- 分析結果 ---")
    print(f"論文数: {paper_analysis['papers_analyzed']}")
    print(f"トップキーワード: {paper_analysis['comparison']['top_keywords']}")
    
    # ユースケース2: ビジネスレポート生成
    print("\n" + "="*70)
    print("ユースケース2: ビジネスレポート生成")
    print("="*70)
    
    generator = BusinessReportGenerator()
    
    business_data = {
        "revenue": 10000000,
        "growth_rate": 15.5,
        "customer_count": 250,
        "satisfaction_score": 85
    }
    
    business_report = generator.generate_report(business_data, "quarterly")
    print("\n--- レポートサマリー ---")
    print(business_report['executive_summary'])
    print(f"\n推奨事項:")
    for rec in business_report['recommendations']:
        print(f"  - {rec}")
    
    # ユースケース3: データパイプライン
    print("\n" + "="*70)
    print("ユースケース3: データパイプライン")
    print("="*70)
    
    orchestrator = DataPipelineOrchestrator()
    
    pipeline_config = {
        "input_data": "  Sample Data  with  extra  spaces  ",
        "stages": [
            {
                "name": "cleanup",
                "type": "transform",
                "pipeline": ["strip", "normalize_spaces"]
            },
            {
                "name": "uppercase",
                "type": "transform",
                "pipeline": ["uppercase"]
            }
        ]
    }
    
    pipeline_result = orchestrator.execute_pipeline(pipeline_config)
    print("\n--- パイプライン結果 ---")
    print(f"実行ステージ数: {pipeline_result['stages_executed']}")
    print(f"最終出力: {pipeline_result['final_output']}")
    
    print("\n" + "="*70)
    print("全ユースケース完了！")
    print("="*70)


if __name__ == "__main__":
    demo_use_cases()
