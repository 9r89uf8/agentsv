# SEO Enhancement Usage Guide

## 🚀 Quick Start

The SEO enhancements have been successfully implemented! This guide will help you use the new features.

## 📋 Features Added

1. **Dwell Time Enhancement** - Stays on target pages for 2-3 minutes with natural behaviors
2. **Brand Search Mixing** - 30% brand searches, 70% discovery searches
3. **Human-like Behaviors** - Random delays, natural scrolling, pause patterns
4. **Internal Engagement** - Clicks 1-2 internal links per visit

## 🔧 Configuration

### 1. Update your `.env` file

Add these SEO settings to your `.env` file:

```bash
# SEO Enhancement Settings
BRAND_NAME=Your Brand Name
BASE_TOPIC=your product category
TARGET_DOMAIN=yoursite.com
MIN_DWELL_TIME=120  # 2 minutes minimum
MAX_DWELL_TIME=180  # 3 minutes maximum
BRAND_SEARCH_RATIO=0.3  # 30% brand searches
SEARCHES_PER_SESSION=20  # Number of searches
```

### 2. Example Configuration

For a clothing brand:
```bash
BRAND_NAME=FashionCo
BASE_TOPIC=sustainable clothing
TARGET_DOMAIN=fashionco.com
SEARCHES_PER_SESSION=15
```

## 🎯 Running SEO-Enhanced Searches

### Option 1: Using the SEO Entry Point

```bash
python main_seo.py
```

This will:
- Load settings from `.env`
- Run multiple searches with brand/discovery mix
- Engage with pages for 2-3 minutes
- Display results summary

### Option 2: Programmatic Usage

```python
from serp_agent.runner.seo_enhanced_task import run_seo_task
from serp_agent.config.settings import Settings

# Load settings
settings = Settings.from_env()

# Run SEO task
results = run_seo_task(
    brand_name="Your Brand",
    target_domain="yoursite.com",
    base_topic="your product",
    num_searches=20,
    settings=settings
)

print(f"Success rate: {results['success_rate']:.1%}")
```

### Option 3: Custom Integration

```python
from serp_agent.behaviors.simple_engagement import engage_with_page
from serp_agent.strategies.simple_search import SimpleSearchStrategy

# Create search strategy
strategy = SimpleSearchStrategy("Brand Name", "domain.com")

# Generate varied queries
for i in range(10):
    query = strategy.get_search_query("product category")
    print(f"Query {i+1}: {query}")

# After clicking a result, engage with the page
engage_with_page(driver, min_time=120, max_time=180)
```

## 📊 What Happens During SEO Searches

1. **Query Generation**
   - 30% searches use brand name directly
   - 70% use discovery terms (best, reviews, comparison)

2. **Search Execution**
   - Performs search on Google/Bing
   - Finds and clicks target domain
   - Waits 10-60 seconds between searches

3. **Page Engagement**
   - Stays on page 2-3 minutes
   - Scrolls naturally through content
   - 20% chance of extended pause (interesting content)
   - Clicks 1-2 internal links
   - 30% chance to scroll back up

## 🎛️ Tuning Parameters

### Dwell Time
- `MIN_DWELL_TIME`: Minimum seconds on page (default: 120)
- `MAX_DWELL_TIME`: Maximum seconds on page (default: 180)

### Search Mix
- `BRAND_SEARCH_RATIO`: Percentage of brand searches (default: 0.3)
- Lower = more discovery searches
- Higher = more direct brand searches

### Session Size
- `SEARCHES_PER_SESSION`: Searches per run (default: 20)
- Start small (5-10) for testing
- Scale up gradually

## 📈 Expected Results

With SEO enhancements enabled:
- **Dwell Time**: 2-3 minutes vs typical 5-10 seconds
- **Bounce Rate**: Lower due to internal link clicks
- **Search Diversity**: Natural mix of brand/discovery
- **Human Pattern**: Realistic browsing behavior

## 🔍 Monitoring

Check the console output for:
- Search type (brand vs discovery)
- Engagement duration
- Internal links clicked
- Success rate

## ⚠️ Best Practices

1. **Start Small**: Test with 5-10 searches first
2. **Use Proxies**: Enable proxy for better results
3. **Vary Timing**: Run at different times of day
4. **Monitor Results**: Track success rates
5. **Adjust Settings**: Fine-tune based on results

## 🐛 Troubleshooting

### No SEO features active
- Ensure `BRAND_NAME` is set in `.env`
- Check that settings are loading correctly

### Low success rate
- Increase `MAX_PAGES` for deeper searching
- Check if target domain appears in results
- Verify proxy is working

### Too fast/slow
- Adjust `MIN_DWELL_TIME` and `MAX_DWELL_TIME`
- Modify delay between searches in code

## 📝 Example Run Output

```
🚀 Starting SEO-enhanced searches
   Brand: FashionCo
   Target: fashionco.com
   Topic: sustainable clothing
   Searches: 20

Brand search #1: FashionCo website
Successfully clicked on fashionco.com
Starting page engagement for 145 seconds
Extended pause - interesting content
Clicking internal link: Read more about our sustainability
Page engagement completed after 145.2 seconds

Discovery search #2: best sustainable clothing
Successfully clicked on fashionco.com
Starting page engagement for 168 seconds
...

✅ Results:
   Success rate: 85.0%
   Successful searches: 17/20
```

## 🔄 Reverting to Standard Mode

To use the original SERP Agent without SEO features:
1. Comment out or remove SEO settings from `.env`
2. Use `python main.py` instead of `main_seo.py`
3. Or use the original `run_task()` function

The SEO enhancements are fully backward compatible!