from api.conn import BaseDeDados

class ManageReservas:
    def __init__(self):
        self.bd = BaseDeDados()
        
    def insert_reserva(self,p_idcliente, p_idquarto, p_datacheckin,p_datacheckout):
        conn = self.bd.get_conn()
        if conn is None:
            return "Erro de conexão com a base de dados."

        try:
            cur = conn.cursor()
            cur.execute("CALL inserir_reserva(%s, %s, %s,%s);", (p_idcliente, p_idquarto, p_datacheckin,p_datacheckout))
            conn.commit()
            cur.close()
            conn.close()
            return "Reserva feita feita com sucesso!"
        except Exception as e:
            return str(e)
        
    def pagar_reserva(self,p_idreserva):
        conn = self.bd.get_conn()
        if conn is None:
            return "Erro de conexão com a base de dados."

        try:
            cur = conn.cursor()
            cur.execute("Select * from pagar_reserva(%s);", (p_idreserva,))
            conn.commit()
            cur.close()
            conn.close()
            return "Reserva paga com sucesso!"
        except Exception as e:
            return str(e)
    