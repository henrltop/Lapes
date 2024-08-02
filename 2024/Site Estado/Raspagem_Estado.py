import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, StaleElementReferenceException
from concurrent.futures import ThreadPoolExecutor, as_completed

num_threads = 8  # Número de threads

# Função para raspar dados de uma única página
def raspagem_pagina(pagina):
    """
    Raspagem de dados de uma única página.

    Args:
        pagina (int): Número da página a ser raspada.
    
    Returns:
        list: Dados raspados da página, ou None em caso de erro.
    """
    url = f'https://consultas.transparencia.mt.gov.br/pessoal/servidores_ativos/resultado_1.php?pg={pagina}&mes=1&ano=2024'
    options = webdriver.ChromeOptions()
    options.add_argument('--log-level=3')  # Minimiza os logs do navegador
    options.add_argument('--headless')     # Executa o navegador em modo headless (sem interface gráfica)
    driver = webdriver.Chrome(options=options)
    driver.get(url)
    
    dados = []  # Lista para armazenar os dados raspados
    try:
        # Espera até que a tabela esteja presente na página
        tabela = WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.TAG_NAME, 'table')))
        linhas = tabela.find_elements(By.TAG_NAME, 'tr')
        
        # Itera sobre as linhas para extrair os dados
        for linha in linhas:
            celulas = linha.find_elements(By.TAG_NAME, 'td')
            dados_linha = [celula.text for celula in celulas]  # Coleta o texto de cada célula
            dados.append(dados_linha)  # Adiciona a linha de dados à lista de dados
    except StaleElementReferenceException:
        # Tente novamente encontrar a tabela se ocorrer um StaleElementReferenceException
        try:
            tabela = WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.TAG_NAME, 'table')))
            linhas = tabela.find_elements(By.TAG_NAME, 'tr')
            for linha in linhas:
                celulas = linha.find_elements(By.TAG_NAME, 'td')
                dados_linha = [celula.text for celula in celulas]
                dados.append(dados_linha)
        except Exception as e:
            print(f"Erro ao raspar a página {pagina}: {e}")
            return None  # Retorna None em caso de erro
    except Exception as e:
        print(f"Erro ao raspar a página {pagina}: {e}")
        return None  # Retorna None em caso de erro
    finally:
        driver.quit()  # Fecha o driver do Chrome
    return dados

# Inicialize o driver para obter o número total de páginas
options = webdriver.ChromeOptions()
options.add_argument('--log-level=3')  # Minimiza os logs do navegador
options.add_argument('--headless')     # Executa o navegador em modo headless (sem interface gráfica)
driver = webdriver.Chrome(options=options)
url = 'https://consultas.transparencia.mt.gov.br/pessoal/servidores_ativos/resultado_1.php?pg=1&mes=1&ano=2024'
driver.get(url)
try:
    # Encontra o elemento que contém o número total de páginas
    total_paginas_element = driver.find_element(By.XPATH, '/html/body/div[1]/div[5]/div/nav/ul/li[8]/a')
    total_paginas = int(total_paginas_element.text)  # Converte o texto do elemento para um inteiro
except Exception as e:
    print(f"Erro ao obter o número total de páginas: {e}")
    total_paginas = 1  # Define um valor padrão de 1 página em caso de erro
finally:
    driver.quit()  # Fecha o driver do Chrome

# Lista para armazenar todos os dados raspados
dados_totais = []
failed_pages = []  # Lista para armazenar páginas que falharam

# Função para processar as páginas em paralelo
def process_pages(pages):
    """
    Processa as páginas em paralelo usando threads.
    
    Args:
        pages (list): Lista de números de páginas a serem processadas.
    """
    global failed_pages
    with ThreadPoolExecutor(max_workers=num_threads) as executor:
        futuras = {executor.submit(raspagem_pagina, pagina): pagina for pagina in pages}
        for future in as_completed(futuras):
            pagina = futuras[future]
            try:
                dados = future.result()
                if dados is None:
                    failed_pages.append(pagina)  # Adiciona à lista de falhas se os dados forem None
                else:
                    dados_totais.extend(dados)  # Adiciona os dados raspados à lista total
                    print(f"Página {pagina} raspada com sucesso.")
            except Exception as e:
                print(f"Erro ao processar a página {pagina}: {e}")
                failed_pages.append(pagina)  # Adiciona à lista de falhas em caso de exceção

