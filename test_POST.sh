echo "Type in your question"
read QUES
echo -e `curl -d "question=$QUES" http://127.0.0.1:5000/qa`
