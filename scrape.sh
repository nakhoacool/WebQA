GDPATH=../drive/MyDrive/uni/graduate/crawl/TDTdata/
echo "Helloworld" > $GDPATH/hello.txt
scrapy runspider core/EduCrawl/EduCrawl/spiders/tdt.py -O $GDPATH/tdt_records.jsonl