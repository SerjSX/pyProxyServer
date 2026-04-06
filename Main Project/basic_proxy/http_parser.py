def parse_http_request(request):
    try:
        #put each line from the request as an element of a list
        lines = request.split("\r\n")
        #set the main request info into a variable (ex: GET {URL} HTTP/1.1)
        request_line = lines[0]

        #extract from the request line each individual part into a separate variable
        method, url, _ = request_line.split()

        #we're gonna handle only GET requests for now
        if method != "GET":
            return None

        headers = {}

        for line in lines[1:]:
            #if line (other than request line) contains ": "
            #something like 'Host: localhost:10000'
            if ": " in line:
                #split them into key and value pairs
                key, value = line.split(": ", 1)
                #add to dictionary
                headers[key] = value

        if "http://" in url:
            #just keep host name and path
            url = url.replace("http://", "")

        #only split once to get host name and path name separately
        parts = url.split("/", 1)
        host = parts[0]
        #keep path empty if no path
        path = "/" + parts[1] if len(parts) > 1 else "/"

        #default port for HTTP
        port = 80

        #this is to get port if available in URL
        if ":" in host:
            host, port = host.split(":")
            port = int(port)

        return method, host, port, path, headers

    except:
        return None
