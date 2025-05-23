import psycopg2
import os

class BaseDeDados:
    def __init__(self, user=None, password=None, user_type=None):
        self.host = os.getenv("db_host")
        self.database = os.getenv("db_database")

        # if para login
        if user_type == "admin":
            self.user = os.getenv("admin_db_user")
            self.password = os.getenv("db_password")
        elif user_type == "cliente":
            self.user = os.getenv("cliente_db_user")
            self.password = os.getenv("db_password")
        elif user_type == "rececionista":
            self.user = os.getenv("rececionista_db_user")
            self.password = os.getenv("db_password")
        else:
            # default se nao conseguir nada tirar depois
            self.user = user if user else os.getenv("db_user")
            self.password = password if password else os.getenv("db_password")

        print(f"Ligacao feita na {self.database} no host {self.host} com o user {self.user}.")

    def get_conn(self):
        if not all([self.host, self.database, self.user, self.password]):
            print("Faltam variaveis de ambiente para a ligação à base de dados.")
            return None

        try:
            connection = psycopg2.connect(
                host=self.host,
                database=self.database,
                user=self.user,
                password=self.password
            )
            print("Ligação à base de dados estabelecida com sucesso.")
            return connection
        except Exception as e:
            print(f"Erro ao conectar à base de dados: {str(e)}")
            return None
        
    