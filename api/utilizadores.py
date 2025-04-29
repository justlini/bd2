from bd2.api.conn import BaseDeDados
import bcrypt
class Utilizadores:
    
    def __init__(self):
        self.bd = BaseDeDados()
    
    def insert_user(self,nome, email, nif, senha, numerotelefone):
        conn = self.bd.get_conn()
        #se a conexaõ for None retorna um erro de conexão
        if conn is None:
            return "Erro de conexão com a base de dados."
        
        try:
            cur = conn.cursor()
            #procidure inserir_utilizadores
            cur.execute("CALL inserir_clientes(%s, %s, %s, %s, %s);", (nome, email, nif, senha, numerotelefone))
            conn.commit()
            cur.close()
            conn.close()
            return "Utilizador inserido com sucesso!"
        except Exception as e:
            return str(e)
        
    def insert_emp(self,idemp, tipoemp, idcliente):
        conn = self.bd.get_conn()
        if conn is None:
            return "Erro de conexão com a base de dados."

        try:
            cur = conn.cursor()
            cur.execute("CALL inserir_emp(%s, %s, %s);", (idemp, tipoemp, idcliente))
            conn.commit()
            cur.close()
            conn.close()
            return "Empregado inserirdo com sucesso!"
        except Exception as e:
            return str(e)
        
    def emp_exists(self,idemp, idcliente):
        conn = self.bd.get_conn()
        if conn is None:
            return False  # Se não conseguir se conectar ao banco, assume que o usuário não existe
    
        try:
            cur = conn.cursor()
            cur.execute("Select emp_existe(%s, %s);", (idemp, idcliente))
            result = cur.fetchone()
            cur.close()
            conn.close()
            return result[0] if result else False  # Retorna True se o utilizador existir
        except Exception as e:
            return False  # Retorna False caso haja erro na execução da consulta
        
    def user_exists(self,email, nif):
        conn = self.bd.get_conn()
        if conn is None:
            return False  # Se não conseguir se conectar na base de dados, assume que o utilizador não existe
        try:
            cur = conn.cursor()
            cur.execute("Select user_existe(%s,%s);", (email, nif))
            result = cur.fetchone()
            cur.close()
            conn.close()
            return result[0] if result else False  # Retorna True se o utilizador existir
        except Exception as e:
            return False  # Retorna False caso haja erro na execução da consultaº
    
        


    
