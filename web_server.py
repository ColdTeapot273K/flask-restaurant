from http.server import BaseHTTPRequestHandler, HTTPServer
import requests
import cgi
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Restaurant, MenuItem

engine = create_engine('sqlite:///restaurantmenu.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()


class webServerHandler(BaseHTTPRequestHandler):

    def do_GET(self):

        try:
            if self.path.endswith("/restaurants"):
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()

                output = ""
                output += "<html><body>"
                output += "<h1>List of restaurants:</h1>"
                output += "<p><a href='/restaurants/new' class='button'>Create new</a></p>"
                restaurants = session.query(Restaurant).all()
                for item in restaurants:
                    output += "<h2>Restaurant {}</h2>".format(item.name)
                    output += "<a href='/restaurants/{}/edit' class='button'>Edit</a>".format(item.id)
                    output += "<br></br>"
                    output += "<a href='/restaurants/{}/delete' class='button'>Delete</a>".format(item.id)
                    output += "</form>"
                output += "</body></html>"
                self.wfile.write(output.encode())
                print(output)
                return

            if self.path.endswith("/restaurants/new"):
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()

                output = ""
                output += "<html><body>"
                output += "<h1>Create a new restaurant</h1>"
                output += "<form method='POST' enctype='multipart/form-data' action='/restaurants/new'>"
                output += "<input name='newRestaurantName' type='text' placeholder='new restaurant name'>"
                output += "<input type='submit' value='Create'></form>"
                output += "</body></html>"
                self.wfile.write(output.encode())
                print(output)
                return

            if self.path.endswith("/edit"):
                restaurantIDPath = self.path.split('/')[2]

                myRestaurantQuery = session.query(Restaurant).filter_by(id=restaurantIDPath).one()
                if myRestaurantQuery:
                    self.send_response(200)
                    self.send_header('Content-type', 'text/html')
                    self.end_headers()
                    output = ""
                    output += "<html><body>"
                    output += "<h1>"
                    output += myRestaurantQuery.name
                    output += "</h1>"
                    output += "<form method='POST' enctype='multipart/form-data' " \
                              "action='/restaurants/%s/edit'>" % restaurantIDPath
                    output += "<input name='newRestaurantName' type='text'" \
                              " placeholder='%s'>" % myRestaurantQuery.name
                    output += "<input type='submit' value='Rename'></form>"
                    output += "</body></html>"
                    self.wfile.write(output.encode())
                    print(output)
                    return

            if self.path.endswith("/delete"):
                restaurantIDPath = self.path.split('/')[2]
                myRestaurantQuery = session.query(Restaurant).filter_by(id=restaurantIDPath).one()
                if myRestaurantQuery:
                    self.send_response(200)
                    self.send_header('Content-type', 'text/html')
                    self.end_headers()
                    output = ""
                    output += "<html><body>"
                    output += "<h1>Are you sure you want to delete restaurant {}?</h1>".format(myRestaurantQuery.name)
                    output += "<form method='POST' enctype='multipart/form-data' " \
                              "action='/restaurants/%s/delete'>" % restaurantIDPath
                    output += "<input type='submit' value='Delete'></form>"
                    output += "</body></html>"
                    self.wfile.write(output.encode())
                    print(output)
                    return

        except IOError:
            self.send_error(404, 'File Not Found: %s' % self.path)

    def do_POST(self):
        try:
            if self.path.endswith("/restaurants/new"):
                ctype, pdict = cgi.parse_header(
                    self.headers.get('Content-type', 0))
                pdict['boundary'] = bytes(pdict['boundary'], 'utf-8')
                content_len = int(self.headers.get('Content-length'))
                pdict['CONTENT-LENGTH'] = content_len
                if ctype == 'multipart/form-data':
                    fields = cgi.parse_multipart(self.rfile, pdict)
                    input_content = fields.get('newRestaurantName')

                newRestaurant = Restaurant(name=input_content[0].decode('utf-8'))
                session.add(newRestaurant)
                session.commit()

                self.send_response(301)
                self.send_header('Content-type', 'text/html')
                self.send_header('Location', '/restaurants')
                self.end_headers()

            if self.path.endswith("/edit"):
                ctype, pdict = cgi.parse_header(
                    self.headers.get('Content-type', 0))
                pdict['boundary'] = bytes(pdict['boundary'], 'utf-8')
                content_len = int(self.headers.get('Content-length'))
                pdict['CONTENT-LENGTH'] = content_len
                if ctype == 'multipart/form-data':
                    fields = cgi.parse_multipart(self.rfile, pdict)
                input_content = fields.get('newRestaurantName')
                restaurantIDPath = self.path.split('/')[2]
                myRestaurantQuery = session.query(Restaurant).filter_by(id=restaurantIDPath).one()

                if myRestaurantQuery:
                    myRestaurantQuery.name = input_content[0].decode('utf-8')
                    session.add(myRestaurantQuery)
                    session.commit()

                self.send_response(301)
                self.send_header('Content-type', 'text/html')
                self.send_header('Location', '/restaurants')
                self.end_headers()

            if self.path.endswith("/delete"):
                restaurantIDPath = self.path.split('/')[2]
                myRestaurantQuery = session.query(Restaurant).filter_by(id=restaurantIDPath).one()

                if myRestaurantQuery:
                    session.delete(myRestaurantQuery)
                    session.commit()

                self.send_response(301)
                self.send_header('Content-type', 'text/html')
                self.send_header('Location', '/restaurants')
                self.end_headers()
        except:
            pass


def main():
    try:
        port = 8080
        server = HTTPServer(('', port), webServerHandler)
        print("Web Server running on port %s" % port)
        server.serve_forever()
    except KeyboardInterrupt:
        print(" ^C entered, stopping web server....")
        server.socket.close()


if __name__ == '__main__':
    main()