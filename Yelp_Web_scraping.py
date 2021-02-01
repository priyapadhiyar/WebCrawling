import sqlite3
import pandas as pd
from time import sleep
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException

chrome_path = r'/usr/local/bin/chromedriver' 
browser = webdriver.Chrome()
browser.maximize_window()
sleep(4)
#location = input("Enter the location here - ")
page_no = 0
#test open the first page
browser.get("https://www.yelp.com/search?cflt=restaurants&find_loc=MA&sortby=rating&l=p%3AMA%3ABoston%3A%3ADorchester&start=" + str(page_no))
sleep(2)

# --------------------------------------------------------------------------------------------------------------
# -----------------------------------------------Creating Database----------------------------------------------
# --------------------------------------------------------------------------------------------------------------
#connect to database
conn = sqlite3.connect('yelp_database.db')
conn.execute("PRAGMA foreign_keys")
cursor = conn.cursor()

#delete RESTAURANTS table if it exists
cursor.execute('DROP TABLE if exists Restaurants')
#create RESTAURANTS table
cursor.execute('CREATE TABLE Restaurants (\
                restaurant_id INT NOT NULL,\
                name varchar (200) NOT NULL,\
                rating varchar (20) NOT NULL,\
                review_count varchar (20) NOT NULL,\
                price_range varchar (100) NOT NULL,\
                category_list varchar (200),\
                PRIMARY KEY (restaurant_id));')

# delete USERS table if it exists
cursor.execute('DROP TABLE if exists Users')
#create USERS table
cursor.execute('CREATE TABLE Users (\
                user_id int NOT NULL, \
                user_name varchar (100) NOT NULL, \
                user_location varchar (15) NOT NULL, \
                count_friends varchar (30) NOT NULL, \
                count_reviews varchar (50) NOT NULL, \
                count_photos varchar (50) NOT NULL, \
                PRIMARY KEY (user_id));')
conn.commit()
 
 # delete REVIEWS table if it exists
cursor.execute('DROP TABLE if exists Reviews')
#create REVIEWS table
cursor.execute('CREATE TABLE Reviews (\
                review_id INT NOT NULL, \
                review_date varchar(15) NOT NULL, \
                review_rating varchar (15) NOT NULL, \
                review_text varchar(9000) NOT NULL, \
                photos varchar(15) NOT NULL, \
                user_id INT NOT NULL,\
                restaurant_id INT NOT NULL,\
                PRIMARY KEY (review_id),\
                FOREIGN KEY (user_id) REFERENCES Users (user_id),\
                FOREIGN KEY (restaurant_id) REFERENCES Restaurants (restaurant_id))')

conn.commit()

print('---------------------------------------------------------------------------------------------------------')
print('*********************************************************************************************************')
print('-----------Setting up Yelp database with 3 tables, Restaurants, Users and Reviews------------------------')
print('*********************************************************************************************************')
print('---------------------------------------------------------------------------------------------------------')

# --------------------------------------------------------------------------------------------------------------
# -----------------------------------------------Restaurant details----------------------------------------------
# --------------------------------------------------------------------------------------------------------------

#find the number of pages on the home page
total_pages_container = browser.find_element_by_css_selector('div.pagination__09f24__q1J0W')
#get the text - example - 1 of 16
total_pages = total_pages_container.find_element_by_css_selector('div.border-color--default__09f24__R1nRO.text-align--center__09f24__31irQ').text
#get the number of pages - 16
total_pages = int(total_pages.split(' ')[2])
print(f'Total Pages to scrape: {total_pages}')
print('---------------------------------------------------------------------------------------------------------')
#initiate blank list for restaurant details
list_of_restaurants = []

