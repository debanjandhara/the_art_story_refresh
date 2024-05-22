What you need to change before making it Deployment ready after development

1) Index.html --> Socket link
2) app.py --> socket ssl path
3) merge vector --> folder count (not needed anymore)
4) website filter --> critic only

-----
For Deployment Use Code :
gunicorn --workers 3 --bind 0.0.0.0:8000 app:app

-----

task left --> delete all files and filtereing them again, this time with proper name at coloumn 5 
upload and delete function of google drive

chatbot section :
download function of google cloud,
use sessionID, to , and request ticket to process queries, and output them... pinecone coode check
