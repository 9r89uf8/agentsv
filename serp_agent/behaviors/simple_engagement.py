"""
Simple engagement behaviors for SEO enhancement
"""
import time
import random
from selenium.webdriver.common.by import By
from ..logging.logger import log


def engage_with_page(driver, min_time=120, max_time=180):
    """
    Simple engagement: stay on page 2-3 minutes with basic behaviors
    
    Args:
        driver: WebDriver instance
        min_time: Minimum time in seconds (default 120 = 2 minutes)
        max_time: Maximum time in seconds (default 180 = 3 minutes)
    """
    total_time = random.randint(min_time, max_time)
    start_time = time.time()
    
    log(f"Iniciando interacción con la página por {total_time} segundos")
    
    # Get page height for scrolling
    page_height = driver.execute_script("return document.body.scrollHeight")
    viewport_height = driver.execute_script("return window.innerHeight")
    
    # Calculate scroll steps
    scroll_steps = max(3, int(page_height / viewport_height))
    time_per_step = total_time / (scroll_steps + 2)  # +2 for initial pause and final actions
    
    # Initial pause (user reading top of page)
    time.sleep(random.uniform(5, 15))
    
    # Scroll through page gradually
    for step in range(scroll_steps):
        scroll_amount = int(page_height / scroll_steps)
        driver.execute_script(f"window.scrollTo(0, {scroll_amount * step});")
        
        # Pause as if reading this section
        pause_time = time_per_step * random.uniform(0.7, 1.3)
        
        # Sometimes pause longer (found something interesting)
        if random.random() < 0.2:  # 20% chance
            pause_time *= random.uniform(1.5, 2.5)
            log("Pausa extendida - contenido interesante")
        
        time.sleep(pause_time)
    
    # Try to click 1-2 internal links
    _click_internal_links(driver)
    
    # Scroll back up sometimes
    if random.random() < 0.3:  # 30% chance
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight * 0.3);")
        time.sleep(random.uniform(3, 8))
    
    # Fill remaining time if needed
    remaining_time = total_time - (time.time() - start_time)
    if remaining_time > 0:
        time.sleep(remaining_time)
    
    log(f"Interacción con la página completada después de {time.time() - start_time:.1f} segundos")


def _click_internal_links(driver):
    """Click 1-2 internal links if available (Spanish optimized for noviachat)"""
    try:
        # Find internal links (basic approach)
        current_domain = driver.current_url.split('/')[2]
        internal_links = driver.find_elements(By.XPATH, f"//a[contains(@href, '{current_domain}') or starts-with(@href, '/')]")
        
        # Filter out navigation links - Spanish keywords
        content_links = []
        for link in internal_links:
            link_text = link.text.lower()
            # Spanish link keywords for AI girlfriend chat site
            spanish_keywords = [
                'leer más', 'ver más', 'artículo', 'guía', 'conocer', 
                'descubrir', 'chicas', 'chat', 'empezar', 'comenzar',
                'hablar', 'conoce', 'nueva', 'más información', 'detalles',
                'perfil', 'galería', 'fotos', 'chatear', 'mensaje'
            ]
            if len(link_text) > 5 and any(word in link_text for word in spanish_keywords):
                content_links.append(link)
        
        if content_links:
            # Click 1-2 links
            num_clicks = random.choice([1, 2]) if len(content_links) > 1 else 1
            
            for _ in range(min(num_clicks, len(content_links))):
                link = random.choice(content_links)
                content_links.remove(link)
                
                try:
                    if link.is_displayed() and link.is_enabled():
                        log(f"Haciendo clic en enlace interno: {link.text[:30]}")
                        link.click()
                        
                        # Stay on new page briefly
                        time.sleep(random.uniform(10, 30))
                        
                        # Go back
                        driver.back()
                        time.sleep(random.uniform(2, 5))
                        
                except Exception as e:
                    log(f"Error al hacer clic en enlace interno: {e}")
                    continue
    
    except Exception as e:
        log(f"Fallo al hacer clic en enlaces internos: {e}")


def add_human_delays():
    """Add small random delays to seem human"""
    time.sleep(random.uniform(0.5, 2.0))