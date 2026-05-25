import re
from typing import Dict, List, Tuple

class ComplexityEstimator:
    """
    评估自然语言问题的复杂度（Easy/Medium/Hard/Extra Hard）
    用于自适应选择 few-shot 示例数量
    """
    
    HARD_KEYWORDS = [
        'having', 'except', 'union', 'intersect', 
        'at least', 'all', 'every', 'most', 'least',
        'average', 'total', 'sum', 'count', 'group',
        'order by', 'limit', 'top', 'bottom'
    ]
    
    NESTED_PATTERNS = [
        r'higher than.*average', r'lower than.*average',
        r'more than.*average', r'less than.*average',
        r'who.*most', r'which.*most',
        r'compare', r'ratio', r'percentage'
    ]
    
    def __init__(self):
        pass
    
    def assess_complexity(self, question: str, linked_schema: Dict) -> str:
        """
        评估问题复杂度
        
        Args:
            question: 自然语言问题
            linked_schema: 已链接的 schema
            
        Returns:
            复杂度等级："easy", "medium", "hard", "extra"
        """
        question_lower = question.lower()
        score = 0
        
        # 1. 关键词检测（+1 分/个）
        for keyword in self.HARD_KEYWORDS:
            if keyword in question_lower:
                score += 1
        
        # 2. 嵌套语义检测（+2 分/个）
        for pattern in self.NESTED_PATTERNS:
            if re.search(pattern, question_lower):
                score += 2
        
        # 3. 表数量检测（兼容两种格式）
        if 'tables' in linked_schema:
            num_tables = len(linked_schema.get('tables', []))
        else:
            num_tables = len(linked_schema)  # linked_schema 本身是字典，键为表名
        if num_tables >= 3:
            score += 2
        elif num_tables >= 2:
            score += 1
        
        # 4. 问题长度（长问题通常更复杂）
        if len(question.split()) > 15:
            score += 1
        
        # 5. 映射到复杂度等级
        if score <= 1:
            return "easy"
        elif score <= 3:
            return "medium"
        elif score <= 5:
            return "hard"
        else:
            return "extra"
    
    def get_example_count(self, complexity: str) -> int:
        """
        根据复杂度获取示例数量
        
        Returns:
            示例数量 k
        """
        mapping = {
            "easy": 1,
            "medium": 3,
            "hard": 5,
            "extra": 7
        }
        return mapping.get(complexity, 3)
    
    def assess_and_get_k(self, question: str, linked_schema: Dict) -> Tuple[str, int]:
        """
        一次性获取复杂度等级和示例数量
        """
        complexity = self.assess_complexity(question, linked_schema)
        k = self.get_example_count(complexity)
        return complexity, k
