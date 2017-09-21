from flask import Flask, Response, request
import requests
import hashlib # import library we use with our own hash function
import redis # import the redis module

# initilizes flask and sets up an application project
app = Flask(__name__)
cache = redis.StrictRedis(host='redis', port=6379, db=0)    # Set up the redis cache. We wil use docker links to make the redis hostname resolvable
salt = "UNIQUE_SALT" # defines salt value to use with our hash function.
default_name = "Joe Bloggs"

# creates a route associated with teh URL. Whenever this URL is requested, it will result in a call to the hello_world function
@app.route('/', methods=['GET', 'POST'])
def mainpage():
    """TODO: Docstring for hello_world.
    :returns: Hello Docker string

    """
    name = default_name

    # Flask routes only responds to HTTP GET requests, but our form submits a HTTP POST request so we need to add the namned argumetns methods to the route declaration and explicitly announce  that the route will handle both POST and GET
    if request.method == 'POST':
        name = request.form['name']

    salted_name = salt + name
    # Get the sha256 of our input
    name_hash = hashlib.sha256(salted_name.encode()).hexdigest()

    header = '<html><head><title>Identidock</title></head><body>'
    body = '''<form method="POST">
            Hello <input type="text" name="name" value="{0}">
            <input type="submit" value="submit">
            </form>
            <p> You look like a:
            <img src="/monster/{1}"/>
            '''.format(name, name_hash)
    footer = '</body></html>'

    return header + body + footer

@app.route('/monster/<name>')
def get_identicon(name):

    # Check if the name is already in the cache
    image = cache.get(name)
    
    # If it's not if we have a cache miss, in this case we get the identicon as usual except we also
    if image is None:
        # output some debug info
        print("Cache miss", flush=True)
        r = requests.get('http://dnmonster:8080/monster/' + name + '?size=80')
        image = r.content
        # add the image into the cache and associate it with the given name
        cache.set(name, image)
    return Response(image, mimetype='image/png')


if __name__ == '__main__':
    # Initializes the python webserver. The use of 0.0.0.0 (instead of localhost or 127.0.0.1) as host argument binds to all network interfaces which is needed to allow the container to be accessed from the host or other containers.
    app.run(debug=True, host='0.0.0.0')
