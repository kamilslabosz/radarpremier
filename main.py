from email.mime.text import MIMEText
import csv
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import smtplib

FILMWEB_URL = "https://www.filmweb.pl"

my_email = ""
password = ""
recipient_email = ""

today = datetime.now()
month = today.month
year = today.year

response = requests.get(url=f"{FILMWEB_URL}/premiere/{year}/{month}")

soup = BeautifulSoup(response.text, "html.parser")

days = soup.find_all(name="time", class_="formatDate")

# creating list of days on which movies premiere
days_list = [day.get('title').replace(f'{year}-', '') for day in days]

# getting divs with movies info
tygodnie = soup.find_all(name="ul", class_="premieresList__boxes")
premiery = {}
strony = {}
index = 0

# making nested dictionary of movies and links where premier date is key
for item in tygodnie:

    titles_html = item.find_all('h2', class_="filmPreview__title")
    titles = [film.get_text() for film in titles_html]

    links_html = item.find_all('a', class_="filmPreview__link")
    links = [link.get('href') for link in links_html]
    week_data_dict = {
        'filmy': titles,
        'linki': links,
    }

    premiery[days_list[index]] = week_data_dict

    index += 1

email_body = ""

index = 0
for key in premiery:
    email_body += f">>>>>>>>>{key}<<<<<<<<<\n"
    for x in range(len(premiery[key]['filmy'])):
        response = requests.get(url=f"{FILMWEB_URL}{premiery[key]['linki'][x-1]}")
        temp_soup = BeautifulSoup(response.text, "html.parser")
        opis = temp_soup.find("span", class_="descriptionSection__moreText")
        email_body += f"-----------{premiery[key]['filmy'][x-1]}-----------\n"
        try:
            email_body += f"{opis.getText().replace('  Więcej...','')}\n"
        except AttributeError:
            try:
                opis = temp_soup.find("p", class_="descriptionSection__text")
                email_body += f"{opis.getText().replace('  Więcej...', '')}\n"
            except AttributeError:
                try:
                    opis = temp_soup.find("span", itemprop="description")
                    email_body += f"{opis.getText()}\n"
                except AttributeError:
                    email_body += f"Ten film nie ma jeszcze zarysu fabuły.\n"
        try:
            ocena = temp_soup.find("span", class_="filmRating__rateValue")
            email_body += f"Średnia ocen: {ocena.getText()} z"
        except AttributeError:
            email_body += "Zainteresowanie: "
        count = temp_soup.find("span", class_="filmRating__count")
        email_body += f"{count.getText()}\n".replace("oceny","ocen")
        email_body += f"{FILMWEB_URL}{premiery[key]['linki'][x-1]}\n"
        email_body += f"\n"
        index += 1

#sending email
text_type = 'plain'
with smtplib.SMTP("smtp.mail.yahoo.com", port=587) as connection:
    connection.starttls()
    connection.login(user=my_email, password=password)
    text = f'Hej!\nObczaj filmy które premierują w tym miesiącu w kinach!\n\n{email_body}'
    msg = MIMEText(text, text_type, 'utf-8')
    msg['Subject'] = f'Premiery {month}.{year}'
    msg['From'] = my_email
    msg['To'] = recipient_email
    connection.sendmail(msg['From'], msg['To'], msg.as_string())