#each page has 10 restaurants - hence, loop to iterate through each page
while page_no < total_pages*10:
    #open the next listing page
    browser.get("https://www.yelp.com/search?cflt=restaurants&find_loc=MA&sortby=rating&l=p%3AMA%3ABoston%3A%3ADorchester&start=" + str(page_no))
    sleep(3)
    #get the main attributes for all 10 listings
    main = browser.find_elements_by_css_selector('div.mainAttributes__09f24__26-vh.arrange-unit__09f24__1gZC1.arrange-unit-fill__09f24__O6JFU.border-color--default__09f24__R1nRO')
    #secondary = browser.find_elements_by_css_selector('div.secondaryAttributes__09f24__3db5x.arrange-unit__09f24__1gZC1.border-color--default__09f24__R1nRO')
    for attr in main:
        name_container = attr.find_element_by_css_selector('h4')
        name_tag = name_container.find_element_by_css_selector('a.link__09f24__1kwXV.link-color--inherit__09f24__3PYlA.link-size--inherit__09f24__2Uj95')
        name = name_tag.text
        print(f'Restaurant_name : {name}')
        
        url = name_tag.get_attribute('href')
        if len(url) > 300:
            ad_flag = 1
        else:
            ad_flag = 0

        #try except clauses used to catch error, in case that element (stars/number of review/price range) is not present for a particular listing
        try:
            stars = attr.find_element_by_css_selector('div.i-stars__09f24__1T6rz.border-color--default__09f24__R1nRO.overflow--hidden__09f24__3u-sw').get_attribute('aria-label')
            stars = stars.split()[0]
            print(f'Restaurant_rating : {stars}')
        except:
            stars = 'No rating'
            print(f'Restaurant_rating : {stars}')
        try:
            num_reviews = attr.find_element_by_css_selector('span.text__09f24__2tZKC.reviewCount__09f24__EUXPN.text-color--black-extra-light__09f24__38DtK.text-align--left__09f24__3Drs0').text
            print(f'Restaurant_total_reviews : {num_reviews}')
        except:
            num_reviews = 0
            print(f'Restaurant_total_reviews : {num_reviews}')

        try:
            price_range = attr.find_element_by_css_selector('span.text__09f24__2tZKC.priceRange__09f24__2O6le.text-color--black-extra-light__09f24__38DtK.text-align--left__09f24__3Drs0.text-bullet--after__09f24__1MWoX').text
            print(f'Restaurant_price_range : {price_range}')
        except:
            price_range  = 'NA'
            print(f'Restaurant_price_range : {price_range}')

        try:
            category_list = []
            category = attr.find_elements_by_css_selector('span.text__09f24__2tZKC.text-color--black-extra-light__09f24__38DtK.text-align--left__09f24__3Drs0.text-size--inherit__09f24__2rwpp')
            for element in category:
                element = element.text
                category_list.append(element)
            category_list = ' '.join(category_list)
            print(f'Restaurant_category : {category_list}') 
        except:
            category_list  = 'NA'
            print(f'Restaurant_category : {category_list}') 
        
        print('---------------------------------------------------------------------------------------------------------')

        list_of_restaurants.append([name, url, ad_flag, stars, num_reviews, price_range,category_list])
    #increment the page number by 10 (10 listings per page)
    page_no += 10

#remove list of restaurants with ad_flag = 1 (sponsered results)and keep the ones with 0
list_of_restaurants = [restaurant for restaurant in list_of_restaurants if restaurant[2] == 0]

#define the column names for list and transfer it to pandas dataframe
cols = ['name', 'url', 'ad_flag', 'stars', 'num_reviews', 'price_range','category_list']
restaurants = pd.DataFrame(list_of_restaurants, columns = cols)
restaurants = restaurants[['name','stars','num_reviews','price_range','category_list']]
#transfer the dataframe to sqlite table Restaurants
restaurants.to_sql('Restaurants', conn, if_exists='replace', index = True, index_label='restaurant_id')
conn.commit()

# --------------------------------------------------------------------------------------------------------------
# -----------------------------------------------Reviews and User details----------------------------------------------
# --------------------------------------------------------------------------------------------------------------

#initiate blank list for review details
sleep(1)
user_id = 0
review_id = 0

