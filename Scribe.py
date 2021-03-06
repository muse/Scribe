#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright © 2014 mvdw
#
# Distributed under terms of the MIT license.

# This will be used for password storage.
import ConfigParser, random

# Getopt is used to handle options given to the script which are required to make this script functional. 
# It handles the search terms, verification and a few other things.
# Sys is the module used by 'Getopt' to handle the arguments given to the script. We only use sys.argv/sys.exit() most likely.
# Math is here for flooring float numbers. (//)
import getopt, sys, math, re

# ELY or ElementTree is a XML parser. We need this because MAL API returns XML objects. 
# This simply formats them to recursive lists which can be called as object or content.
import xml.etree.ElementTree as ELY

# Costum modules required to run the following script.
# Requests is the module used to lay a connection with the API and retrieve and send data.
# It replaces libraries like urllib that are more difficult to implement and make things uneccasery difficult.
try:
    import requests
except ImportError as e:
    print "%s.\n $ 'pip install requests'"%e;sys.exit()

# Terminaltables is a module that creates simple ASCII tables. It makes it easier to show results.
# I've added a costum class to this reducing the length from strings as terminaltables doesn't do this very well.
# @Table()
try: 
    from terminaltables import AsciiTable
except ImportError as e:
    print "%s.\n $ pip install terminaltables"%e;sys.exit()

