import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import StaleElementReferenceException, ElementClickInterceptedException, TimeoutException
import csv
import pandas as pd
from tqdm import tqdm

options = webdriver.ChromeOptions()
options.add_argument('--log-level=3')
#options.add_argument('--headless')
driver = webdriver.Chrome(options=options)

url = #ESCREVA AQUI A URL DO SITE DA COPLAN
driver.get(url)

pesquisar = WebDriverWait(driver, 10).until(
    EC.element_to_be_clickable((By.XPATH, '//*[@id="BUTTON1"]'))
)
pesquisar.click()

selecionar = WebDriverWait(driver, 10).until(
    EC.visibility_of_element_located((By.XPATH, '//*[@id="vQTD_POR_PAGINA"]'))
)
select = Select(selecionar)
select.select_by_visible_text('150')

def get_total_registros():
    total_registros_element = driver.find_element(By.XPATH, '//*[@id="span_vTOTAL_REGISTROS"]')
    return int(total_registros_element.text)

total_registros = get_total_registros()
registros_por_pagina = 150
num_paginas = (total_registros + registros_por_pagina - 1) // registros_por_pagina
dados_raspados = []

def click_proximo():
    try:
        proximo = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, '//*[@id="TB_PROXIMO_ENABLED"]/a'))
        )
        proximo.click()
        return True
    except:
        print("Botão 'Próximo' desativado.")
        return False

def scrape_table():
    for i in range(1, 151):
        xpath_lupa = f'//*[@id="grid"]/tbody/tr[{i}]/td/a/i[@title="Visualizar detalhes"]'
        try:
            lupa = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, xpath_lupa))
            )
            lupa.click()
        except (StaleElementReferenceException, ElementClickInterceptedException):
            print("Lupa não encontrada. Tentando novamente...")
            time.sleep(1)
            continue 

        try:
            WebDriverWait(driver, 10).until(EC.number_of_windows_to_be(2))
        except TimeoutException:
            print("Tempo esgostado na abertura da nova janela. Pulando para o próximo.")
            continue 

        driver.switch_to.window(driver.window_handles[1])

        try:
            tabela = WebDriverWait(driver, 10).until(
                EC.visibility_of_element_located((By.XPATH, '//*[@id="TABLE3"]/tbody'))
            )
            dados_tabela = tabela.text.split('\n')
            dados_raspados.extend(dados_tabela)
        except TimeoutException:
            print("Tempo esgotado ao encontrar a tabela na nova página. Pulando para o próximo.")
        except Exception as e:
            print(f"Erro ao encontrar a tabela na nova página: {e}")

        driver.close()
        driver.switch_to.window(driver.window_handles[0])

print('Quantidade de Registros:', total_registros)       
print('Quantidade de paginas:', num_paginas)

for _ in tqdm(range(num_paginas), desc="Progresso"):
    scrape_table()
    if not click_proximo():
        break

driver.quit()

df_raspagem = pd.DataFrame([d.split() for d in dados_raspados])

urls_alunos = [
    "https://dados.ifmt.edu.br/dataset/6b7c7c38-587a-436b-a7b2-4e3ca59d1ca8/resource/fc30244a-166d-4830-a66d-a573ebe187eb/download/aluno.csv",
    "https://dados.ifmt.edu.br/dataset/6b7c7c38-587a-436b-a7b2-4e3ca59d1ca8/resource/d2a472aa-3a02-4d45-bc65-5852fa9be664/download/aluno.csv",
    "https://dados.ifmt.edu.br/dataset/6b7c7c38-587a-436b-a7b2-4e3ca59d1ca8/resource/96f114e2-58f9-4f59-9c44-f59814c0b264/download/aluno.csv",
    "https://dados.ifmt.edu.br/dataset/6b7c7c38-587a-436b-a7b2-4e3ca59d1ca8/resource/1535c8e2-f1c4-4dcf-9948-dc734522d040/download/aluno.csv",
    "https://dados.ifmt.edu.br/dataset/6b7c7c38-587a-436b-a7b2-4e3ca59d1ca8/resource/9513092b-ad4a-4e70-a806-b65618fcd102/download/aluno.csv"
]

dfs_alunos = [pd.read_csv(url) for url in urls_alunos]
df_alunos_concatenado = pd.concat(dfs_alunos).drop_duplicates()
df_raspagem.to_csv('resultado_raspagem.csv', index=False)
df_comparacao = pd.merge(df_raspagem, df_alunos_concatenado, on='NOME', how='inner')
df_comparacao.to_csv('resultado_comparacao.csv', index=False)

print("Raspagem e comparação concluídas. Arquivo salvo como 'resultado_comparacao.csv'.")
