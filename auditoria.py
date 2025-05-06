from datetime import datetime
from api.conn import BaseDeDados

class ManageAuditoria:
    def __init__(self):
        self.bd = BaseDeDados()

    def insert_Log(self, p_utilizador_bd, p_utilizador_app,p_data, p_acao):
        conn = self.bd.get_conn()
        if conn is None:
            return "Erro de conexÃ£o com a base de dados."
        try:
            p_data='2025-05-06'
            cur = conn.cursor()
            cur.execute("CALL inserir_log(%s, %s, %s,%s);",
                        (p_utilizador_bd, p_utilizador_app, p_data, p_acao))
            conn.commit()
            cur.close()
            conn.close()
            return "Log inserido com sucesso.!"
        except Exception as e:
            return str(e)