#cycle through each restaurant for reviews using url captured in above list
for restaurant in list_of_restaurants:
    if(int(restaurant[4])) > 0:
        #open restaurant landing page - that's where reviews are - 20 reviews per page
        browser.get(restaurant[1])
        sleep(5)
        
        cursor.execute("SELECT restaurant_id FROM Restaurants where name='"+restaurant[0]+"'")
        restaurant_id = cursor.fetchone()[0]
        #not_reco = int(browser.find_element_by_partial_link_text('not currently recommended').text.split(' ')[0])
        
        #get review container on the page to get the number of pages of reviews for the restaurant
        total_review_pages_container = browser.find_element_by_css_selector('div.lemon--div__373c0__1mboc.pagination__373c0__3z4d_.border--top__373c0__3gXLy.border--bottom__373c0__3qNtD.border-color--default__373c0__3-ifU')
        #get pagination text - 1 of 4
        total_review_pages = total_review_pages_container.find_element_by_css_selector('div.lemon--div__373c0__1mboc.border-color--default__373c0__3-ifU.text-align--center__373c0__2n2yQ').text
        #split the number of pages - 4
        total_review_pages = int(total_review_pages.split(' ')[2])
        print(f'Total number of review pages for restaurant {restaurant[0]} : {total_review_pages}')
        #initiate the review page count to cycle through all review pages
        review_page = 0

        #cycle through all the review pages for the restaurant - each page has 20 reviews
        while review_page < total_review_pages:
            #As each page has 20 reviews, multiplying 20 with page number will give starting of next page - 0, 20, 40 and so on...
            browser.get(restaurant[1] + '?start=' + str(review_page*20))
            sleep(7)

            #get all 20 review boxes - divided into two parts -  left (user info) and right (reviews)
            review_containers = browser.find_elements_by_css_selector('li.lemon--li__373c0__1r9wz.margin-b5__373c0__2ErL8.border-color--default__373c0__3-ifU')

            if len(review_containers) == 21 or len(review_containers) == (int(restaurant[4]) % 20) + 1:
                review_containers.pop(0)

            #cycle through all 20 reviews in this loop
            
            for review_container in review_containers:
                #userid is left side box containing user info - used to fetch name, location and stats
                try:
                    userid = review_container.find_element_by_css_selector('div.lemon--div__373c0__1mboc.user-passport-info.border-color--default__373c0__3-ifU')
                    name = userid.find_element_by_tag_name('a').text.replace("'", "")
                    print(f'Review user_name: {name}')
                    profile_link = userid.find_element_by_tag_name('a').get_attribute('href')
                except NoSuchElementException:
                    print('-----------No Element found-------------------')
                
                try:
                    divs = userid.find_elements_by_tag_name('div')
                    if len(divs) > 1:
                        loc = divs[2].text.replace("'", "")
                        elite_flag = userid.find_element_by_partial_link_text('Elite').text
                        print(f'Review user location: {loc}')
                    else:
                        loc = divs[0].text.replace("'", "")
                        elite_flag = 'regular'
                        print(f'Review user location: {loc}')
                except:
                    loc = 'not_available'
                    elite_flag = 'regular'
                    print(f'Review user location: {loc}')
                
                try:
                    userstats = review_container.find_element_by_css_selector('div.lemon--div__373c0__1mboc.user-passport-stats__373c0__2LjLz.border-color--default__373c0__3-ifU')
                    userstats = userstats.text
                    userdetails = userstats.split("\n")
