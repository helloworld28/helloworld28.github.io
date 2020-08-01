import re
from pathlib import Path
import os

def read_categories_tags(fileName):
    postFine = open(fileName, "rb")
    postContent = postFine.read().decode("utf8")
    categories = re.search(r"categories:.*\[(.*)\]",postContent)

    for category in categories.group(1).split(","):
        create_category(category.strip())
    
    tags = re.search(r"tags:.*\[(.*)\]", postContent)
    for tag in tags.group(1).split(","):
        create_tag(tag.strip())
    postFine.close

def create_category(categroyName):
    categoryPagePath = "categories/"+ re.sub(" ", "-", categroyName).lower().strip() + ".html"
    categoryPageFile = Path(categoryPagePath)
    if not categoryPageFile.exists():
        f = open(categoryPagePath, "x", encoding="utf-8")
        f.write("---\n")
        f.write("layout: category\n")
        f.write(("title: "+ categroyName + "\n"))
        f.write(("category: "+ categroyName +"\n"))
        f.write("---")
        f.close()
        print("the tag page["+ categroyName +"] created success!" )
    else:
        print("the category ["+ categroyName +"] already exists will skip create page step!" )

def create_tag(tagName):
    tagPagePath = "tags/"+ re.sub(" ", "-", tagName).lower().strip() + ".html"
    tagPageFile = Path(tagPagePath)
    if not tagPageFile.exists():
        f = open(tagPageFile, "x", encoding="utf-8")
        f.write("---\n")
        f.write("layout: tag\n")
        f.write(("title: " + tagName + "\n"))
        f.write(("tag: " + tagName + "\n"))
        f.write("---")
        f.close()
        print("the tag page["+ tagName +"] created success!" )
    else:
        print("the tag ["+ tagName +"] already exists will skip create page step!" )



if __name__ == "__main__":
    for fileName in os.listdir("./_posts"):
        if fileName.endswith(".md") or fileName.endswith("markdown"):
            read_categories_tags("_posts/" + fileName)