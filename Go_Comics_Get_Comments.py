import os
import csv
import json
import requests
from bs4 import BeautifulSoup

def get_comments(comic_name, comic_url, output_dir):
    try:
        response = requests.get(comic_url)
        soup = BeautifulSoup(response.content, 'html.parser')
        comment_bodies = soup.find_all("div", class_="comment-body")
        reply_bodies = soup.find_all("div", class_="media-body ml-3")
        
        if not comment_bodies:
            print(f"No comments found for {comic_name}.")
            return
        if not reply_bodies:
            print(f"No Replies found for {comment_body}.")
            return

        comic_dir = output_dir
        os.makedirs(comic_dir, exist_ok=True)
        
        csv_file = os.path.join(comic_dir, f"{comic_name}_comments.csv")
        with open(csv_file, mode='w', newline='', encoding='utf-8') as csvfile:
            csv_writer = csv.writer(csvfile)
            csv_writer.writerow(['Comment'])
            csv_writer.writerow(['Replies'])
            for comment_body in comment_bodies:
                comment_text_elem = comment_body.find("p")
                if comment_text_elem:
                    comment_text = comment_text_elem.get_text(strip=True)
                    csv_writer.writerow([comment_text])
            for reply_bodie in reply_bodies:
                reply_text_elem = reply_bodie.find('p')
                if reply_text_elem:
                    reply_text = reply_text_elem.get_text(strip=True)
                    csv_writer.writerow([reply_text])
        
        json_file = os.path.join(comic_dir, f"{comic_name}_comments.json")
        with open(json_file, mode='w', encoding='utf-8') as jsonfile:
            comments = []
            for comment_body in comment_bodies:
                comment_text_elem = comment_body.find("p")
                if comment_text_elem:
                    comment_text = comment_text_elem.get_text(strip=True)
                    comments.append(comment_text)
            json.dump(comments, jsonfile, ensure_ascii=False, indent=4)
    except Exception as e:
        print(f"Error: {e}")

def get_comic_comments(comic_name, comic_url, output_dir, page_number):
    try:
        base_url = "https://www.gocomics.com"
        full_comic_url = f"{base_url}{comic_url}?comments=visible#comments"
        print(f"Scraping comments for {comic_name}")
        get_comments(comic_name, full_comic_url, output_dir)
    except Exception as e:
        print(f"Error: {e}")

def scrape_comics(category, output_dir):
    page_num = 1
    base_url = ""
    if category == "Trending":
        base_url = "https://www.gocomics.com/comics/trending"
    elif category == "Political":
        base_url = "https://www.gocomics.com/comics/political"
    elif category == "Web Comics":
        base_url = "https://www.gocomics.com/comics/web-comics"
    elif category == "Popular":
        base_url = "https://www.gocomics.com/comics/popular"
    elif category == "A-to-Z":
        base_url = "https://www.gocomics.com/comics/a-to-z"
    else:
        print("Invalid category.")
        return
    
    category_dir = os.path.join(output_dir, category)
    os.makedirs(category_dir, exist_ok=True)
    
    while True:
        page_url = f"{base_url}?page={page_num}"
        print(f"Scraping page {page_num} for {category}: {page_url}")
        try:
            response = requests.get(page_url)
            soup = BeautifulSoup(response.content, 'html.parser')
            comic_links = soup.find_all("a", class_="gc-blended-link")
            if not comic_links:
                break
            for link in comic_links:
                comic_name = link.get_text(strip=True)
                comic_url = link['href']
                comic_output_dir = os.path.join(category_dir, str(page_num), comic_name)
                get_comic_comments(comic_name, comic_url, comic_output_dir, page_num)
            next_button = soup.find("a", class_="btn btn-primary gc-button", string="Next ›")
            if not next_button:
                break
            page_num += 1
        except Exception as e:
            print(f"Error: {e}")
            break

output_dir = "data"

while True:
    print("\nMenu:")
    print("1. Trending")
    print("2. Political")
    print("3. Web Comics")
    print("4. Popular")
    print("5. A-to-Z")
    print("q. Quit")
    
    choice = input("Enter your choice: ")
    
    if choice == "1":
        scrape_comics("Trending", output_dir)
    elif choice == "2":
        scrape_comics("Political", output_dir)
    elif choice == "3":
        scrape_comics("Web Comics", output_dir)
    elif choice == "4":
        scrape_comics("Popular", output_dir)
    elif choice == "5":
        scrape_comics("A-to-Z", output_dir)
    elif choice.lower() == "q":
        print("Exiting program.")
        break
    else:
        print("Invalid choice. Please try again.")
