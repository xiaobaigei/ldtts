from typing import List, Dict, Callable

class EnsembleVoter:
    def __init__(self, generators: List[Callable]):
        self.generators = generators
    
    def generate_candidates(self, question: str, schema: Dict[str, List[str]], 
                           examples: List[Dict[str, str]] = None) -> List[str]:
        candidates = []
        for gen in self.generators:
            try:
                sql = gen(question, schema, examples)
                if sql:
                    candidates.append(sql)
            except Exception as e:
                print(f"Generator error: {e}")
        return candidates
    
    def vote_by_execution(self, candidates: List[str], db_path: str) -> str:
        if not candidates:
            return candidates[0] if candidates else ""
        
        results = {}
        for sql in candidates:
            result = self._execute_sql(sql, db_path)
            result_key = str(result)
            if result_key not in results:
                results[result_key] = []
            results[result_key].append(sql)
        
        if results:
            max_votes = max(results.values(), key=len)
            return max_votes[0]
        return candidates[0]
    
    def _execute_sql(self, sql: str, db_path: str) -> List:
        import sqlite3
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            cursor.execute(sql)
            return cursor.fetchall()
        except Exception:
            return None
        finally:
            conn.close()
