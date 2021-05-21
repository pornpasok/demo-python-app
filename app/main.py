import os
 
# printing environment variables
print(os.environ)

MYHOME=os.environ.get('HOME')
print(MYHOME)

ELK_ENPOINT=str(os.environ.get('ELK_ENDPOINT',"aa"))
ISHOP_CONNECTOR=str(os.environ.get('ISHOP_CONNECTOR'))
PASSWORD=str(os.environ.get('PASSWORD'))
USERNAME=str(os.environ.get('USERNAME'))

print("ELK_ENDPOINT: "+ELK_ENPOINT)
print("ISHOP_CONNECTOR: "+ISHOP_CONNECTOR)
print("PASSWORD: "+PASSWORD)
print("USERNAME: "+USERNAME)


from flask import Flask
app = Flask(__name__)

@app.route("/")
def hello():
    #return "Hello from Python!"
    return("ELK_ENDPOINT: "+ELK_ENPOINT+"<br>"+
        "ISHOP_CONNECTOR: "+ISHOP_CONNECTOR+"<br>"+
        "PASSWORD: "+PASSWORD+"<br>"+
        "USERNAME: "+USERNAME
    )

    

if __name__ == "__main__":
    app.run(host='0.0.0.0')
