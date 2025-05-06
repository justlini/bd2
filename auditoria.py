from datetime import datetime
from api.conn import BaseDeDados

class ManageAuditoria:
    def __init__(self):
        self.bd = BaseDeDados()

    def insert_Log(self, p_utilizador_bd, p_utilizador_app, p_acao):
        conn = self.bd.get_conn()
        if conn is None:
            return "Erro de conexÃ£o com a base de dados."
        try:
            p_data=datetime.datetime.now()
            cur = conn.cursor()
            cur.execute("CALL inserir_log(%s, %s, %s,%s);",
                        ("ola", "adeus", p_data, "ooooooooooo"))
            conn.commit()
            cur.close()
            conn.close()
            return "Log inserido com sucesso.!"
        except Exception as e:
            return str(e)