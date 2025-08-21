"""
Simple SEO-enhanced main function for SERP Agent
"""
from serp_agent.runner.seo_enhanced_task import run_seo_task
from serp_agent.config.settings import Settings
import os
from dotenv import load_dotenv


def main():
    """Simple SEO-enhanced main function"""
    # Load environment variables
    load_dotenv()
    
    # Load settings from environment
    settings = Settings.from_env()
    
    # Get SEO parameters from environment or use defaults
    brand_name = os.getenv("BRAND_NAME", "Your Brand Name")
    target_domain = os.getenv("TARGET_DOMAIN", "yoursite.com")
    base_topic = os.getenv("BASE_TOPIC", "your main product/service")
    num_searches = int(os.getenv("SEARCHES_PER_SESSION", "20"))
    
    print(f"\n🚀 Iniciando búsquedas SEO en español para {brand_name}")
    print(f"   Marca: {brand_name}")
    print(f"   Sitio objetivo: {target_domain}")
    print(f"   Tema: {base_topic}")
    print(f"   Número de búsquedas: {num_searches}")
    print(f"   Mercado objetivo: México y España\n")
    
    results = run_seo_task(
        brand_name=brand_name,
        target_domain=target_domain, 
        base_topic=base_topic,
        num_searches=num_searches,
        settings=settings
    )
    
    print(f"\n✅ Resultados:")
    print(f"   Tasa de éxito: {results['success_rate']:.1%}")
    print(f"   Búsquedas exitosas: {results['successful']}/{results['total_searches']}")
    
    # Display individual results
    print(f"\n📊 Detalle de búsquedas:")
    for result in results['results']:
        status = "✓" if result['success'] else "✗"
        print(f"   {status} Búsqueda {result['search_num']}: {result['query']}")
        if 'error' in result:
            print(f"      Error: {result['error']}")


if __name__ == "__main__":
    main()