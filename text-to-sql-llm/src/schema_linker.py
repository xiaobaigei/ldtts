import re
from typing import List, Dict, Tuple

class SchemaLinker:
    def __init__(self):
        self.table_keywords = ['table', 'from', 'select', 'join']
    
    def extract_entities(self, question: str) -> List[str]:
        tokens = re.findall(r'\b[A-Za-z][a-zA-Z0-9_]*\b', question)
        return [t.lower() for t in tokens if len(t) > 2]
    
    def jaccard_similarity(self, s1: str, s2: str) -> float:
        set1 = set(s1.lower().split())
        set2 = set(s2.lower().split())
        if not set1 and not set2:
            return 1.0
        return len(set1 & set2) / len(set1 | set2)
    
    def link_schema(self, question: str, schema: Dict[str, List[str]]) -> Tuple[List[str], List[str]]:
        entities = self.extract_entities(question)
        linked_tables = []
        linked_columns = []
        
        for table_name, columns in schema.items():
            table_name_lower = table_name.lower()
            for entity in entities:
                if self.jaccard_similarity(entity, table_name_lower) > 0.5:
                    if table_name not in linked_tables:
                        linked_tables.append(table_name)
                    for col in columns:
                        col_lower = col.lower()
                        if any(self.jaccard_similarity(entity, col_part) > 0.4 
                               for col_part in col_lower.split('_')):
                            if col not in linked_columns:
                                linked_columns.append(col)
        
        if not linked_tables:
            linked_tables = list(schema.keys())[:2]
        
        return linked_tables, linked_columns
    
    def get_simplified_schema(self, question: str, full_schema: Dict[str, List[str]]) -> Dict[str, List[str]]:
        linked_tables, linked_columns = self.link_schema(question, full_schema)
        simplified = {}
        for table in linked_tables:
            if table in full_schema:
                simplified[table] = full_schema[table]
        return simplified
