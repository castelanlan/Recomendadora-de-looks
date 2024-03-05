from time import sleep
from log import CustomFormatter

import logging
import requests

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.remote.webelement import WebElement
from selenium.common.exceptions import StaleElementReferenceException, NoSuchElementException

class Roupa:

    @staticmethod
    def download_image(url, o) -> None:
        open(o, 'wb').write(requests.get(url))

    def __init__(self, href: str, titulo: str, preco: str, desc: str, condicao: str, imgs: list[str], colecao: str = None) -> None:
        self.href = href
        self.titulo = titulo
        self.preco = preco
        self.desc = desc
        self.colecao = colecao
        self.condicao = condicao
        self.imgs = imgs
    
    def save_str(self) -> str:
        to_s = f"""Roupa: {self.titulo}
Link: {self.href}
Preço: {self.preco}
Descrição: {self.desc}
Condição: {self.condicao}
Imagens: {self.imgs}

"""
        return to_s
    
    def __repr__(self) -> str:
        return f'Roupa({self.titulo}, {self.preco}, {self.colecao})'

    @staticmethod
    def from_doc(doc: str) -> dict:
        res = {}
        lines = doc.splitlines()
        for line in lines:
            key, value = line.split(': ', 1)
            res[key] = value
        
        return res
    
    @staticmethod
    def from_dict(dic):
        return Roupa(dic['Link'],
                     dic['Roupa'],
                     dic['Preço'],
                     dic['Descrição'],
                     dic['Condição'],
                     dic['Imagens'])

def front_page(limite: int) -> None:
    global tentativa
    if tentativa > limite_tentativas:
        logger.critical("Limite de tentativas excedido")
        return 0
    logger.warning("Front page")
    # driver.get("https://www.lancaperfume.com.br/roupas?initialMap=productClusterIds&initialQuery=2462&map=,&query=/roupas/sandalias&searchState")
    # driver.get("https://www.lancaperfume.com.br/roupas?initialMap=productClusterIds&initialQuery=2462&map=category-2,productclusternames&query=/saias/roupas&searchState")
    driver.get("https://www.lancaperfume.com.br/roupas?initialMap=productClusterIds&initialQuery=2462&map=category-2,productclusternames&query=/t-shirts/roupas&searchState")
    logger.info("Dormindo")
    sleep(7)
    logger.warning("Carregando roupas...")
    for n in range(2, 12, 2):
        driver.execute_script(f"window.scrollTo(0, {n * 1000})")
        logger.info("Dormindo")
        sleep(4)
    div_roupas = driver.find_element(By.CLASS_NAME, "lojalancaperfume-store-theme-5-x-customGallery")

    try:
        for card in div_roupas.find_elements(By.TAG_NAME, "a"):
            
            if len(roupas) == limite:
                logger.info(f"{limite} Roupas encontradas, terminando . . .")
                return
            
            # logger.info("Card encontrado")
            try:
                imgs = [i.get_attribute("src") for i in card.find_element(By.CLASS_NAME, "lojalancaperfume-store-theme-5-x-customGalleryItemImage").find_elements(By.TAG_NAME, "img")]
            except NoSuchElementException:
                continue

            card_href = card.get_attribute("href")
            card_summary = card.find_element(By.CLASS_NAME, "lojalancaperfume-store-theme-5-x-customGalleryItemDetailsSummary")
            card_title = card_summary.find_element(By.TAG_NAME, "h2").text
            card_price = card_summary.find_element(By.CLASS_NAME, "lojalancaperfume-store-theme-5-x-customGalleryItemPrice").find_element(By.TAG_NAME, "div").text
            # card_collection = card_summary.find_element(By.TAG_NAME, "span").text
            card_condition = card.find_element(By.CLASS_NAME, "lojalancaperfume-store-theme-5-x-customGalleryItemInstallments").text.strip("Em at├®").strip("sem juros").replace("\n", "")

            logger.info(f"Objeto de Roupa: {card_title}")
            roupa = Roupa(href = card_href, titulo = card_title, preco = card_price, desc = "Vazio", condicao = card_condition, imgs = imgs)
            roupas.append(roupa)
            sleep(.5)
            # print(roupas)

    # except NoSuchElementException:
        # pass

    except Exception as e:
        logger.error(e)
        tentativa += 1
        logger.error(f"Elemento n├úo encontrado, dormindo e tentando novamente em 10 segundos. Tentativas: {tentativa}/{limite_tentativas}")
        sleep(5)
        front_page(limite)

def descricao(link) -> str:
    from random import randint
    dc = str(link).strip('\n')
    logger.warning(f"Procurando descri├º├úo: {dc}")
    driver.get(link)
    logger.info("Dormindo")
    sleep(randint(4, 7))

    logger.info("Recuperando descrição")
    driver.execute_script("window.scrollTo(0, 1400)")
    h2s = driver.find_elements(By.TAG_NAME, 'h2')
            
    global irmao
    for h2 in h2s:
        if h2.text.startswith("DESC"):
            irmao = h2 # descricao = h2.find_element(By.XPATH, "./following-sibling::div").find_element(By.TAG_NAME, "div").find_element(By.TAG_NAME, "div").find_element(By.TAG_NAME, "div").get_attribute("innerText")
        else:
            return "DESCRIÇÃO NÃO ENCONTRADA"

    elem = irmao.find_element(By.XPATH, "./following-sibling::div")
    descricao = elem.find_element(By.TAG_NAME, "div").find_element(By.TAG_NAME, "div").find_element(By.TAG_NAME, "div").get_attribute("innerText")
    
    logger.info(f"Sucesso na descrição.\n")
    return descricao

def main() -> None:
    front_page(50)
    logger.info(f"Foram encontradas {len(roupas)} roupas")

if __name__ == "__main__": 

    roupas: list[Roupa] = []
    tentativa: int = 1
    limite_tentativas = 1000
    logger = logging.Logger("scraper")
    logger.setLevel(logging.INFO)
    ch = logging.StreamHandler()
    ch.setFormatter(CustomFormatter())
    logger.addHandler(ch)
    
    driver = webdriver.Chrome()
    driver.set_window_size(1920, 1080)
    
    main()
    
    from datetime import datetime
    data = str(datetime.now().strftime("%d.%m - %H.%M"))
    arquivo = f"SANDALIA La Moda - {data}"
    arquivo = f"SAIAS La Moda - {data}"
    arquivo = f"T-SHIRTS La Moda - {data}"    

    with open(f"./App/RAG/sem-desc/{arquivo}.txt", "w", encoding="utf-8") as f:
        write = ""
        for roupa in roupas:
            write += roupa.save_str()
        
        logger.warning(f"Salvando informações básicas de roupas ----> {arquivo}.txt")
        f.write(write)
    
    logger.info("2ª parte do script - Descricões das roupas")

    with open(f"./App/RAG/sem-desc/{arquivo}.txt", "r", encoding="utf-8") as f:
        linhas = f.readlines()

    with open(f"./App/RAG/docs/{arquivo} Completo.txt", "x", encoding = "utf-8") as f:
        new_lines = []
        for linha in linhas:

            if linha.startswith("Link:"):
                link = linha.split(" ")[1]
                new_lines.append(linha)

                continue

            if linha.startswith("Desc"):
                linha = f"Descri├º├úo: {descricao(link)}\n"
                new_lines.append(linha)

                continue
            
            else:
                new_lines.append(linha)
        
        logger.warning(f"Salvando descri├º├Áes de roupas ----> {arquivo} Completo.txt")
        f.writelines(new_lines)
