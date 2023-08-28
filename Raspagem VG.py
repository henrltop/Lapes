from time import sleep
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.firefox.options import Options
import json


options = Options()
options.headless = True
navegador = webdriver.Firefox(options=options)

navegador = webdriver.Firefox() #(caso precise testar o programa abrindo o )


navegador.get(
    'https://vg.abaco.com.br/transparencia/servlet/wmservidores?0')
print("navegador")

exibir = WebDriverWait(navegador, 40).until(
    EC.element_to_be_clickable((By.ID, 'W0044vNREGISTROSPORPAGINA')))
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
