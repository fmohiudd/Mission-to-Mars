# Import Splinter and BeautifulSoup
from splinter import Browser
from bs4 import BeautifulSoup as soup
from webdriver_manager.chrome import ChromeDriverManager
import pandas as pd
import datetime as dt
# Added this import to pause the program
import time

# Initialize the browser, create a data dictionary and End the WebDriver
#  & return the scraped data
def scrape_all():
    #Initiate headless driver for deployment
    # Set the executable path and set up the URL for scrapping
    # Set up Splinter
    executable_path = {'executable_path': ChromeDriverManager().install()}
    browser = Browser('chrome', **executable_path, headless=True)

    news_title, news_paragraph = mars_news(browser)

    # Run all scraping functions and store results in a dictionary
    data = {
        "news_title": news_title,
        "news_paragraph": news_paragraph,
        "featured_image": featured_image(browser),
        "facts": mars_facts(),
        "last_modified": dt.datetime.now(),
        # This is from Deliverable 1 modified for Del 2
        "mars_image": mars_image(browser)
    }

    # Stop webdriver and return data
    ### End the automated browsing session to release the scraping
    browser.quit()
    return data

def mars_news(browser):

    # Scrape the Mars NASA news
    # Visit the mars nasa news site
    url = 'https://redplanetscience.com/'
    browser.visit(url)

    #Optional delay for loading the page
    browser.is_element_present_by_css('div.list_text', wait_time=1)

    # Convert the browser html to a soup object and then quit the browser
    html = browser.html
    news_soup = soup(html, 'html.parser')

    # Add try/except for error handling
    try:
        slide_elem = news_soup.select_one('div.list_text')
        #slide_elem.find('div', class_='content_title')
        # Use the parent element to find the first 'a' tag and save it as 'news_title'
        news_title = slide_elem.find('div', class_='content_title').get_text()
        # Use the parent element to find the paragraph text
        news_p = slide_elem.find('div', class_='article_teaser_body').get_text()

    except AttributeError:
        return None, None

    return news_title, news_p

# ------------------------
### JPL Space Featured Images

def featured_image(browser):

    # Visit URL (Jet Propulsion Lab for images)
    url = 'https://spaceimages-mars.com'
    browser.visit(url)

    ## Locate the button for the full image
    # Find and click the full image button
    full_image_elem = browser.find_by_tag('button')[1]
    full_image_elem.click()

    # Parse the resulting html with soup
    html = browser.html
    img_soup = soup(html, 'html.parser')

    # Add try/except for error handling
    try:
        # Find the relative image.url
        img_url_rel = img_soup.find('img', class_='fancybox-image').get('src')

    except AttributeError:
        return None

    # Use the base URL to create an absolute URL
    img_url = f'http://spaceimages-mars.com/{img_url_rel}'

    return img_url

### Mars Facts
##### Convert the html table to pandas dataframe

def mars_facts():
    # Add try/except for error handling
    try:
         # use 'read_html" to scrape the facts table into a dataframe
        df = pd.read_html('http://galaxyfacts-mars.com')[0]

    except BaseException:
        return None

    # Assign columns and set indext of dataframe
    df.columns=['Description', 'Mars', 'Earth']
    df.set_index('Description', inplace = True)

    ### Convert dataframe into HTML format, add bootstrap
    return df.to_html()

# ----------------------------------------
### For Deliverable 2
def mars_image(browser):
    ### Hemispheres
    # Use browser to visit the URL 
    url = 'https://marshemispheres.com/'
    browser.visit(url)

    # Parse the resulting html with soup
    html = browser.html
    img_soup = soup(html, 'html.parser')
    # 2. Create a list to hold the images and titles.
    hemisphere_image_urls = []

    # 3. Write code to retrieve the image urls and titles for each hemisphere.
    for i in range(4):   
        hemispheres = {}
        # titles = {}
        # Find the link to click to get to the web page 
        # with high resolution images
        browser.find_by_tag('h3')[i].click()

        # Parse this new webpage
        html = browser.html
        img_souped = soup(html,'html.parser')
        # The web page that has the high resolution image
        all_refs = img_souped.find('a', href = True, text='Sample')
        images = all_refs.get('href')
        # Extract the high resolution image link
        hemispheres['img_url'] = f'{url}{images}'
        # Go back to the original page
        browser.back()
        # Extract the title of the web page
        hemispheres['title'] = browser.find_by_css('a.itemLink h3')[i].text

        # Add this image and title information in the list. Start again
        hemisphere_image_urls.append(hemispheres)
        # print(hemisphere_image_urls)
        # # time.sleep(10)    
    return hemisphere_image_urls

     # END Deliverable 2 entries----------------------------------------

# Let Flask know that the script is complete
if __name__ == "__main__":
    #If running as a script, print scraped data
    print(scrape_all())
