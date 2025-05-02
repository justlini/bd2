from api.conn import BaseDeDados


class ManageTransacoes:
    def __init__(self):
        self.bd = BaseDeDados()

    def ver_pagamentos(self):
        conn = self.bd.get_conn()
        if conn is None:
            return "Erro de conexão com a base de dados."

        try:
            cur = conn.cursor()
            cur.execute("Select * from ver_todas_transacoes;")
            pagamentos = cur.fetchall()
            cur.close()
            conn.close()
            return pagamentos
        except Exception as e:
            return str(e)

    def verpagamentos_cliente(self, p_idcliente):
        conn = self.bd.get_conn()
        if conn is None:
            return "Erro de conexão com a base de dados."

        try:
            cur = conn.cursor()
            cur.execute("Select * from vertransacoes_cliente(%s);", (p_idcliente,))
            pagamentos = cur.fetchall()
            cur.close()
            conn.close()
            return pagamentos
        except Exception as e:
            return str(e)
        
        