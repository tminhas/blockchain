import sqlite3

# Conecte-se ao banco de dados (criará um novo arquivo se não existir)
conn = sqlite3.connect('db.sqlite')

# Crie um cursor para executar comandos SQL
cursor = conn.cursor()

# Crie uma tabela chamada 'usuarios'
cursor.execute('''CREATE TABLE usuarios
                  (id INTEGER PRIMARY KEY AUTOINCREMENT,
                   nome TEXT NOT NULL,
                   idade INTEGER NOT NULL)''')

# Salve as alterações e feche a conexão com o banco de dados
conn.commit()
conn.close()