import psycopg2
import os

class BaseDeDados:
    def __init__(self, user=None, password=None):
        #self.host = os.getenv("db_host", "localhost")
        #self.database = os.getenv("db_database", "bd2")
        #self.user = os.getenv("db_user", "postgres")
        #self.password = os.getenv("db_password", "postgres")
        #dados server
        self.host = os.getenv("db_host")
        self.database = os.getenv("db_database")
        self.user = user  # Use provided user or default
        self.password = password if password else os.getenv("db_password")  # Use provided password or default
        print(f"Conectando ao banco de dados {self.database} no host {self.host} com o usuário {self.user}.")

    def get_conn(self):
        # Verifica se todas as variáveis de ambiente existem
        if not all([self.host, self.database, self.user, self.password]):
            return None  # Retorna None se faltar alguma variável

        try:
            # Conecta à base de dados
            connection = psycopg2.connect(
                host=self.host,
                database=self.database,
                user=self.user,
                password=self.password
            )
            return connection
        except Exception as e:
            print(f"Erro ao coneceetar à base de dados: {str(e)}")
            return None
        
    