import requests

frag_list = []
TOTAL = 10
TYPE = "test" # 'test' or 'train'
LANGUAGE = "nl" # 'en' or 'nl'

# insert in file
# with open(f"{TYPE}_{LANGUAGE}.txt", "r+") as f:
#     lines = f.readlines()

#     for line in lines:
#         f.writelines("en|" + line)

# with open(f"datasets/{TYPE}_{LANGUAGE}.txt", "r", encoding="utf-8") as f:
#     data = f.readlines()
#     for i in range(len(data)):
#         length = len(data[i].split(" "))
#         if (length != 15):
#             print(i + 1, " length not 15")

# exit()

for i in range(TOTAL):
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
    frag_list.append(fragments)

with open(f"datasets/{TYPE}_{LANGUAGE}.txt", "a", encoding="utf-8") as f:
    count = 0
    for frag in frag_list:
        if (count > 500):
            break
        try:
            count += len(frag)
            print(f"Total lines: {count}")
            to_write = "\n".join([f"{f"{LANGUAGE}|" if TYPE == "train" else ""}" + line for line in frag]) + "\n"
            f.writelines(to_write)
        except Exception as e:
            print(e)
