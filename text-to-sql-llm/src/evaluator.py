import sqlite3
from typing import List, Tuple

class Evaluator:
    @staticmethod
    def execute_sql(db_path: str, sql: str) -> Tuple[bool, List]:
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            cursor.execute(sql)
            result = cursor.fetchall()
            return True, result
        except Exception as e:
            return False, str(e)
        finally:
            conn.close()
    
    @staticmethod
    def execution_accuracy(predicted_sql: str, ground_truth_sql: str, db_path: str) -> bool:
        pred_ok, pred_result = Evaluator.execute_sql(db_path, predicted_sql)
        truth_ok, truth_result = Evaluator.execute_sql(db_path, ground_truth_sql)
        
        if not pred_ok or not truth_ok:
            return False
        
        return sorted(pred_result) == sorted(truth_result)
    
    @staticmethod
    def exact_set_match(predicted_sql: str, ground_truth_sql: str, db_path: str) -> bool:
        pred_ok, pred_result = Evaluator.execute_sql(db_path, predicted_sql)
        truth_ok, truth_result = Evaluator.execute_sql(db_path, ground_truth_sql)
        
        if not pred_ok or not truth_ok:
            return False
        
        pred_set = set(tuple(row) for row in pred_result)
        truth_set = set(tuple(row) for row in truth_result)
        
        return pred_set == truth_set
    
    @staticmethod
    def component_match(predicted_sql: str, ground_truth_sql: str) -> dict:
        pred_lower = predicted_sql.lower()
        truth_lower = ground_truth_sql.lower()
        
        components = {
            'select': 'select' in pred_lower and 'select' in truth_lower,
            'from': 'from' in pred_lower and 'from' in truth_lower,
            'where': 'where' in pred_lower and 'where' in truth_lower,
            'group_by': ('group by' in pred_lower or 'group_by' in pred_lower) and 
                       ('group by' in truth_lower or 'group_by' in truth_lower),
            'having': 'having' in pred_lower and 'having' in truth_lower,
            'order_by': ('order by' in pred_lower or 'order_by' in pred_lower) and 
                       ('order by' in truth_lower or 'order_by' in truth_lower),
            'limit': 'limit' in pred_lower and 'limit' in truth_lower
        }
        
        return components
    
    @staticmethod
    def evaluate_batch(predictions: List[str], ground_truths: List[str], db_paths: List[str]) -> dict:
        ex_count = 0
        esm_count = 0
        cm_counts = {k: 0 for k in ['select', 'from', 'where', 'group_by', 'having', 'order_by', 'limit']}
        
        for pred, truth, db_path in zip(predictions, ground_truths, db_paths):
            if Evaluator.execution_accuracy(pred, truth, db_path):
                ex_count += 1
            
            if Evaluator.exact_set_match(pred, truth, db_path):
                esm_count += 1
            
            cm = Evaluator.component_match(pred, truth)
            for k, v in cm.items():
                if v:
                    cm_counts[k] += 1
        
        total = len(predictions)
        return {
            'execution_accuracy': ex_count / total if total > 0 else 0,
            'exact_set_match': esm_count / total if total > 0 else 0,
            'component_match': {k: v / total if total > 0 else 0 for k, v in cm_counts.items()}
        }