# The main function.
def main():
    class Table(object):    
        def __init__(self, 
                     title="", 
                     heading="", 
                     string_length=32, 
                     list_length=8):

            '''
            Title and heading represent the values to be checked. Both having their own check functions.            
            'string_length' is the max length of characters in a string before we shorten it.
            'list_length' is the max amount of words allowed in a string before we shorten it.
            '''

            self.string_length = string_length
            self.list_length = list_length
            self.title  = self.Title(title)
            self.heading = self.Heading(heading)

        def Title(self, argv):

            try:
                # This will try to append an integer to a string.
                # If it is a list the append will succeed thus we return.
                argv.append(1)
                print "Don't use lists"; return
            except:
                pass

            # Is the length of the string bigger then the length. (32)
            if len(argv) >= self.string_length: 
                # Return the shortened format.
                return "%s..."%argv[:self.string_length]
            else: 
                # Return the normal format.
                return argv

        def Heading(self, argv):
            
            head = []        
            
            for string in argv:
                # If the length of string exceeds the length (16)
                if len(string) > (self.string_length/2):
                    # Append the shortened format.
                    head.append("%s-"%string[:(self.string_length/2)])
                
                else:
                    # Append the normal format.
                    head.append(string)

            # Return the list of formatted strings.
            return head
     
        def Newspace(self, argv):
            '''
            Take a list of all strings and convert them to a newspaced format.
            '''

            texts = []

            # See how many strings are given.
            for string in argv:
                words = []
                sentence = []
                text = []

                if string == None: string = 'None'

                # Replace some nasty shit myAnimeList returns.
                string = re.sub("\[\w]+|\[/\w]+|\<\w>+|\</\w>+|\<\w+? \/\>|\&\w+\;|\&\w-\w+\;", "", string)

                # Put all the words in a words array.
                words = string.split()
                
                # If the length of the string is bigger then 32. 
                # We're going to need 1 or more \n's.
                if len(words) > self.list_length:
                    
                    # How many new lines do we need to add?
                    newlines = int(math.floor(len(words)/self.list_length))
                    
                    # +1) Because we don't start with 0.
                    # +1) Because we need to loop through the excess characters also.
                    for newadd in xrange(1, newlines + 2):
                        
                        # Take portions of 32 out of the list and add a \n.
                        sentence = words[
                            ( self.list_length * (newadd - 1) ):( self.list_length * newadd )
                            ]
                           
                    
                        if len(''.join(text)) > synopsis_length:
                            text.append("%s... \n"%' '.join(sentence)); break

                        # Add the combined portion to the list
                        text.append("%s \n"%' '.join(sentence))
                                
                    # Uncomment this line to remove the last \n character shortening the table but making it less readable. 
                    # text[len(text)-1]=text[len(text)-1].replace("\n","")
                    
                    # /\[\w]+|\[/\w]+|\<\w>+|\</\w>+|\<\w+? \/\>/g                        

                    texts.append(''.join(text))
                else:
                    texts.append("%s \n"%' '.join(words))

            return texts

    class Connection(object):
            def __init__(self, url):
                # Initialze requests object.
                self.http = requests.Session()

                # The url to connect to.
                self.url = url

                # The credentials for the connection.
                self.credentials = [
                Scribe.Reader.get('credentials', 'username'),
                Scribe.Reader.get('credentials', 'password')
                ]

                # Headers to connect to MALAPI.
                self.headers = {
                        'User-Agent':'api-indiv-36634BEE58157FB1D1C1E0B5A5E0AE73',
                        }
                
                # Is the connection set?
                self.set = False;

                # The content of the connection (XML)
                self.tree = []
                
                try: 
                    self.raw = self.http.get(
                          self.url, 
                          auth=(self.credentials[0], self.credentials[1]),
                          headers=self.headers
                    )
                    self.set = True
                    self.tree = ELY.fromstring(self.raw.text)

                except Exception as e:
                    print "%s"%e;
                    self.set = False

      
    class MyAnimeList():
        def __init__(self):
            # User credential file.
            self.ini = 'pwd.ini'

            # Initialize the reader.
            self.Reader = ConfigParser.ConfigParser()
            self.Reader.read(self.ini)

        def setCredentials(self, variable, value):
            self.Reader.set('credentials', variable, value)
            
            with open(self.ini, 'w') as f: 
                self.Reader.write(f)
            

        def verify(self):                
            Verify = Connection('http://myanimelist.net/api/account/verify_credentials.xml')
            if Verify.set:
                print "The user '%s' has succefully verified. (%s)"%(Verify.tree[1].text, Verify.tree[0].text)
            else: 
                print "Are you sure you have the correct username and password?\n$ --set-password\n$ --set-username"

        def search(self, search, results,
                   xid=False,        title=True,     english=False, 
                   score=True,       xtype=False,    episodes=True,    
                   synonyms=False,   status=True,    start_date=False, 
                   end_date=False,   synopsis=False, synopsis_length=140, 
                   image=False):
            '''
            Make a tableview of the requested terms and their values.
            '''
            
            attr = [
                [0, ['Id', xid]],
                [1, ['Title', title]],
                [2, ['English', english]],
                [3, ['Synonyms', synonyms]],
                [4, ['Episodes', episodes]],
                [5, ['Score', score]],
                [6, ['Type', xtype]],
                [7, ['Status', status]],
                [8, ['Start date', start_date]],
                [9, ['End date', end_date]],
                [10,['Synopsis', synopsis]],
                [11,['Image', image]]
            ]
            
            # The values for the heading
            heading_values = []
            
            for value in attr:
                if value[1][1]: 
                    heading_values.append(value[1][0])
                
            Search = Connection('http://myanimelist.net/api/anime/search.xml?q=%s'%search)

            def appendResult(which=1):
                if which > len(Search.tree): which = len(Search.tree)
                
                for root in xrange(0, which):
                    this = []
                    for value in attr:
                        if value[1][1]:
                            this.append(Search.tree[root][value[0]].text)
                    table_data.append(table_nav.Newspace(this))

            # Add the title and the heading elements to the nav.
            table_nav = Table(title = search, heading = heading_values) 
            
            # Add the heading to the table.
            # Append this table to add a row.
            table_data = [table_nav.heading]

            appendResult(results)

            # Build the table and add the title.
            table = AsciiTable(table_data, table_nav.title)

            print table.table

        def add(self, anime):
            pass

    Scribe = MyAnimeList()

    try:
        opts, args = getopt.getopt(sys.argv[1:], 
                "w:n: ilectpyurfdg", [
                "set-password=", 
                "set-username=",
                "search=",
                "add=",
                "help", "verify"]
                )
    
    except getopt.GetoptError as err:
        # print help information and exit:
        print str(err)
        sys.exit(2)
    
    xid = False         # I 
    title = False       # L
    english = False     # E
    score = False       # C
    xtype = False       # T
    episodes=False      # P
    synonyms=False      # Y
    status=False        # U
    start_date=False    # R
    end_date=False      # F 
    synopsis=False      # D
    synopsis_length=140 # -N
    image=False         # G

    results=5           # -A

    for o, a in opts:
        # Verify set credentials for further use.
        if   o in ("--verify"):
            Scribe.verify()
        
        # Set the password of the user.
        elif o in ("--set-password"):
            Scribe.setCredentials('password', a)
            sys.exit()
        
        # Set the username of the user.
        elif o in ("--set-username"):
            Scribe.setCredentials('username', a)
            sys.exit()

        elif o in ("-i"):   xid = True
        elif o in ("-l"):   title = True
        elif o in ("-e"):   english = True
        elif o in ("-c"):   score = True
        elif o in ("-t"):   xtype = True
        elif o in ("-p"):   episodes = True
        elif o in ("-y"):   synonyms = True
        elif o in ("-u"):   status = True
        elif o in ("-r"):   start_date = True
        elif o in ("-f"):   end_date = True
        elif o in ("-d"):   synopsis = True
        elif o in ("-g"):   image = True

        elif o in ("-n"):   synopsis_length = int(a)

        elif o in ("-w"):   results = int(a)

        elif o in ("--search"):
            Scribe.search(a, results, xid, title, english, 
                    score, xtype, episodes, synonyms, status, start_date,
                    end_date, synopsis, synopsis_length, image)    

        elif o in ("--add"):
            Scribe.add()

        else:
            print 'What'
 
if __name__ == '__main__': main()


