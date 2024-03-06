from time import sleep
# from log import CustomFormatter
import logging
class CustomFormatter(logging.Formatter):

    grey = "\x1b[38;20m"
    blue = "\x1b[34;20m"
    yellow = "\x1b[33;20m"
    red = "\x1b[31;20m"
    bold_red = "\x1b[31;1m"
    pink = "\x1b[0;35m"
    reset = "\x1b[0m"
    # format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s (%(filename)s:%(lineno)d)"
    title = pink + '%(name)-5s :: ' + reset
    format =  '%(levelname)-8s :: %(message)s'
    FORMATS = {
        logging.DEBUG: title + grey + format + reset,
        logging.INFO: title + blue + format + reset,
        logging.WARNING: title + yellow + format + reset,
        logging.ERROR: title + red + format + reset,
        logging.CRITICAL: title + bold_red + format + reset
    }

    def format(self, record):
        log_fmt = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(log_fmt)
        return formatter.format(record)


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

    def __init__(self, href: str, titulo: str, valor: str, desc: str, parcela: str, imgs: list[str], colecao: str = None) -> None:
        self.href = href
        self.titulo = titulo
        self.valor = valor
        self.desc = desc
        self.colecao = colecao
        self.parcela = parcela
        self.imgs = imgs
    
    def save_str(self) -> str:
        to_s = f"""Roupa: {self.titulo}
Link: {self.href}
Valor: {self.valor}
Resumo: {self.desc}
Parcela: {self.parcela}
Imagens: {self.imgs}

"""
        return to_s
    
    def __repr__(self) -> str:
        return f'Roupa({self.titulo}, {self.valor}, {self.colecao})'

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
                     dic['Valor'],
                     dic['Resumo'],
                     dic['Parcela'],
                     dic['Imagens'])

def front_page(limite: int, first_try=True) -> None:
    global tentativa
    if tentativa > limite_tentativas:
        logger.critical("Limite de tentativas excedido")
        return
    
    if first_try:
        logger.warning("Front page")
        # driver.get("https://www.lancaperfume.com.br/roupas/vestidos")
        # driver.get("https://www.lancaperfume.com.br/roupas/cal%C3%A7as")
        # driver.get("https://www.lancaperfume.com.br/roupas/blusas")
        # driver.get("https://www.lancaperfume.com.br/roupas/jaquetas-e-casacos")
        driver.get("https://www.lancaperfume.com.br/roupas/shorts-e-bermudas")
        # driver.get("https://www.lancaperfume.com.br/roupas/macacões")
        # driver.get("https://www.lancaperfume.com.br/roupas/camisas")
        # driver.get("https://www.lancaperfume.com.br/roupas?initialMap=productClusterIds&initialQuery=2462&map=category-2,productclusternames&query=/biquinis/roupas&searchState")
        

        logger.info("Dormindo")
        sleep(7)
        logger.warning("Carregando roupas...")

        for n in range(2, 12, 2):
            driver.execute_script(f"window.scrollTo(0, {n * 1000})")
            logger.info("Dormindo")
            sleep(4)
    
    logger.debug("Div roupas")
    div_roupas = driver.find_element(By.CLASS_NAME, "lojalancaperfume-store-theme-5-x-customGallery")
    cards_roupas = div_roupas.find_elements(By.TAG_NAME, "a")
    try:
        logger.debug(f"{len(cards_roupas)} roupas encontradas na div roupas.")
        for card in cards_roupas:
        
            if len(roupas) == limite:
                logger.info(f"{limite} Roupas encontradas, terminando . . .")
                return
            
            # logger.info("Card encontrado")
            card_href = card.get_attribute("href")
            
            card_summary = card.find_element(By.CLASS_NAME, "lojalancaperfume-store-theme-5-x-customGalleryItemDetailsSummary")
            card_title = card_summary.find_element(By.TAG_NAME, "h2").text
            card_price = card_summary.find_element(By.CLASS_NAME, "lojalancaperfume-store-theme-5-x-customGalleryItemPrice").find_element(By.TAG_NAME, "div").text

            try:
                imgs = [i.get_attribute("src") for i in card.find_element(By.CLASS_NAME, "lojalancaperfume-store-theme-5-x-customGalleryItemImage").find_elements(By.TAG_NAME, "img")]
            except NoSuchElementException:
                logger.critical("IMAGEM não encontrada.")
                continue

            # card_collection = card_summary.find_element(By.TAG_NAME, "span").text
            card_condition = card.find_element(By.CLASS_NAME, "lojalancaperfume-store-theme-5-x-customGalleryItemInstallments").text.strip("Em até").strip("sem juros").replace("\n", "")

            logger.info(f"Objeto de Roupa: {card_title} | Roupas: {len(roupas) + 1}")
            roupa = Roupa(href = card_href, titulo = card_title, valor = card_price, desc = "Vazio", parcela = card_condition, imgs = imgs)
            roupas.append(roupa)
            sleep(.5)

    except Exception as e:
        logger.error(e)
        tentativa += 1
        logger.error(f"Elemento não encontrado, dormindo e tentando novamente em 7 segundos. Tentativas: {tentativa}/{limite_tentativas}")
        sleep(7)
        front_page(limite, False)

