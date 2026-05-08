import requests
import pandas as pd
import os
from sqlalchemy import create_engine

Shoptan = os.getenv('Shoptan')
Xangai = os.getenv('Xangai')
user = os.getenv('user')
password = os.getenv('password')
host = os.getenv('host')
port = os.getenv('port')
dbname = os.getenv('dbname')

#extrair dados da API
def coletar_dados(access_token, nome_empresa):
    url_base = "https://api.maino.com.br/api/v2/contas_a_recebers"
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }

    todos_os_dados = []
    pagina =     1

    while True:
        params = {"page": pagina, "per_page": 100}
        response = requests.get(url_base, headers=headers, params=params)

        if response.status_code != 200:
            print(f"Erro com a empresa {nome_empresa}: {response.status_code}")
            return None

        dados = response.json()
        contas = dados.get("contas") or dados.get("data", {}).get("contas_a_receber", [])

        if not contas:
            break

        for conta in contas:
            todos_os_dados.append({

                "Processo": (conta.get("processo") or {}).get("codigo", ""),
                "numero_do_documento": conta.get("numero_titulo", ""),
                "Vencimento": conta.get("data_vencimento", ""),
                "Valor": float(conta.get("valor") or 0),
                "data_pagamento": conta.get("data_pagamento", ""),
                "cliente": (conta.get("cliente") or {}).get("razao_social", ""),
                "Tags": ", ".join([tag.get("nome", "") for tag in (conta.get("tags") or [])])
                
            })

        pagina += 1
    return pd.DataFrame(todos_os_dados)

#Xangai carregamento
def conexao():
    USER = os.getenv("user")
    PASSWORD = os.getenv("password")
    HOST = os.getenv("host")
    PORT = os.getenv("port")
    DBNAME = os.getenv("dbname")

    DATABASE_URL = f"postgresql+psycopg2://{USER}:{PASSWORD}@{HOST}:{PORT}/{DBNAME}?sslmode=require"

    engine = create_engine(DATABASE_URL)

    try:
        with engine.connect() as connection:
            print("Connection successful!")
    except Exception as e:
        print(f"Failed to connect: {e}")
    return engine

conn = conexao()

for x in ["Xangai", "Shoptan"]:
    df = coletar_dados(os.getenv(x), x)
    df = df[df['data_pagamento'].isna()]
    df.to_sql(f'tabela_{x}', conn, if_exists="replace", index=False)
    print(f"Dados da empresa {x} carregados com sucesso!")
