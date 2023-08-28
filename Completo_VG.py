from time import sleep
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.firefox.options import Options
import json
import pandas as pd


options = Options()
options.headless = True
navegador = webdriver.Firefox(options=options)

navegador.get('https://vg.abaco.com.br/transparencia/servlet/wmservidores?0')
print("navegador")

exibir = WebDriverWait(navegador, 40).until(EC.element_to_be_clickable((By.ID, 'W0044vNREGISTROSPORPAGINA')))
exibir_paginas = Select(exibir)
exibir_paginas.select_by_value('30')

print("exibir")
sleep(2)

total_paginas_loc = (By.ID, 'span_W0044vNPAGINAS')
total_paginas_e = WebDriverWait(navegador, 30).until(EC.visibility_of_element_located(total_paginas_loc))
total_paginas = total_paginas_e.text
paginas = int(total_paginas_e.text)
print(paginas)

map = {}

def ler_tabela():
    table = navegador.find_element(By.ID, 'W0044Grid1ContainerTbl')
    tbody = table.find_element(By.TAG_NAME, 'tbody')
    tr = tbody.find_elements(By.TAG_NAME,'tr')
    for current in tr:
        td = current.find_elements(By.TAG_NAME, 'td')
        matricula = td[4].get_property('innerText')
        nome = td[5].get_property('innerText')
        map[matricula] = nome
        
        

proximo = "document.querySelector('#W0044vIMGPROXIMO').click()"

ler_tabela()

count = 1
i = 0
while i <= paginas:
    i += 1
    ler_tabela()
    print("lido")
    navegador.execute_script(proximo)
    count += 1
    print("pag", count)
    sleep(3)


ler_tabela()
print(map)

file = open('Dados_Varzea_Grande_01.csv', 'w')
json.dump(map, file, ensure_ascii=False)
file.close()

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