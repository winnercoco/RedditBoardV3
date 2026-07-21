# By viewing this repository, you agree to be 18+!!

## RedditBoard V3

https://redditboardv3.streamlit.app/

### Reddit Saves and Founds - A collection of several NSFW links

### <b>Flow of Operations:</b>
1. Save a post on reddit
2. Copy its html and paste into source_html_contents.html
3. Run the batch file named [RUN]_1-html_to_master_xl.bat (you will get 1-master_reddit_links_scraped.xlsx)
4. Copy and paste the contents from the newly created file into 2-master_reddit_links_curated.xlsx. Also fill the extra contents of remaining fields
5. Copy and paste the "Done" contents from 2-master_reddit_links_curated.xlsx into 3-reddit_links.xlsx

Note: The only files that change across commits are:
- source_html_contents.html
- 1-master_reddit_links_scraped.xlsx
- 2-master_reddit_links_curated.xlsx
- 3-reddit_links.xlsx
- reddit_links.json
