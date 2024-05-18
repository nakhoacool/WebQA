echo "Type in your question"
QUES=""
read QUES
if [[ -z "$QUES" ]]; then
	QUES="tư vấn ngành CNTT"
fi
echo -e `curl -d "question=$QUES" http://127.0.0.1:5001/qa` >> rag_test.txt
cat ./rag_test.txt
