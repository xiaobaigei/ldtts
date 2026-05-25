import re
from typing import List, Dict, Tuple, Optional
from .complexity_estimator import ComplexityEstimator

class ExampleRetriever:
    """
    基于相似度的 Few-shot 示例检索模块
    支持复杂度感知的自适应检索
    """
    
    def __init__(self):
        self.examples = []
        self.complexity_estimator = ComplexityEstimator()
    
    def build_index(self, examples: List[Dict[str, str]]):
        """
        构建示例索引
        
        Args:
            examples: 示例列表，每个示例包含 question, sql, schema, complexity（可选）
        """
        self.examples = examples
        
        # 如果没有标注复杂度，自动评估
        for ex in self.examples:
            if 'complexity' not in ex:
                ex['complexity'] = self.complexity_estimator.assess_complexity(
                    ex['question'], 
                    {'tables': [], 'columns': []}
                )
    
    def _jaccard_similarity(self, s1: str, s2: str) -> float:
        """计算 Jaccard 相似度（基于 trigram）"""
        def get_trigrams(s: str) -> set:
            s = s.lower()
            if len(s) < 3:
                return {s}
            return {s[i:i+3] for i in range(len(s)-2)}
        
        set1 = get_trigrams(s1)
        set2 = get_trigrams(s2)
        
        if not set1 and not set2:
            return 1.0
        return len(set1 & set2) / len(set1 | set2)
    
    def retrieve(self, question: str, schema_str: str, top_k: int = 3, 
                 target_complexity: Optional[str] = None) -> List[Dict[str, str]]:
        """
        检索最相似的示例
        
        Args:
            question: 当前问题
            schema_str: 已链接的 schema 字符串
            top_k: 返回的示例数量
            target_complexity: 目标复杂度（如果为 None，则自动评估）
            
        Returns:
            检索到的示例列表
        """
        if not self.examples:
            return []
        
        # 自动评估复杂度
        if target_complexity is None:
            complexity, k = self.complexity_estimator.assess_and_get_k(
                question, 
                {'tables': [], 'columns': []}
            )
            top_k = k
        
        query = f"{question} {schema_str}"
        scored = []
        
        for ex in self.examples:
            text = f"{ex['question']} {ex['schema']}"
            score = self._jaccard_similarity(query, text)
            
            # 复杂度匹配加分
            if target_complexity and ex.get('complexity') == target_complexity:
                score *= 1.2
            
            scored.append((score, ex))
        
        # 按分数排序
        scored.sort(reverse=True, key=lambda x: x[0])
        
        # 优先返回同复杂度的示例
        if target_complexity:
            same_complexity = [ex for score, ex in scored 
                              if ex.get('complexity') == target_complexity]
            if len(same_complexity) >= top_k:
                return same_complexity[:top_k]
        
        # 如果同复杂度不够，混合返回
        return [ex for _, ex in scored[:top_k]]
    
    def retrieve_adaptive(self, question: str, schema_str: str, 
                         linked_schema: Dict) -> List[Dict[str, str]]:
        """
        自适应检索：根据问题复杂度自动决定示例数量
        
        Args:
            question: 当前问题
            schema_str: schema 字符串
            linked_schema: 已链接的 schema 字典
            
        Returns:
            检索到的示例列表
        """
        complexity, k = self.complexity_estimator.assess_and_get_k(
            question, linked_schema
        )
        
        print(f"[DEBUG] Complexity: {complexity}, Retrieving {k} examples")
        
        return self.retrieve(question, schema_str, top_k=k, 
                           target_complexity=complexity)