#                     print(len(userdetails))
                    if len(userdetails) >2:
                        friends = userdetails[0]
                        print(f'Review user friend count: {friends}')
                        count_reviews = userdetails[1]
                        print(f'Review user total review count: {count_reviews}')
                        count_photos = userdetails[2]
                        print(f'Review user photo count: {count_photos}')

                    elif len(userdetails)==2:
                        friends = userdetails[0]
                        print(f'Review user friend count: {friends}')
                        count_reviews = userdetails[1]
                        print(f'Review user total review count: {count_reviews}')
                        count_photos = 0
                        print(f'Review user photo count: {count_photos}')

                except:
                    friends = 0
                    print(f'Review user friend count: {friends}')
                    count_reviews = 0
                    print(f'Review user total review count: {count_reviews}')
                    count_photos = 0
                    print(f'Review user photo count: {count_photos}')

                #as this element text 'photos' is unique to this element in each review - number of images are extracted directly
                try:
                    images = int(review_container.find_element_by_partial_link_text('photos').text.split(' ')[0])
                    print(f'Review - user review photo count: {images}')
                except:
                    images = 0
                    print(f'Review - user review photo count: {images}')

                # --------------insert value of users into database and also retrieve user id from the table to avoid duplicates
                cursor.execute("SELECT user_id FROM Users where user_name='"+name+"' and user_location = '"+loc+"' and count_friends='"+str(friends)+"' and count_reviews='"+str(count_reviews)+"' and count_photos='"+str(count_photos)+"'")
                userID = cursor.fetchone()
                print(f'User Id: {user_id}')
                if userID:
                    user_id_generated=userID[0]
                else:
                    cursor.execute('INSERT INTO Users VALUES ("'+str(user_id)+'","'+name+'","'+loc+'","'+str(friends)+'","'+str(count_reviews)+'","'+str(count_photos)+'")')
                    conn.commit()
                    user_id += 1
                    user_id_generated = user_id
                    
                #fetch the review rating, date, count and text of review

                #to check if there are more than 1 reviews within one user
                rev_check = review_container.find_elements_by_css_selector('p.lemon--p__373c0__3Qnnj.text__373c0__2Kxyz.comment__373c0__1M-px.text-color--normal__373c0__3xep9.text-align--left__373c0__2XGa-')
                count_rev = len(rev_check)

                all_buttons = review_container.find_elements_by_tag_name('button')

                if count_rev > 0:
                    contents = review_container.find_elements_by_css_selector('div.lemon--div__373c0__1mboc.margin-t1__373c0__oLmO6.margin-b1-5__373c0__2Wblx.border-color--default__373c0__3-ifU')

                    all_reviews = review_container.find_elements_by_css_selector('span.lemon--span__373c0__3997G.raw__373c0__3rcx7')

                    for i in range(0,count_rev):
                        review_rating = contents[i].find_element_by_css_selector('div.lemon--div__373c0__1mboc.i-stars__373c0__1T6rz.border-color--default__373c0__3-ifU.overflow--hidden__373c0__2y4YK').get_attribute('aria-label')
                        print(f'Review - user rating: {review_rating}')
                        
                        review_date = contents[i].text.split('\n')[0].replace('Previous review','')
                        print(f'Review - user review date: {review_date}')
                        
                        review_text = all_reviews[i].text.replace('"', '')
                        print(f'Review - user review text: {review_text}')
                        
                        cursor.execute('INSERT INTO Reviews VALUES ("'+str(review_id)+'","'+str(review_date)+'","'+str(review_rating)+'","'+review_text+'","'+str(images)+'","'+str(user_id_generated)+'","'+str(restaurant_id)+'")')
                        conn.commit()
                        print('---------------------------------------------------------------------------------------------------------')

                        review_id += 1
                else:
                    try:
                        content = review_container.find_element_by_css_selector('div.lemon--div__373c0__1mboc.margin-t1__373c0__oLmO6.margin-b1-5__373c0__2Wblx.border-color--default__373c0__3-ifU')
                        review_rating = content.find_element_by_css_selector('div.lemon--div__373c0__1mboc.i-stars__373c0__1T6rz.border-color--default__373c0__3-ifU.overflow--hidden__373c0__2y4YK').get_attribute('aria-label')
                        print(f'Review - user rating: {review_rating}')
                    
                        review_date = content.text.split('\n')[0]
                        print(f'Review - user review date: {review_date}')
                    
                        review_text = review_container.find_element_by_css_selector('span.lemon--span__373c0__3997G.raw__373c0__3rcx7').text.replace('"', '')
                        print(f'Review - user review text: {review_text}')
                    
                        cursor.execute('INSERT INTO Reviews VALUES ("'+str(review_id)+'","'+str(review_date)+'","'+str(review_rating)+'","'+review_text+'","'+str(images)+'","'+str(user_id_generated)+'","'+str(restaurant_id)+'")')
                        conn.commit()
                    
                        print('---------------------------------------------------------------------------------------------------------')

                        review_id += 1
                    except NoSuchElementException :
                        print('--------------------------No Element Found---------------------------')

            review_page += 1
        print('---------------------------------------------------------------------------------------------------------')
        print('*********************************************************************************************************')
        print('Reviews for ' + restaurant[0] + ' is done.')
        print('*********************************************************************************************************')
        print('---------------------------------------------------------------------------------------------------------')


conn.close()
print("-----Web Scraping Completed---------")
