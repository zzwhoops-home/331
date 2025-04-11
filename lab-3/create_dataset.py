import requests

frag_list = []
LANGUAGE = "nl"

# insert in file
# with open(f"test_{LANGUAGE}.txt", "r+") as f:
#     lines = f.readlines()

#     for line in lines:
#         f.writelines("en|" + line)

# with open(f"test_{LANGUAGE}.txt", "r") as f:
#     data = f.readlines()
#     for i in range(len(data)):
#         length = len(data[i].split(" "))
#         if (length != 15):
#             print(i + 1, " length not 15")

# exit()

for i in range(10):
    print(i)
    # Get the random article URL
    article = requests.get(f"https://{LANGUAGE}.wikipedia.org/wiki/Special:Random")
    final_url = article.url  # Wikipedia redirects you to the real page
    # get page title
    page_title = final_url.split("/")[-1]

    # get from API
    data = requests.get(f"https://{LANGUAGE}.wikipedia.org/w/api.php?action=query&format=json&prop=extracts&explaintext=true&titles={page_title}")
    data_json = data.json()

    # get the extract of the page
    try:
        extract = list(data_json['query']['pages'].values())[0]['extract']
    except KeyError:
        print("Did not find extract, moving on")
        continue
    # get all fragments that are 15 words in length
    fragments = [" ".join(fragment.split(" ")[:15]) for fragment in extract.split("\n") if len(fragment.split(" ")) >= 15]
    print(fragments)
    frag_list.append(fragments)

with open(f"test_{LANGUAGE}.txt", "ab") as f:
    for frag in frag_list:
        try:
            to_write = "\n".join(frag) + "\n"
            for line in to_write:
                f.write(f"{LANGUAGE}|" + line)
        except Exception as e:
            print(e)
