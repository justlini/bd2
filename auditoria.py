from datetime import datetime
from api.conn import BaseDeDados

class ManageAuditoria:
    def __init__(self):
        self.bd = BaseDeDados()

    def insert_Log(self, p_utilizador_bd, p_utilizador_app,p_dataLog, p_acao):
        conn = self.bd.get_conn()
        if conn is None:
            return "Erro de conexÃo com a base de dados."
        try:
            cur = conn.cursor()
            cur.execute("CALL inserir_log(%s, %s, %s,%s);",
                        (p_utilizador_bd, p_utilizador_app, p_dataLog, p_acao))
            conn.commit()
            cur.close()
            conn.close()
        except Exception as e:
            return str(e)