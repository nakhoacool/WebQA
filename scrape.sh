GDPATH=../drive/MyDrive/uni/graduate/crawl/TDTdata/
echo "Helloworld" > $GDPATH/hello.txt
rm $GDPATH/data/*
rm $GDPATH/tdt_records.jsonl
echo "REMOVE"
scrapy runspider core/EduCrawl/EduCrawl/spiders/tdt.py -O $GDPATH/tdt_records.jsonl