import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException, ElementClickInterceptedException, StaleElementReferenceException
from time import sleep
import re
from bs4 import BeautifulSoup

#informar o caminho para salvar o arquivo
caminho_dados = None
chrome_options = Options()

# Ativar o modo headless (se desejar)
# chrome_options.add_argument("--headless")

# Ativar o uso de cache
chrome_options.add_argument("--disable-application-cache")
chrome_options.add_argument("--disk-cache-dir=/path/to/cache-directory")

# Inicializar o driver do Selenium
driver = webdriver.Chrome(options=chrome_options)
driver.get('https://cadastur.turismo.gov.br/hotsite/#!/public/capa/entrar')
sleep(1)
# Filtrando dados informados

# Esperar até que a tecla "Enter" seja pressionada manualmente
input("Pressione 'Enter' após verificar os filtros...")
sleep(1)
# Lista para armazenar os dados

# Definições
pagina = 1
dados_coletados = []
cadastros = 0
contador = 0
#numero_pg = 0
wait = WebDriverWait(driver, 10)
while True:
    print(f'pagina : {pagina}')

  
    try:
        # Aguarde até que o elemento desapareça
        wait.until(EC.invisibility_of_element_located((By.XPATH, '//*[@id="loader"]')))
    except TimeoutException:
        continue
    
    # Esperar até que o botão "Visualizar" esteja visível antes de clicar
    
    botao_lupa = wait.until(EC.presence_of_all_elements_located((By.XPATH, '//button[@ng-click="vm.detalharPrestador(item.id, item.tipoPessoa)"]')))
    wait.until(EC.presence_of_all_elements_located((By.XPATH, '//button[@ng-click="vm.detalharPrestador(item.id, item.tipoPessoa)"]')))
    for botao in botao_lupa:
        sleep(1)
        wait.until(EC.presence_of_all_elements_located((By.XPATH, '//button[@ng-click="vm.detalharPrestador(item.id, item.tipoPessoa)"]')))
        botao_lupa = wait.until(EC.presence_of_all_elements_located((By.XPATH, '//button[@ng-click="vm.detalharPrestador(item.id, item.tipoPessoa)"]')))
        try:
            botao.click()
            
        except TimeoutException:
            # Se não for possível clicar, role a página para encontrar o botão e clique nele
            driver.execute_script("arguments[0].scrollIntoView();", botao)
            botao.click()
            
            continue
        except:
            continue
        
        sleep(0.5)
        wait.until(EC.presence_of_element_located((By.XPATH, '//p[@class="ng-binding"]')))
        try:
            elementos = driver.find_elements(By.XPATH, '//p[@class="ng-binding"]')
            textos_elementos = [elemento.text for elemento in elementos if elemento.text.strip()]
            html_content = '\n'.join(textos_elementos)
        except StaleElementReferenceException:

            print('erro StaleElementReferenceException elementos')
            break
        
        # Coleta de dados
                
        soup = BeautifulSoup(html_content, 'html.parser')
        dados_brutos = html_content.split('\n')
        lista_dados = [dado for dado in dados_brutos if dado.strip()]
        try:
            url_pattern = r'(www\.[a-zA-Z0-9-]+\.[a-zA-Z]+|www\.[a-zA-Z0-9-]+\.[a-zA-Z]+\.[a-zA-Z]{2}|www\.[a-zA-Z0-9-]+\.[a-zA-Z]+\.[a-zA-Z]{3,4}|www\.[a-zA-Z0-9-]+\.[a-zA-Z]+\.[a-zA-Z]+\.[a-zA-Z]{2,4}|[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,4})'
            nome_completo = [lista_dados[0]]
            nome_de_tratamento = [lista_dados[1]]
            numero_cadastro = [dado for dado in lista_dados if re.match(r'\d{2}\.\d{6}.\d{2}-\d', dado)]
            website = [dado for dado in lista_dados if re.search(url_pattern, dado)]
            email = [dado for dado in lista_dados if re.match(r'\S+@\S+', dado)]
            validade_atividade = [dado for dado in lista_dados if re.match(r'\d{2}/\d{2}/\d{4} - \d{2}/\d{2}/\d{4}', dado)]
        except:
            print('erro bloco url-patern')
            break
        try:
            idiomas = driver.find_elements(By.XPATH, '//span[@class="idioma ng-binding ng-scope"]')
            idiomas_text = [idioma.text for idioma in idiomas]
        except :
            print('erro idiomas text')
            idiomas_text = []
            break

        try:
            municipio_atuacao = driver.find_elements(By.XPATH, '//span[@ng-if="municipio.noLocalidade && municipio.uf.sgUf"]')
            municipio_atuacao_text = [municipio.text for municipio in municipio_atuacao]
        except :
            print('erro municipio')
            municipio_atuacao_text = []
            break

        try:
            categoria = driver.find_elements(By.XPATH, '//span[@class="categoria-guia ng-binding ng-scope"]')
            categoria_text = [cat.text for cat in categoria]
        except :
            print('erro categoria')
            categoria_text = []
            break

        try:
            telefone = driver.find_elements(By.XPATH, '//p[@ng-if="vm.dadosPrestador.nuTelefone.length >= 8"]')
            telefone_text = [tel.text for tel in telefone]
        except TimeoutException:
            print('erro time , telefone')
            telefone_text = ['Nao informado']

        dados_coletados.append({
            'Nome Completo': nome_completo,
            'Nome de Tratamento': nome_de_tratamento,
            'Número de Cadastro': numero_cadastro,
            'Idiomas': idiomas_text,
            'Municípios de Atuação': municipio_atuacao_text,
            'Categorias': categoria_text,
            'E-mail': email,
            'Website': website,
            'Telefones': telefone_text,
            'Validades atividade': validade_atividade
        })
        cadastros += 1
        contador += 1
        
        sleep(0.5)
        if contador % 10 == 0:
            caminho_csv = rf'C:\Users\User\Desktop\Dados_coletados\dados_sp\dados_até_pag_{pagina}.csv'
            df = pd.DataFrame(dados_coletados)
            df.to_csv(caminho_csv, sep=';', index=False)
            print(f'{cadastros} cadastros efetuados')
        
        # Bloco para utilizar quando se tem um numero especifico de paginas para extrair.
        #if  contador == numero_pg :
        #   caminho_csv = rf'C:\Users\User\Desktop\Dados_coletados\dados_sp\Dados_SP.csv'
        #    df = pd.DataFrame(dados_coletados)
        #    df.to_csv(caminho_csv, sep=';', index=False)
        #    print(cadastros)
        #    driver.quit()"""

        # Fechando a pesquisa e seguindo para troca de pagina.                
        try:
            
            botao_fechar = wait.until(EC.element_to_be_clickable((By.XPATH, '//span[@class="close-pesqusia"]')))
            botao_fechar.click()

            
        except ElementClickInterceptedException:
            sleep(5)
            botao_fechar = wait.until(EC.element_to_be_clickable((By.XPATH, '//span[@class="close-pesqusia"]')))
            botao_fechar.click()
            print('Erro botao fechar')
            continue
        except TimeoutException:
            break
        except:
            break
        
        
    try:
        
        botao_lupa = wait.until(EC.visibility_of_element_located((By.XPATH, '//button[@ng-click="vm.detalharPrestador(item.id, item.tipoPessoa)"]')))
        pagina_habilitada = driver.find_element(By.XPATH, '//li[@class="pagination-next ng-scope"]')
        botao_proxima_pg = wait.until(EC.element_to_be_clickable((By.XPATH, '//a[@ng-click="selectPage(page + 1, $event)"]')))
        botao_proxima_pg.click()
                
    except NoSuchElementException:

        print(f"Concluido")
        break
    except ElementClickInterceptedException:
        sleep(3)
        print('Erro botao proxima pag')
        
        continue
    except TimeoutException:
        break
    except:
        break
    pagina += 1    

    
 #Salvar dados totais   
caminho_csv = caminho_dados
df = pd.DataFrame(dados_coletados)
df.to_csv(caminho_csv, sep=';', index=False)
print(cadastros)
driver.quit()