# Primeira raspagem
pages_to_process = list(range(1, total_paginas + 1))  # Cria uma lista de páginas para processar
process_pages(pages_to_process)

# Tentar novamente as páginas que falharam
while failed_pages:
    print(f"Tentando novamente as páginas que falharam: {failed_pages}")
    paginas_falhas = failed_pages
    failed_pages = []
    process_pages(paginas_falhas)

# Criar DataFrame a partir dos dados raspados e adicionar cabeçalho
df_raspagem = pd.DataFrame(dados_totais, columns=["Matricula", "Ficha", "NOME", "Data de Exercício", "Data da Vacância", "Folha", "Órgão", "Vantagens", "Deduções", "Pós Deduções"])

# Verificar e transformar a coluna 'NOME' para maiúsculas
if 'NOME' in df_raspagem.columns:
    df_raspagem['NOME'] = df_raspagem['NOME'].str.upper()
else:
    print("Erro: A coluna 'NOME' não está presente em df_raspagem.")

# URLs dos dados de alunos
urls_alunos = [
    "https://dados.ifmt.edu.br/dataset/6b7c7c38-587a-436b-a7b2-4e3ca59d1ca8/resource/fc30244a-166d-4830-a66d-a573ebe187eb/download/aluno.csv",
    "https://dados.ifmt.edu.br/dataset/6b7c7c38-587a-436b-a7b2-4e3ca59d1ca8/resource/d2a472aa-3a02-4d45-bc65-5852fa9be664/download/aluno.csv",
    "https://dados.ifmt.edu.br/dataset/6b7c7c38-587a-436b-a7b2-4e3ca59d1ca8/resource/96f114e2-58f9-4f59-9c44-f59814c0b264/download/aluno.csv",
    "https://dados.ifmt.edu.br/dataset/6b7c7c38-587a-436b-a7b2-4e3ca59d1ca8/resource/1535c8e2-f1c4-4dcf-9948-dc734522d040/download/aluno.csv",
    "https://dados.ifmt.edu.br/dataset/6b7c7c38-587a-436b-a7b2-4e3ca59d1ca8/resource/9513092b-ad4a-4e70-a806-b65618fcd102/download/aluno.csv"
]

# Carregar os dados de alunos das URLs
dfs_alunos = [pd.read_csv(url) for url in urls_alunos]
df_alunos_concatenado = pd.concat(dfs_alunos).drop_duplicates()

# Renomear coluna 'nome' para 'Servidor' em df_alunos_concatenado
if 'nome' in df_alunos_concatenado.columns:
    df_alunos_concatenado.rename(columns={'nome': 'Servidor'}, inplace=True)

# Verificar e transformar a coluna 'Servidor' para maiúsculas em df_alunos_concatenado
if 'Servidor' in df_alunos_concatenado.columns:
    df_alunos_concatenado['Servidor'] = df_alunos_concatenado['Servidor'].str.upper()
else:
    print("Erro: A coluna 'Servidor' não está presente em df_alunos_concatenado.")

# Comparar os dados e salvar o resultado da comparação
if 'NOME' in df_raspagem.columns and 'Servidor' in df_alunos_concatenado.columns:
    df_comparacao = pd.merge(df_raspagem, df_alunos_concatenado, left_on='NOME', right_on='Servidor', how='inner')
    
    # Ordenar pelo valor de 'Vantagens' e remover duplicatas mantendo o maior valor de 'Vantagens'
    df_comparacao.sort_values(by='Vantagens', ascending=False, inplace=True)
    df_comparacao.drop_duplicates(subset='NOME', keep='first', inplace=True)

    # Salvar o resultado final da comparação
    df_comparacao.to_csv('resultado_comparacao.csv', index=False)
    print(f"Junção realizada com sucesso. {df_comparacao.shape[0]} alunos encontrados. Arquivo salvo como 'resultado_comparacao.csv'.")
else:
    print("Erro: A coluna 'NOME' ou 'Servidor' não está presente em ambos os DataFrames.")
