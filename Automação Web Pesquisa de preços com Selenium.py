#!/usr/bin/env python
# coding: utf-8

# In[ ]:


# 0.importar bibliotecas
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
import pandas as pd
import time
import win32com.client as win32

# 1.criar o navegador
nav = webdriver.Chrome()
# 2. importar/visualizar a base de dados
tabela_produtos = pd.read_excel("buscas.xlsx")

def busca_google_shopping(nav, produto, termos_banidos, preco_minimo, preco_maximo):
    # entrar no google
    nav.get('https://www.google.com/')
    
    #tratar os valores que vieram da tabela
    produto = produto.lower()
    termos_banidos = termos_banidos.lower()
    lista_termos_banidos = termos_banidos.split(' ')
    lista_termos_produto = produto.split(' ')

    #pesquisar o nome do produto no Google
    nav.find_element(By.XPATH, '/html/body/div[1]/div[3]/form/div[1]/div[1]/div[1]/div/div[2]/input').send_keys(produto)
    nav.find_element(By.XPATH, '/html/body/div[1]/div[3]/form/div[1]/div[1]/div[1]/div/div[2]/input').send_keys(Keys.ENTER)

        # clicar na aba shopping
    elementos = nav.find_elements(By.CLASS_NAME, 'hdtb-mitem')
    for item in elementos:
        if "Shopping" in item.text:
            item.click()
            break
        # pegar o preco do produto no shopping
    lista_resultados = nav.find_elements(By.CLASS_NAME, 'sh-dgr__grid-result')
    lista_ofertas = []
    for resultado in lista_resultados:
        preco = resultado.find_element(By.CLASS_NAME, 'a8Pemb').text
        nome = resultado.find_element(By.CLASS_NAME, 'Xjkr3b').text
        nome = nome.lower()
        link = resultado.find_element(By.TAG_NAME, 'a').get_attribute('href')

        #verificação do nome
        tem_termos_banidos = False
        for palavra in lista_termos_banidos:
            if palavra in nome:
                tem_termos_banidos = True

        tem_todos_termos_produto = True
        for palavra in lista_termos_produto:
            if palavra not in nome:
                tem_todos_termos_produto = False
        #tratando o preço
        if not tem_termos_banidos and tem_todos_termos_produto:
            try:        
                preco = resultado.find_element(By.CLASS_NAME, 'a8Pemb').text
                preco = preco.replace('R$', '').replace(' ','').replace('.', '').replace(',', '.')
                preco = float(preco)
    # verificando se o preco está dentro do mínimo e máximo
                preco_maximo = float(preco_maximo)
                preco_minimo = float(preco_minimo)
                if preco_minimo <= preco <= preco_maximo:   
                    lista_ofertas.append((nome, preco, link))
            except:
                continue
    return lista_ofertas 

def busca_buscape(nav, produto, termos_banidos, preco_minimo, preco_maximo):
    # tratar os valores da função
    preco_maximo = float(preco_maximo)
    preco_minimo = float(preco_minimo)
    produto = produto.lower()
    termos_banidos = termos_banidos.lower()
    lista_termos_banidos = termos_banidos.split(" ")
    lista_termos_produto = produto.split(" ")
    
    # entrar no buscape
    nav.get("https://www.buscape.com.br/")
    # pesquisar pelo produto no buscape
    nav.find_element(By.XPATH, '//*[@id="new-header"]/div[1]/div/div/div[3]/div/div/div[1]/input').send_keys(produto, Keys.ENTER)
    # pegar a lista de resultados da busca do buscape
    time.sleep(4)
    lista_resultados = nav.find_elements(By.CLASS_NAME, 'Cell_Content__fT5st')
    # para cada resultado
    lista_ofertas = []
    for resultado in lista_resultados:
        try:
            preco = resultado.find_element(By.TAG_NAME, 'strong').text
            nome = resultado.get_attribute('title')
            nome = nome.lower()
            link = resultado.get_attribute('href')
        # verificacao do nome - se no nome tem algum termo banido
            tem_termos_banidos = False
            for palavra in lista_termos_banidos:
                if palavra in nome:
                    tem_termos_banidos = True  
                    
        # verificar se no nome tem todos os termos do nome do produto
            tem_todos_termos_produto = True
            for palavra in lista_termos_produto:
                if palavra not in nome:
                    tem_todos_termos_produto = False
                
            if not tem_termos_banidos and tem_todos_termos_produto:
                preco = preco.replace("R$", "").replace(" ", "").replace(".", "").replace(",", ".")
                preco = float(preco)
                if preco_minimo <= preco <= preco_maximo:
                    lista_ofertas.append((nome, preco, link))
        except:
            pass
    return lista_ofertas


# Para fins de testes, inicialmente vc pode por um break no final do for, para que ele não percorra as linhas todas da tabela.
tabela_ofertas = pd.DataFrame()

for linha in tabela_produtos.index:
    produto = tabela_produtos.loc[linha, 'Nome']
    termos_banidos = tabela_produtos.loc[linha, 'Termos banidos']
    preco_minimo = tabela_produtos.loc[linha,'Preço mínimo']
    preco_maximo = tabela_produtos.loc[linha,'Preço máximo']
    
    lista_ofertas_google = busca_google_shopping(nav, produto, termos_banidos, preco_minimo, preco_maximo)
    if lista_ofertas_google:
        tabela_google_shopping = pd.DataFrame(lista_ofertas_google, columns=['produto','preco', 'link'])
        tabela_ofertas = tabela_ofertas.append(tabela_google_shopping)
    else:
        tabela_google_shopping = None
        
    lista_ofertas_buscape = busca_buscape(nav, produto, termos_banidos, preco_minimo, preco_maximo)
    if lista_ofertas_buscape:
        tabela_buscape = pd.DataFrame(lista_ofertas_buscape, columns=['produto', 'preco', 'link'])
        tabela_ofertas = tabela_ofertas.append(tabela_buscape)
    else:
        tabela_buscape = None
    display(tabela_google_shopping)
    display(tabela_buscape)
    
# Exportando a base para Excel  

# A primiera linha, retira o íncice errado que vem na exportaçõa dos dados das duas tabelas das pesquisa
# e ordena um novo índice. 
# A segunda linha exporta para o excel sem o índice.
# 1. Ao passar p o Excel, foi com um índice criado, o comando reset_index(drop= True), solucionou isso.
# tabela_ofertas = tabela_ofertas.drop(['Unnamed: 0'], axis=1)

tabela_ofertas = tabela_ofertas.reset_index(drop= True)
tabela_ofertas.to_excel('Ofertas.xlsx', index=False)

# Enviando email

# O f na linha mail.HTMLBody, é pq qro por a variável tabela_ofertas em texto.
# O to_html é para a tabela ir no corpo do email de maneira formatada.
# O index=False é para ir sem índice.
# verificando se existe alguma oferta dentro da tabela de ofertas


if len(tabela_ofertas.index) > 0:
   
    outlook = win32.Dispatch('outlook.application')
    mail = outlook.CreateItem(0)
    mail.To = 'devfullstack26@gmail.com'
    mail.Subject = 'Produto(s) Encontrado(s) na faixa de preço desejada'
    mail.HTMLBody = f"""
    <p>Prezados,</p>
    <p>Encontramos alguns produtos em oferta dentro da faixa de preço desejada. Segue tabela com detalhes</p>
    {tabela_ofertas.to_html(index=False)}
    <p>Qualquer dúvida estou à disposição</p>
    <p>Att.,</p>
    """
    
    mail.Send()

nav.quit()  

