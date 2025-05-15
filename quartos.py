from api.conn import BaseDeDados

class ManageQuartos:
    def __init__(self):
        self.bd = BaseDeDados()
        
    def insert_quarto(self,p_numeroquarto, p_precoquarto, p_tipoquarto):
        conn = self.bd.get_conn()
        if conn is None:
            return "Erro de conexão com a base de dados."

        try:
            cur = conn.cursor()
            cur.execute("CALL inserirquartos(%s, %s, %s);", (p_numeroquarto, p_precoquarto, p_tipoquarto))
            conn.commit()
            cur.close()
            conn.close()
            return "Quarto inserido com sucesso!"
        except Exception as e:
            return str(e)
    
    def mudarPrecoQuarto(self,p_idquarto, p_precoQuarto):
        conn = self.bd.get_conn()
        if conn is None:
            return "Erro de conexão com a base de dados."

        try:
            cur = conn.cursor()
            cur.execute("CALL atualizar_precoQuarto(%s, %s);", (p_idquarto, p_precoQuarto))
            conn.commit()
            cur.close()
            conn.close()
            return "Preco do quarto alterado com sucesso!"
        except Exception as e:
            return str(e)
        
    
    def get_ImagensQuarto(self,p_idquarto):
        conn = self.bd.get_conn()
        if conn is None:
            return "Erro de conexão com a base de dados."
        try:
            cur = conn.cursor()
            cur.execute("SELECT * from get_imagensQuarto(%s);", (p_idquarto,))
            imagens = cur.fetchall()
            cur.close()
            conn.close()
            return imagens
        except Exception as e:
            return str(e)
        
        
    def upload_imagem_quarto(self,p_idquarto, p_imagem):
        conn = self.bd.get_conn()
        if conn is None:
            return "Erro de conexão com a base de dados."
        try:
            cur = conn.cursor()
            cur.execute("CALL inserir_imagem(%s, %s);", (p_idquarto, p_imagem))
            conn.commit()
            cur.close()
            conn.close()
            return "Imagem do quarto carregada com sucesso!"
        except Exception as e:
            return str(e)
        
    def ver_disponibilidade_quarto(self):
        conn = self.bd.get_conn()
        if conn is None:
            return "Erro de conexão com a base de dados."
        try:
            cur = conn.cursor()
            cur.execute("SELECT * from verdisponibilidadequarto;")
            disponibilidade = cur.fetchall()
            cur.close()
            conn.close()
            return disponibilidade
        except Exception as e:
            return str(e)
        
    def quarto_exists(self,p_numeroquarto):
        conn = self.bd.get_conn()
        if conn is None:
            return False 

        try:
            cur = conn.cursor()
            cur.execute("Select quarto_existe(%s);", (p_numeroquarto,))
            result = cur.fetchone()
            cur.close()
            conn.close()
            return result[0] if result else False  # Retorna True se o quarto existir
        except Exception as e:
            return False  # Retorna False caso haja erro na execução da consulta
        
    def mudarTipoQuarto(self,p_idquarto, p_tipoquarto):
        conn = self.bd.get_conn()
        if conn is None:
            return "Erro de conexão com a base de dados."
        if p_tipoquarto not in ["casal", "solteiro"]:
            return "Tipo de quarto invalido!"
        try:
            cur = conn.cursor()
            if p_tipoquarto == "casal":
                cur.execute("CALL atualizar_tipocasal(%s);", (p_idquarto,))
            elif p_tipoquarto == "solteiro":
                cur.execute("CALL atualizar_tiposolteiro(%s);", (p_idquarto,))
            conn.commit()
            cur.close()
            conn.close()
            return "Tipo do quarto alterado com sucesso!"
        except Exception as e:
            if conn:
                conn.close()
            return f"Erro ao alterar tipo do quarto: {str(e)}"

    
        
    