def descricao(link) -> str:
    from random import randint
    
    logger.warning(f"Procurando descrição: {link}")
    driver.get(link)
    logger.info("Dormindo")
    sleep(randint(4, 7))

    logger.info("Recuperando descrição")
    driver.execute_script("window.scrollTo(0, 1400)")
    h2s = driver.find_elements(By.TAG_NAME, 'h2')
            
    global irmao

    for h2 in h2s:
        if h2.text.startswith("DESC"):
            descricao = h2.find_element(By.XPATH, "./following-sibling::div").find_element(By.TAG_NAME, "div").find_element(By.TAG_NAME, "div").find_element(By.TAG_NAME, "div").get_attribute("innerText")
            logger.info(f"Sucesso na descrição.\n")
            return descricao
    
    # Só chega aqui caso nenhum h2 cumpra a condição
    logger.error(f"Descrição não encontrada para link: {link}")
    return "DESCRIÇÃO NÃO ENCONTRADA"

    # for h2 in h2s:
        # if h2.text.startswith("DESC"):
            # irmao = h2 # descricao = h2.find_element(By.XPATH, "./following-sibling::div").find_element(By.TAG_NAME, "div").find_element(By.TAG_NAME, "div").find_element(By.TAG_NAME, "div").get_attribute("innerText")
        # else:
            # logger.error(f"Descrição não encontrada para link: {link}")
            # return "DESCRIÇÃO NÃO ENCONTRADA"

    # elem = irmao.find_element(By.XPATH, "./following-sibling::div")
    # descricao = elem.find_element(By.TAG_NAME, "div").find_element(By.TAG_NAME, "div").find_element(By.TAG_NAME, "div").get_attribute("innerText")
    

def main() -> None:
    front_page(50)
    logger.info(f"Foram encontradas {len(roupas)} roupas")

if __name__ == "__main__":
# if 1: 

    roupas: list[Roupa] = []
    tentativa: int = 1
    limite_tentativas = 10
    logger = logging.getLogger("main")
    logger.setLevel(logging.INFO)
    ch = logging.StreamHandler()
    ch.setFormatter(CustomFormatter())
    logger.addHandler(ch)
    
    driver = webdriver.Chrome()
    driver.set_window_size(1920, 1080)
    
    main()
    
    from datetime import datetime
    data = str(datetime.now().strftime("%d.%m - %H.%M"))
    
    # arquivo = f"CALÇAS La Moda - {data}"
    
    # arquivo = f"JAQUETAS E CASACOS La Moda - {data}"
    arquivo = f"SHORTS E BERMUDAS La Moda - {data}"
    # arquivo = f"MACACÕES La Moda - {data}"
    # arquivo = f"CAMISAS La Moda - {data}"
    # arquivo = f"BIQUINIS La Moda - {data}"

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

            if linha.startswith("Link"):
                link = linha.split(": ")[1].strip('\n')
                new_lines.append(linha)

                continue

            if linha.startswith("Resumo"):
                linha = f"Resumo: {descricao(link)}\n"
                new_lines.append(linha)

                continue
            
            else:
                new_lines.append(linha)
        
        logger.warning(f"Salvando descrições de roupas ----> {arquivo} Completo.txt")
        f.writelines(new_lines)
    driver.close()
