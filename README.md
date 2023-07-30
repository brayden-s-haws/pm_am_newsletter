## Description
Product management is a field that is with long-form and strategic content. But when I went looking for real-time news through the lens of product management, I couldn't find anything. It looked like this could be an area of opportunity for someone to fill a need. There was a second problem, I wanted to be a consumer of this material, not a creator. So I decided to see if AI could use crowd-sourced content to create a newsletter that I would want to read every day. This experiment with AI has become [The PM A.M. Newsletter](https://pmnews.today). Each day this code delivers an email to my inbox with the latest news that product managers should care about.
![PM AM Newsletter](https://github.com/brayden-s-haws/pm_am_newsletter/assets/58832489/7e099a89-0ff5-4986-aad8-1f235e3f76df)

While I have fine-tuned it to deliver product management content, the prompts and sources could easily be tweaked to cover any topic or domain. Hopefully others take this code and create newsletters about whatever matters most to them.

## How It Works
The newsletter is built by grabbing content from various sources, filtering it and summarizing it with GPT, and then ultimately sending to subscribers using SendGrid. This diagram shows the various content flows in detail:
![CleanShot Freeform-2023-07-30](https://github.com/brayden-s-haws/pm_am_newsletter/assets/58832489/13f4a133-34af-4f94-80ba-ebde0f02977b)

## Features
This describes some of the key features of how the code works to ultimately generate an email.

- **GPT Filtering**: .
- **GPT Deduping**: .
- **GPT Summaries**: .
- **Email Inbox Scraping**: .
- **Scraping (API and Web-based)**: .

## Files
This describes the role of each file in creating the newsletter.
- **email_generator**: .

## Setup
I deployed this on a GCP server. But it could be deployed on almost any machine running python and flask. I wrote it all in plain python but switched to Flask for creating endpoints for testing and the recurring run. This ended up using more packages than imagined at the outset, they can be installed using this command:
  <pre><code>pip install flask openai pytz google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client bs4 newspaper sendgrid </code></pre>

## Roadmap
- Generalize all scrapers into a single class to make adding new sources easier
- Add longform content to daily sends (waiting to see if this content makes sense/is in demand)

## Acknowledgements/Thanks
- Ryan
- Kasey
- Todd

## License

This project is open source and available under the [MIT License](LICENSE).
