import os
import re
import pandas as pd
from time import sleep
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException, ElementClickInterceptedException, TimeoutException

chrome_options = Options()
chrome_options.add_argument("--disable-application-cache")
chrome_options.add_argument("--disk-cache-dir=/path/to/cache-directory")

# Inicializar o driver do Selenium
try:
    driver = webdriver.Chrome(options=chrome_options)
except Exception as e:
    print(f"Erro ao iniciar o driver: {str(e)}")
    quit()

wait = WebDriverWait(driver, 10)

try:
    driver.get('https://www.anuga.com/anuga-exhibitors/list-of-exhibitors/')
except Exception as e:
    print(f"Erro ao abrir a página: {str(e)}")
    driver.quit()
    quit()

try:
    popup = wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="onetrust-accept-btn-handler"]')))
    popup.click()
except TimeoutException:
    print("Pop-up de cookies não encontrado. Continuando...")

input("Pressione 'Enter' após verificar os filtros...")

# Inicializar variáveis
titulos_clicados = []
pagina = 0
dados_coletados = []

while True:
    try:
        div_select_options = wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'select_options')))
        # Encontre todos os itens dentro do elemento com a classe "entry"
        items = div_select_options.find_elements(By.CLASS_NAME, 'entry')

        for item in items:
            try:
                # Encontre todos os elementos que deseja clicar (dentro do loop para atualização)
                elemento_aguardando = wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, '[href^="/exhibitor/"]')))
                elementos = driver.find_elements(By.CSS_SELECTOR, '[href^="/exhibitor/"]')
            except Exception as e:
                print(f"Erro ao encontrar elementos: {str(e)}")
                continue  # Continue com o próximo item

            for elemento in elementos:
                try:
                    # Verifique se o elemento não está na lista de elementos já clicados
                    if elemento not in titulos_clicados:
                        # Clique no link para abrir em uma nova aba
                        ActionChains(driver).key_down(Keys.CONTROL).click(elemento).key_up(Keys.CONTROL).perform()

                        # Mude o foco para a nova aba
                        driver.switch_to.window(driver.window_handles[-1])

                        # Faça o que você precisa fazer na nova aba
                        if driver.current_url == "https://www.anuga.com/":
                            # Se a URL for igual à página inicial, saia do loop
                            driver.close()
                            driver.switch_to.window(driver.window_handles[0])
                            break
                        try:
                            sleep(1)
                            name_elemento = wait.until(EC.visibility_of_element_located((By.XPATH,'//div[@class="headline-title"]')))
                            html_content = driver.page_source
                            soup = BeautifulSoup(html_content, 'html.parser')
                            elementos = soup.find_all('div', class_='text-compound')
                            Country = []
                            phone = []
                            email = []
                            url = []
                            # Encontrar o elemento com a classe 'headline-title'
                            elemento = soup.find('div', class_='headline-title')

                            # Verificar se o elemento foi encontrado
                            if elemento:
                                # Extrair o texto do elemento
                                texto_elemento = elemento.text.strip()
                                print(texto_elemento)
                            else:
                                print('Elemento não encontrado.')
                            for element in elementos:
                                sleep(1)
                                element_text = element.text

                                # Use regex para extrair URLs
                                regex_url = r'(www\.[a-zA-Z0-9-]+\.[a-zA-Z]+|www\.[a-zA-Z0-9-]+\.[a-zA-Z]+\.[a-zA-Z]{2}|www\.[a-zA-Z0-9-]+\.[a-zA-Z]+\.[a-zA-Z]{3,4}|www\.[a-zA-Z0-9-]+\.[a-zA-Z]+\.[a-zA-Z]+\.[a-zA-Z]{2,4}|[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,4})'
                                urls = re.findall(regex_url, element_text)

                                regex_telefone = re.compile(r'\+\d{1,3}\s?\d{1,4}\s?\d{1,4}\s?\d{1,4}\s?\d{1,4}')
                                phone = regex_telefone.findall(element_text)

                                # O restante do seu código para processar e armazenar as informações
                                text_firstfilter = re.sub(r'[ \t]+', ' ', element_text)
                                text_secondfilter = text_firstfilter.strip().split('\n')
                                text_lines = [line.strip() for line in text_secondfilter if line.strip()]
                                email = [dado for dado in text_lines if re.match(r'\S+@\S+', dado)]
                                Country.append(text_lines[2])

                                # Adicione a lista de URLs
                                url.append(urls)

                                dados_coletados.append({
                                    'Name' : texto_elemento,
                                    'Country': Country,
                                    'Phone': phone,
                                    'Email': email,
                                    'URL': url
                                })
                                

                            # Feche a nova aba
                            driver.close()

                            # Volte o foco para a aba original
                            driver.switch_to.window(driver.window_handles[0])

                            # Adicione o elemento à lista de elementos já clicados
                            titulos_clicados.append(elemento)
                        except Exception as e:
                            print(f"Erro ao processar informações do expositor: {str(e)}")

                        driver.execute_script("window.scrollBy(0, 400);")  # Isso rolará a página 400 pixels para baixo

                except Exception as e:
                    print(f"Erro ao clicar no elemento: {str(e)}")
                
           
              
        # Salvar o DataFrame em um arquivo CSV dividido
        caminho_diretorio = r'C:\Users\User\Desktop\Projeto\Projeto Anuga'
        nome_arquivo_csv = f'dados_empresas_pagina_{pagina}.csv'
        caminho_arquivo_csv = os.path.join(caminho_diretorio, nome_arquivo_csv)

        df_empresas = pd.DataFrame(dados_coletados)
        df_empresas.to_csv(caminho_arquivo_csv, index=False, sep=";")
        sleep(2)

        # Confirmação de que o arquivo foi salvo
        print(f'O arquivo CSV da página {pagina} foi salvo em: {caminho_arquivo_csv}')
        botao_proxima_pg = wait.until(EC.element_to_be_clickable((By.XPATH, '//a[starts-with(@href, "/anuga-exhibitors/list-of-exhibitors/") and @rel="next"]')))
        botao_proxima_pg.click()  
    except NoSuchElementException:
        # Se o elemento não existe, significa que não há mais páginas
        # Então você pode executar o código para salvar os dados finais em CSV
        caminho_diretorio = r'C:\Users\User\Desktop\Projeto\Projeto Anuga'
        nome_arquivo_csv = 'dados_empresas_final.csv'
        caminho_arquivo_csv = os.path.join(caminho_diretorio, nome_arquivo_csv)

        df_empresas = pd.DataFrame(dados_coletados)
        df_empresas.to_csv(caminho_arquivo_csv, index=False, sep=";")

        # Confirmação de que o arquivo foi salvo
        print(f'O arquivo CSV final foi salvo em: {caminho_arquivo_csv}')

        # Sair do loop
        break
    except NoSuchElementException:
        sleep(5)
        driver.execute_script("window.scrollBy(0, 400);")
        botao_proxima_pg = wait.until(EC.element_to_be_clickable((By.XPATH, '//a[starts-with(@href, "/anuga-exhibitors/list-of-exhibitors/") and @rel="next"]')))
        botao_proxima_pg.click()  
        print(f"Erro desconhecido: {str(e)}")
        continue
    except Exception as e:
        print(f"Erro desconhecido: {str(e)}")
        break
driver.quit()
