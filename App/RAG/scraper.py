from time import sleep
# from log import CustomFormatter
import logging

from App import Roupa, CustomFormatter

import logging

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException

def front_page(limite: int, first_try=True) -> None:
    global tentativa
    if tentativa > limite_tentativas:
        logger.critical("Limite de tentativas excedido")
        return
    
    if first_try:
        logger.warning("Front page")
        # driver.get("https://www.lancaperfume.com.br/roupas/cal%C3%A7as")
        driver.get("https://www.lancaperfume.com.br/roupas?initialMap=productClusterIds&initialQuery=2462&map=category-2,productclusternames&query=/biquinis/roupas&searchState")
        

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
            try:
                card_condition = card.find_element(By.CLASS_NAME, "lojalancaperfume-store-theme-5-x-customGalleryItemInstallments").text.strip("Em até").strip("sem juros").replace("\n", "")
            except NoSuchElementException:
                card_condition = "Sem parcelamento :("

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

def main() -> None:
    front_page(50)
    logger.info(f"Foram encontradas {len(roupas)} roupas")

if __name__ == "__main__":
# if 1: 

    roupas: list[Roupa] = []
    tentativa: int = 1
    limite_tentativas = 10
    logger = logging.Logger("Scraper")
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
    arquivo = f"BIQUINIS La Moda - {data}"

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
