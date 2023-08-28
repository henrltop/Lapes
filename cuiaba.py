import pandas as pd
#Em desenvolvimento...
# Carregar os dados dos servidores
"""""define o caminho do arquivo ativos.csv que contém os dados dos servidores a serem lidos pelo pandas. Ele utiliza uma string 
formatada para definir o caminho do arquivo com base no DIRETORIO onde ele se encontra"""
arquivo_Servidores = f"ativos.csv"


data_servidores = pd.read_csv(arquivo_Servidores,encoding='utf-8', sep=';')

# Salvar os dados dos servidores em um arquivo CSV
data_servidores.to_csv("Servidores_Cuiaba.csv")

# Carregar os dados dos alunos dos anos 2020-2023
urls_alunos = [
    "https://dados.ifmt.edu.br/dataset/6b7c7c38-587a-436b-a7b2-4e3ca59d1ca8/resource/fc30244a-166d-4830-a66d-a573ebe187eb/download/aluno.csv",
    "https://dados.ifmt.edu.br/dataset/6b7c7c38-587a-436b-a7b2-4e3ca59d1ca8/resource/d2a472aa-3a02-4d45-bc65-5852fa9be664/download/aluno.csv",
    "https://dados.ifmt.edu.br/dataset/6b7c7c38-587a-436b-a7b2-4e3ca59d1ca8/resource/96f114e2-58f9-4f59-9c44-f59814c0b264/download/aluno.csv",
    "https://dados.ifmt.edu.br/dataset/6b7c7c38-587a-436b-a7b2-4e3ca59d1ca8/resource/1535c8e2-f1c4-4dcf-9948-dc734522d040/download/aluno.csv",
]
#cria um lista vazia 
dfs_alunos = []


#percorre os links e adiociona na lista anterio
for url in urls_alunos:
    df = pd.read_csv(url, encoding="utf-8", sep=",")
    dfs_alunos.append(df)

""""Imprime os servidores quando nao estiver comentado"""
#print(data_servidores)


# Concatenar os dataframes dos alunos em um único dataframe
df_alunos = pd.concat(dfs_alunos)

# Juntar os dataframes dos servidores e dos alunos com base no nome
df_merge = pd.merge(data_servidores, df_alunos, how="inner", left_on="Nome", right_on="nome")

    #apaga os nomes duplicados na lista
""""método drop_duplicates do pandas para remover as linhas duplicadas do dataframe df_merge. O parâmetro subset='Nome' 
    indica que a coluna "Nome" será usada para identificar as duplicatas, ou seja, se houver duas ou mais linhas com o mesmo valor na coluna "Nome", apenas 
    a primeira delas será mantida no dataframe resultante. O parâmetro keep='first' indica que deve ser mantida a primeira ocorrência de cada duplicata, e as 
demais serão removidas. """
    #Em resumo, essa linha de código garante que cada servidor/aluno apareça apenas uma vez no resultado final, evitando duplicatas e inconsistências nos dados.
df_merge = df_merge.drop_duplicates(subset='Nome',keep='first')

print(df_merge)
#nomes_comuns = set(df_alunos['Nome']).intersection(data_servidores['Nome'])