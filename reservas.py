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
            return "Pagar reserva"
        except Exception as e:
            return str(e)
        
    def cancelar_reserva(self,p_idreserva):
        conn = self.bd.get_conn()
        if conn is None:
            return "Erro ligação a base de dados."
        
        try:
            cur = conn.cursor()
            cur.execute("Select * from cancelar_reserva(%s);", (p_idreserva,))
            conn.commit()
            cur.close()
            conn.close()
            return "Reserva cancelada com sucesso!"
        except Exception as e:
            return str(e)
        
    def ver_reservasCliente(self,p_idcliente):
        conn = self.bd.get_conn()
        if conn is None:
            return "Erro de conexão com a base de dados."

        try:
            cur = conn.cursor()
            cur.execute("Select * from verreservas_cliente(%s);", (p_idcliente,))
            reservas = cur.fetchall()
            cur.close()
            conn.close()
            return reservas
        except Exception as e:
            return str(e)
        
    def ver_todasReservas(self):
        conn = self.bd.get_conn()
        if conn is None:
            return "Erro de conexão com a base de dados."

        try:
            cur = conn.cursor()
            cur.execute("Select * from reservas_admin;")
            reservas = cur.fetchall()
            cur.close()
            conn.close()
            return reservas
        except Exception as e:
            return str(e)
        
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
    
    def verDisponibilidadeQuarto(self,p_idquarto,data_pretendida):
        conn = self.bd.get_conn()
        if conn is None:
            return "Erro de conexão com a base de dados."
        
        try:
            cur = conn.cursor()
            cur.execute("Select quarto_ocupado(%s, %s);", (p_idquarto, data_pretendida))
            result = cur.fetchone()
            cur.close()
            conn.close()
            return result[0] if result else False
        except Exception as e:
            return False
    
    