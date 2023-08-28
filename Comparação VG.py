import pandas as pd

# Carregar os dados dos servidores de um arquivo em .json
arquivo_Servidores_007 = "C:\\Users\\henri\\OneDrive\\Área de Trabalho\\pasta nova de projetinhos\\Dados_Varzea_Grande.json"

data_servidores = pd.read_json(arquivo_Servidores_007, orient='index')
data_servidores = data_servidores.reset_index()
data_servidores.columns = ['matricula', 'NOME']

# Salvar os dados dos servidores em um arquivo CSV
data_servidores.to_csv("Servidores_008.csv", index=False)

# Carregar os dados dos alunos dos anos 2020 a 2023
urls_alunos = [
    "https://dados.ifmt.edu.br/dataset/6b7c7c38-587a-436b-a7b2-4e3ca59d1ca8/resource/fc30244a-166d-4830-a66d-a573ebe187eb/download/aluno.csv",
    "https://dados.ifmt.edu.br/dataset/6b7c7c38-587a-436b-a7b2-4e3ca59d1ca8/resource/d2a472aa-3a02-4d45-bc65-5852fa9be664/download/aluno.csv",
    "https://dados.ifmt.edu.br/dataset/6b7c7c38-587a-436b-a7b2-4e3ca59d1ca8/resource/96f114e2-58f9-4f59-9c44-f59814c0b264/download/aluno.csv",
    "https://dados.ifmt.edu.br/dataset/6b7c7c38-587a-436b-a7b2-4e3ca59d1ca8/resource/1535c8e2-f1c4-4dcf-9948-dc734522d040/download/aluno.csv",
]
# cria uma lista vazia
dfs_alunos = []

# percorre os links e adiciona na lista anterior
for url in urls_alunos:
    df = pd.read_csv(url, encoding="utf-8", sep=",")
    dfs_alunos.append(df)

# Concatenar os dataframes dos alunos em um único dataframe
df_alunos = pd.concat(dfs_alunos)
df_alunos['nome'] = df_alunos['nome'].str.upper()

# Juntar os dataframes dos servidores e dos alunos com base no nome
df_merge = pd.merge(data_servidores, df_alunos, how="inner", left_on="NOME", right_on="nome")

# apaga os nomes duplicados na lista
df_merge = df_merge.drop_duplicates(subset='NOME', keep='first')

print("\n**********************************************************************************************************************************************************************************************************")
print("\n Esses são os alunos que estudaram no IF e agora trabalham para o governo")
print("\n********************************************************************************************************************************************************************************************************\n \n")

print(df_merge)
