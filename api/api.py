from flask import Flask, request, jsonify
from conn import get_db_connection
from http.client import BAD_REQUEST, CREATED, INTERNAL_SERVER_ERROR, CONFLICT

app = Flask(__name__)

def insert_user(nome, email, nif, senha, numerotelefone):
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        # Use CALL to call the stored procedure in PostgreSQL
        cur.execute("""
            CALL inserir_utilizadores(%s, %s, %s, %s, %s);
        """, (nome, email, nif, senha, numerotelefone))
        
        conn.commit()
        cur.close()
        conn.close()
        
        return True, "User inserted successfully!"
    except Exception as e:
        return False, str(e)

def user_exists(email, nif):
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        query = "SELECT 1 FROM public.utilizadores WHERE email = %s OR nif = %s LIMIT 1"
        cur.execute(query, (email, nif))
        result = cur.fetchone()
        cur.close()
        conn.close()
        return result is not None
    except Exception as e:
        return False

@app.route("/register", methods=['POST'])
def register():
    data = request.get_json()

    # Check if all required fields are present
    if "nome" not in data or "email" not in data or "nif" not in data or "senha" not in data or "numerotelefone" not in data:
        return jsonify({"error": "Missing required parameters"}), BAD_REQUEST

    # Check if user already exists
    if user_exists(data["email"], data["nif"]):
        return jsonify({"error": "User with this email or NIF already exists"}), CONFLICT

    # Insert user into database
    #insert
    success, message = insert_user(
        data['nome'], 
        data['email'], 
        data['nif'], 
        data['senha'], 
        data['numerotelefone']
    )

    if success:
        return jsonify({"message": message}), CREATED
    else:
        return jsonify({"error": message}), INTERNAL_SERVER_ERROR

if __name__ == '__main__':
    app.run(debug=True)
